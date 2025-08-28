import streamlit as st
import cv2
import numpy as np
import pandas as pd
from camera import ThreadedCamera
from user_management import UserManagement
from access_history import AccessHistory
import time
import asyncio
from datetime import datetime
from typing import Tuple
import faiss
# import csv
import json
import os


# Giả sử đây là module bạn dùng, nếu tên khác hãy thay đổi
import face_recognition_pybind as FR
# FR.init_neural_networks()


st.set_page_config(page_title="Face Recognition System", layout="wide")

# Session state for persistent variables
if "camera" not in st.session_state:
    st.session_state.camera = None
if "stable_start_time" not in st.session_state:
    st.session_state.stable_start_time = None
if "last_center" not in st.session_state:
    st.session_state.last_center = None
if "recognized_this_session" not in st.session_state:
    st.session_state.recognized_this_session = False

# Thêm các biến trạng thái để lưu kết quả nhận diện cuối cùng
if "last_known_box" not in st.session_state:
    st.session_state.last_known_box = None
if "last_known_text" not in st.session_state:
    st.session_state.last_known_text = ""

# Thêm counter để đếm số frame không có face
if "no_face_counter" not in st.session_state:
    st.session_state.no_face_counter = 0

if "cos_sim_thresh" not in st.session_state:
    st.session_state.cos_sim_thresh = 0.7

dims = 128  # vector dims
if "faiss_index" not in st.session_state:
    file_path = "facial_faiss_index.bin"
    if os.path.exists(file_path):
        st.session_state.faiss_index = faiss.read_index(file_path)
        print(f"faiss_index.ntotal: {st.session_state.faiss_index.ntotal}")
    else:
        st.session_state.faiss_index = faiss.index_factory(dims, "Flat", faiss.METRIC_INNER_PRODUCT)

# if "users_list" not in st.session_state:
#     st.session_state.users_list = []
#     file_path = "users.json"
#     if os.path.exists(file_path):
#         with open(file_path, 'r') as json_file:
#             st.session_state.users_list = json.load(json_file)
#             print(st.session_state.users_list)
if "user_management" not in st.session_state:
    st.session_state.user_management = UserManagement()
if "users_list" not in st.session_state:
    st.session_state.users_list = st.session_state.user_management.get_users()
    print(f"users_list: {st.session_state.users_list}")
if "access_history" not in st.session_state:
    st.session_state.access_history = AccessHistory()
    st.session_state.history = st.session_state.access_history.load_history()
if "last_log_status" not in st.session_state:
    st.session_state.last_log_status = "No recent activity"
if "last_log_time" not in st.session_state:
    st.session_state.last_log_time = ""
if "history_needs_refresh" not in st.session_state:
    st.session_state.history_needs_refresh = False
if "last_refresh_time" not in st.session_state:
    st.session_state.last_refresh_time = 0


# user_management = UserManagement()
# access_history = AccessHistory()
stable_threshold = 20  # pixels
stable_duration = 1.2  # seconds

def start_camera(cam_src):
    try:
        cam_index = int(cam_src)
        st.session_state.camera = ThreadedCamera(cam_index)
    except ValueError:
        st.session_state.camera = ThreadedCamera(cam_src)
    st.session_state.camera.start()

def stop_camera():
    if st.session_state.camera:
        st.session_state.camera.stop()
        st.session_state.camera = None

def reset_users():
    st.session_state.user_management.reset_users()
    st.session_state.users_list = st.session_state.user_management.get_users()
    st.session_state.faiss_index.reset()
    faiss.write_index(st.session_state.faiss_index, "facial_faiss_index.bin")
    # file_path = "users.json"
    # with open(file_path, 'w', newline='') as json_file:
    #     json.dump(st.session_state.users_list, json_file)
    st.success("All users have been reset.")

def calculate_cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:  # Handle zero vectors
        return 0.0
    return dot_product / (norm_vec1 * norm_vec2)

