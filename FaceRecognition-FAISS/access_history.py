import time
import json
import os
from datetime import datetime, timedelta

class AccessHistory:
    def __init__(self, login_history_file='login_history.json'):
        self.login_history_file = login_history_file
        self.history = []  # Giữ để backward compatibility
        self.history_data = {}  # JSON format: {"username": ["timestamp1", "timestamp2"]}
        self.load_history()
        print(f"🏗️ AccessHistory initialized with {len(self.history)} entries")

    def get_last_access_time(self, user_name):
        """Tìm lần truy cập gần nhất của user (ưu tiên JSON format)"""
        # Ưu tiên JSON format trước
        if user_name in self.history_data and self.history_data[user_name]:
            return self.history_data[user_name][-1]  # Lấy timestamp cuối cùng
        
        # Fallback cho text format
        last_time = None
        for entry in reversed(self.history):
            if '\t' in entry:
                parts = entry.split('\t')
                if len(parts) == 2 and parts[0] == user_name:
                    last_time = parts[1]
                    break
        return last_time

    def should_log_access(self, user_name):
        """Kiểm tra xem có nên ghi log không (dựa trên rule 5 phút)"""
        last_time_str = self.get_last_access_time(user_name)
        
        if not last_time_str:
            return True, "No previous access found"
            
        try:
            # Sử dụng datetime để tính toán chính xác hơn
            last_time = datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            now_time = datetime.now()
            time_diff = now_time - last_time
            
            minutes_diff = time_diff.total_seconds() / 60
            
            if minutes_diff >= 5:
                return True, f"Last access was {minutes_diff:.2f} minutes ago"
            else:
                return False, f"Only {minutes_diff:.2f} minutes since last access"
                
        except Exception as e:
            print(f"⚠️ Error parsing time: {e}")
            return True, "Error parsing time, allowing access"

    def log_access(self, user_name):
        """Ghi log truy cập nếu thỏa mãn điều kiện 5 phút"""
        if not user_name or user_name.strip() == "":
            print(f"⚠️ Empty username, not logging")
            return False
            
        user_name = user_name.strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"\n🔍 CHECKING ACCESS LOG")
        print(f"   User: {user_name}")
        print(f"   Current time: {timestamp}")
        
        # Kiểm tra xem có nên ghi log không
        should_log, reason = self.should_log_access(user_name)
        print(f"   Decision: {reason}")
        
        if should_log:
            # Tạo entry và thêm vào cả hai format
            entry = f"{user_name}\t{timestamp}"
            self.history.append(entry)
            print(f"   📝 Added to history: {entry}")
            
            # Thêm vào JSON format
            if user_name not in self.history_data:
                self.history_data[user_name] = []
            self.history_data[user_name].append(timestamp)
            print(f"   📝 Added to history_data: {user_name} -> {timestamp}")
            
            # Save ngay lập tức
            save_success = self.save_history()
            if save_success:
                print(f"   ✅ Successfully saved to file")
                return True
            else:
                print(f"   ❌ Failed to save to file")
                return False
        else:
            print(f"   ⏭️ Skipped logging: {reason}")
            return False

    def save_history(self):
        """Save history to file với error handling tốt hơn"""
        try:
            # Backup current file trước khi save
            if os.path.exists(self.login_history_file):
                backup_file = f"{self.login_history_file}.backup"
                import shutil
                shutil.copy2(self.login_history_file, backup_file)
            
            # Save theo JSON format mới (dictionary)
            with open(self.login_history_file, 'w', encoding='utf-8') as file:
                json.dump(self.history_data, file, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved {len(self.history_data)} users to {self.login_history_file}")
            return True
            
        except Exception as e:
            print(f"❌ File write error: {e}")
            return False

    def load_history(self):
        """Load history from file - Support both formats"""
        try:
            if os.path.exists(self.login_history_file):
                with open(self.login_history_file, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                
                # Kiểm tra format của data
                if isinstance(data, dict):
                    # JSON format mới: {"username": ["timestamp1", "timestamp2"]}
                    self.history_data = data
                    print(f"📂 Loaded JSON format: {len(self.history_data)} users")
                    
                    # Convert sang list format để backward compatibility
                    self.history = []
                    for username, timestamps in self.history_data.items():
                        for timestamp in timestamps:
                            self.history.append(f"{username}\t{timestamp}")
                    print(f"📂 Converted to {len(self.history)} text entries for compatibility")
                    
                elif isinstance(data, list):
                    # Old text format: ["Tu\t2025-08-25 16:41:56", ...]
                    self.history = data
                    print(f"📂 Loaded old text format: {len(self.history)} entries")
                    
                    # Convert sang JSON format
                    self.history_data = {}
                    for entry in self.history:
                        if '\t' in entry:
                            parts = entry.split('\t')
                            if len(parts) == 2:
                                username, timestamp = parts
                                if username not in self.history_data:
                                    self.history_data[username] = []
                                self.history_data[username].append(timestamp)
                    print(f"📂 Converted to JSON format: {len(self.history_data)} users")
                    
                    # Save lại theo format mới
                    self.save_history()
                    
            else:
                self.history = []
                self.history_data = {}
                print(f"📝 Created new empty history file")
                
        except Exception as e:
            print(f"❌ File read error: {e}")
            self.history = []
            self.history_data = {}
            
        return self.history

    def get_history(self):
        """Trả về copy của history"""
        return self.history.copy()

    def get_recent_history(self, limit=10):
        """Trả về các entry gần nhất"""
        return self.history[-limit:] if len(self.history) > limit else self.history.copy()

    def reset_history(self):
        """Xóa toàn bộ history"""
        self.history.clear()
        self.history_data.clear()
        self.save_history()

    def get_user_access_count(self, user_name):
        """Đếm số lần truy cập của một user (ưu tiên JSON format)"""
        # Ưu tiên JSON format
        if user_name in self.history_data:
            return len(self.history_data[user_name])
        
        # Fallback cho text format
        count = 0
        for entry in self.history:
            if '\t' in entry:
                parts = entry.split('\t')
                if len(parts) == 2 and parts[0] == user_name:
                    count += 1
        return count