def update_history_display():
    """Update history table display - xóa bảng cũ hoàn toàn và hiển thị bảng mới"""
    try:
        # Bước 1: Xóa hoàn toàn nội dung placeholder cũ (Double check)
        history_placeholder.empty()
        
        # Bước 2: Đợi một chút để đảm bảo clear hoàn toàn
        import time
        time.sleep(0.01)
        
        # Bước 3: Xóa lần nữa để đảm bảo
        history_placeholder.empty()
        
        # Bước 4: Tạo nội dung mới hoàn toàn
        with history_placeholder.container():
            st.subheader("📊 Access History")
            
            # Hiển thị trạng thái log gần nhất
            if hasattr(st.session_state, 'last_log_status') and st.session_state.last_log_status:
                col_status1, col_status2 = st.columns([3, 1])
                with col_status1:
                    st.write(f"**Last Activity:** {st.session_state.last_log_status}")
                with col_status2:
                    if hasattr(st.session_state, 'last_log_time') and st.session_state.last_log_time:
                        st.write(f"**Time:** {st.session_state.last_log_time}")
            
            # Hiển thị bảng lịch sử mới
            history_data = get_access_history()
            if history_data:
                df = pd.DataFrame(history_data)
                st.dataframe(df, use_container_width=True)
                print(f"✅ Successfully displayed history table with {len(history_data)} entries")
            else:
                st.info("No access history available.")
                print("ℹ️ No access history data available")
                
    except Exception as e:
        print(f"❌ Error updating history display: {e}")
        # Đảm bảo xóa placeholder nếu có lỗi
        history_placeholder.empty()
        history_placeholder.error(f"Error loading access history: {e}")



def register_user(name):
    if not name:
        st.warning("Please enter a name.")
        return

    frame = st.session_state.camera.get_frame()
    # img_path = name
    # frame = cv2.imread(img_path, cv2.IMREAD_COLOR)
    if frame is not None:
        # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # frame = resize_with_pad(frame, (640, 640), padding_color=(0, 0, 0))
        frame_rgb = frame
        # Giả định hàm của bạn nhận các tham số này
        result, facial_feature = FR.register_user(frame_rgb, frame_rgb.shape[0], frame_rgb.shape[1], frame_rgb.shape[2])
        facial_feature= np.array(facial_feature, dtype='float32')
        print(f"facial_feature.ndim: {facial_feature.ndim}")
        print(f"facial_feature.shape: {facial_feature.shape}")
        # print(facial_feature)
        # file_path = "chau_reg_2.txt"
        # print(file_path)
        # register_feature = np.loadtxt(file_path, dtype="float32")
        # cosine_similarity = calculate_cosine_similarity(vec1=register_feature, vec2=facial_feature)
        # print(f"cosine_similarity = {cosine_similarity}")

        # st.session_state.users_list.append(name)
        result, err_mgs = st.session_state.user_management.register_user(name)
        print(err_mgs)
        if result:
            print(f"faiss_index.ntotal: {st.session_state.faiss_index.ntotal}")
            facial_feature = facial_feature.reshape(1, 128)
            faiss.normalize_L2(facial_feature)
            st.session_state.faiss_index.add(facial_feature)
            faiss.write_index(st.session_state.faiss_index, "facial_faiss_index.bin")

        st.session_state.users_list = st.session_state.user_management.get_users()
        print(st.session_state.users_list)
        # file_path = "users.json"
        # with open(file_path, 'w', newline='') as json_file:
        #     json.dump(st.session_state.users_list, json_file, indent=4)

        # Display the result
        st.success(err_mgs)
    else:
        st.warning("Failed to capture image for registration.")

def get_access_history():
    # Force reload from file to ensure fresh data
    st.session_state.access_history.load_history()
    
    # Kiểm tra xem có phải JSON format hay text format
    if hasattr(st.session_state.access_history, 'history_data'):
        # JSON format - lấy trực tiếp từ dictionary
        history_data = st.session_state.access_history.history_data
        
        print(f"🔍 DEBUG - JSON format: {len(history_data)} users")
        
        lines = []
        for username, timestamps in history_data.items():
            if timestamps:  # Nếu user có ít nhất 1 lần access
                last_access = timestamps[-1]  # Lấy timestamp cuối cùng
                total_count = len(timestamps)   # Đếm tổng số lần access
                
                lines.append({
                    "Name": username,
                    "Last Checkin": last_access,
                    "Total Access": total_count
                })
                print(f"  ✅ Added: {username} - Last: {last_access} - Total: {total_count}")
    else:
        # Text format - fallback cho compatibility
        history = st.session_state.access_history.get_history()
        
        print(f"🔍 DEBUG - Text format: {len(history)} entries")
        
        # Nhóm theo user để đếm
        user_data = {}
        for entry in history:
            if entry and entry.strip():
                parts = entry.strip().split('\t')
                if len(parts) == 2:
                    name, timestamp = parts
                    if name not in user_data:
                        user_data[name] = []
                    user_data[name].append(timestamp)
        
        lines = []
        for username, timestamps in user_data.items():
            if timestamps:
                # Sắp xếp timestamps và lấy cái mới nhất
                timestamps.sort(reverse=True)
                last_access = timestamps[0]
                total_count = len(timestamps)
                
                lines.append({
                    "Name": username,
                    "Last Checkin": last_access,
                    "Total Access": total_count
                })
                print(f"  ✅ Added: {username} - Last: {last_access} - Total: {total_count}")
    
    # Sắp xếp theo last checkin mới nhất trước
    lines.sort(key=lambda x: x.get("Last Checkin", ""), reverse=True)
    print(f"📊 Final display: {len(lines)} users")
    return lines

# Các hàm không sử dụng nữa có thể được xóa hoặc giữ lại nếu cần
# def process_frame(): ...
# def detect_face(tmp=0): ...

def resize_with_pad(image: np.array, 
                    new_shape: Tuple[int, int], 
                    padding_color: Tuple[int] = (255, 255, 255)) -> np.array:
    """Maintains aspect ratio and resizes with padding.
    Params:
        image: Image to be resized.
        new_shape: Expected (width, height) of new image.
        padding_color: Tuple in BGR of padding color
    Returns:
        image: Resized image with padding
    """
    original_shape = (image.shape[1], image.shape[0])
    ratio = float(max(new_shape))/max(original_shape)
    new_size = tuple([int(x*ratio) for x in original_shape])
    image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    delta_w = new_shape[0] - new_size[0]
    delta_h = new_shape[1] - new_size[1]
    top, bottom = delta_h//2, delta_h-(delta_h//2)
    left, right = delta_w//2, delta_w-(delta_w//2)
    image = cv2.copyMakeBorder(image, top, bottom, left, right, cv2.BORDER_CONSTANT, value=padding_color)
    return image

################# main #################

st.title("Check-in System")

# Tạo container cho history table để có thể update real-time
history_container = st.container()
history_placeholder = st.empty()  # Placeholder cho real-time update

col1, col2 = st.columns([2, 1])

with col2:
    cam_src = st.text_input("Camera Source", value="rtsp://adminOnvif:Vision123@10.60.3.157/Streaming/Channels/102?transportmode=unicast&profile=Profile_1")
    name = st.text_input("Name")
    
    # Face Recognition controls
    st.subheader("Face Recognition Settings")
    st.session_state.cos_sim_thresh = st.slider(
        "Similarity Threshold", 
        min_value=0.0, 
        max_value=1.0, 
        value=st.session_state.cos_sim_thresh, 
        step=0.01,
        help="Ngưỡng tương đồng: ≥threshold = Nhận diện, <threshold = Người lạ"
    )
    
    # System Status
    st.subheader("System Status")
    st.success("✅ Face Recognition: Ready")
    
    if st.button("Start Camera"):
        stop_camera()
        start_camera(cam_src)
    if st.button("Register"):
        # if st.session_state.camera:
        if st.session_state.camera is None:
            st.error("❌ Please start the camera first before registering.")
        else:
            register_user(name)
    
    if st.button("Test Face Detection"):
        if st.session_state.camera is None:
            st.error("❌ Please start the camera first.")
        else:
            frame = st.session_state.camera.get_frame()
            if frame is not None:
                frame = resize_with_pad(np.array(frame), (640, 640), padding_color=(0, 0, 0))
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                try:
                    left, top, right, bottom, spoof_confidence, facial_feature = FR.detect_face(frame_rgb, frame_rgb.shape[0], frame_rgb.shape[1], frame_rgb.shape[2])
                    
                    if left > 0 and top > 0 and right > 0 and bottom > 0:
                        st.success(f"✅ Face detected! Position: ({left}, {top}, {right}, {bottom})")
                        st.success("✅ Ready for registration!")
                    else:
                        st.warning("⚠️ No face detected in current frame")
                        st.info("💡 Try adjusting your position, lighting, or camera angle")
                        
                except Exception as e:
                    st.error(f"❌ Error during face detection test: {e}")
            else:
                st.warning("❌ No frame available from camera")
                
    if st.button("Reset Users"):
        reset_users()
    if st.button("Stop Camera"):
        stop_camera()

with col1:
    st.subheader("Camera Feed")
    frame_placeholder = st.empty()
    show_feed = st.checkbox("Show Camera Feed", value=True)

if st.session_state.camera and show_feed:
    circle = 2
    tmp = 0
    while True:
        # 1. Luôn lấy frame mới từ camera
        frame = st.session_state.camera.get_frame()
        # print(frame.shape)
        # img_path = "register_images_2/Hop.jpg"
        # frame = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if frame is None:
            frame_placeholder.warning("No frame available.")
            time.sleep(0.05)
            continue
        frame = resize_with_pad(np.array(frame), (640, 640), padding_color=(0, 0, 0))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 2. Chỉ chạy nhận diện mỗi 4 frame để tối ưu (gọi SOM)
        if tmp == 0:
            # Gọi SOM để detect face
            display_text = ""
            
            left, top, right, bottom, spoof_confidence, facial_feature = FR.detect_face(frame, frame.shape[0], frame.shape[1], frame.shape[2])
                
            print(f"🔍 SOM call #{st.session_state.no_face_counter + 1}: Face detection")
            
            # ✅ KIỂM TRA NẾU FRAME BỊ SKIP TỪ C++ (empty result)
            if left == 0 and top == 0 and right == 0 and bottom == 0:
                # Frame bị skip từ C++, không có thông tin face detection
                # Tăng counter vì đây vẫn là lần gửi xuống SOM
                st.session_state.no_face_counter += 1
                print(f"⏭️ No face detected - SOM call {st.session_state.no_face_counter}/10")
                
                # Xóa bounding box sau 10 lần liên tiếp không detect
                if st.session_state.no_face_counter >= 10:
                    st.session_state.last_known_box = None
                    st.session_state.no_face_counter =0 
                    st.session_state.last_known_text = ""
                    print(f"🗑️ Cleared bounding box after {st.session_state.no_face_counter} frames without face")
            else:
                # Frame được xử lý, tiếp tục logic bình thường
                
                # ✅ CHỈ CẬP NHẬT BOUNDING BOX KHI CÓ FACE DETECTION THÀNH CÔNG
                # Kiểm tra nếu có face được detect (left, top, right, bottom > 0)
                if left > 0 and top > 0 and right > 0 and bottom > 0:
                    st.session_state.last_known_box = (left, top, right, bottom)
                    st.session_state.no_face_counter = 0  # Reset counter khi có face
                    print(f"✅ Face detected! Reset counter to 0")
                    print(f"📦 Updated bounding box: ({left}, {top}, {right}, {bottom})")
                else:
                    # Tăng counter khi không có face
                    st.session_state.no_face_counter += 1
                    print(f"❌ No face detected - SOM call {st.session_state.no_face_counter}/10")
                    
                    # Xóa bounding box sau 10 lần liên tiếp không detect
                    if st.session_state.no_face_counter >= 10:
                        st.session_state.last_known_box = None
                        st.session_state.last_known_text = ""
                        print(f"🗑️ Cleared bounding box after {st.session_state.no_face_counter} frames without face")
                
                # Proceed with face recognition if face detected
                if left > 0 and top > 0 and right > 0 and bottom > 0 and st.session_state.faiss_index.ntotal > 0:
                    if len(facial_feature) == 128:
                        facial_feature= np.array(facial_feature, dtype='float32')
                        facial_feature = facial_feature.reshape(1, 128)
                        faiss.normalize_L2(facial_feature)
                        k = 3
                        distances, indices = st.session_state.faiss_index.search(facial_feature, k)
                        
                        # Tìm người có độ tương đồng cao nhất và >= ngưỡng
                        best_match = None
                        best_distance = -1
                        
                        # Kiểm tra an toàn trước khi xử lý kết quả search
                        if len(indices) > 0 and len(indices[0]) > 0 and len(st.session_state.users_list) > 0:
                            for i, index in enumerate(indices[0]):
                                distance = distances[0][i]
                                # Kiểm tra index hợp lệ trước khi truy cập users_list
                                if 0 <= index < len(st.session_state.users_list):
                                    print(f"Nearest neighbor {i+1}: Index: {index}, Distance: {distance:.4f}, Name: {st.session_state.users_list[index]}")
                                    
                                    # Kiểm tra nếu distance >= ngưỡng và cao hơn best match hiện tại
                                    if distance >= st.session_state.cos_sim_thresh and distance > best_distance:
                                        best_match = st.session_state.users_list[index]
                                        best_distance = distance
                                else:
                                    print(f"Nearest neighbor {i+1}: Index: {index}, Distance: {distance:.4f}, Name: [Invalid Index]")
                        else:
                            print("⚠️ No valid search results or empty user list")
                        
                        if best_match:
                            display_text = best_match
                            print(f"✅ Best match: {best_match} with distance: {best_distance:.4f}")
                        else:
                            print(f"❌ No match found above threshold {st.session_state.cos_sim_thresh}")
                            display_text = "Unknown Person"
                
                # ✅ CẬP NHẬT TEXT CHỈ KHI CÓ KẾT QUẢ MỚI
                if display_text and not display_text.startswith("⚠️"):
                    st.session_state.last_known_text = display_text
                    # Chỉ ghi lịch sử nếu nhận diện thành công (không phải Unknown Person)
                    if display_text != "Unknown Person":
                        print(f"🚪 REAL-TIME LOGGING: Attempting to log access for: {display_text}")
                        
                        # Đảm bảo access_history được khởi tạo
                        if not hasattr(st.session_state, 'access_history') or st.session_state.access_history is None:
                            print(f"🔧 Initializing AccessHistory...")
                            st.session_state.access_history = AccessHistory()
                        
                        try:
                            # Gọi log_access và nhận kết quả
                            log_result = st.session_state.access_history.log_access(display_text)
                            current_time = datetime.now().strftime("%H:%M:%S")
                            
                            # Luôn refresh bảng ngay sau mỗi lần nhận diện thành công
                            st.session_state.access_history.load_history()
                            
                            if log_result:
                                print(f"✅ REAL-TIME SUCCESS: Logged and saved to file for: {display_text}")
                                st.session_state.last_log_status = f"✅ Logged: {display_text}"
                                st.session_state.last_log_time = current_time
                            else:
                                print(f"⏭️ REAL-TIME SKIP: Not logged due to 5-minute rule for: {display_text}")
                                st.session_state.last_log_status = f"⏭️ Skipped: {display_text} (5-min rule)"
                                st.session_state.last_log_time = current_time
                            
                            # 🔄 REFRESH BẢNG NGAY LẬP TỨC sau khi nhận diện thành công
                            print(f"🔄 [REAL-TIME] Starting history table refresh for: {display_text}")
                            print(f"🗑️ [REAL-TIME] Clearing old table...")
                            
                            # Đảm bảo xóa bảng cũ trước
                            history_placeholder.empty()
                            
                            print(f"🆕 [REAL-TIME] Creating new table...")
                            update_history_display()
                            
                            print(f"✅ [REAL-TIME] History table refresh completed for: {display_text}")
                        except Exception as e:
                            print(f"❌ REAL-TIME ERROR: {e}")
                            st.session_state.last_log_status = "Error logging access"
                            st.session_state.last_log_time = ""
                            st.session_state.last_log_time = ""
        
        tmp = (tmp + 1) % 4  # Chỉ nhận diện mỗi 4 frame
        
        # 3. Hiển thị kết quả lên streamlit
        if st.session_state.last_known_box:
            left, top, right, bottom = st.session_state.last_known_box
            frame = cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Hiển thị text nhận diện được
            display_text = st.session_state.last_known_text
            if display_text and not display_text.startswith("⚠️"):
                # Hiển thị tên người nhận diện được
                frame = cv2.putText(frame, display_text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
        
        # Convert màu sắc về BGR để hiển thị đúng trên streamlit
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # Hiển thị frame lên streamlit
        frame_placeholder.image(frame, channels="BGR")
        
        # Giảm độ trễ giữa các lần hiển thị
        time.sleep(0.1)

# Hiển thị bảng lịch sử truy cập ban đầu (chỉ khi camera chưa chạy)
if not (st.session_state.camera and show_feed):
    print("📊 Displaying initial history table (camera not running)")
    update_history_display()

# Nút refresh thủ công
if st.button("🔄 Refresh History"):
    if hasattr(st.session_state, 'access_history'):
        st.session_state.access_history.load_history()
        print("🔄 Manual refresh triggered")
        history_placeholder.empty()  # Xóa bảng cũ trước
        update_history_display()
