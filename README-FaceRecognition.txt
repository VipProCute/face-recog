########### How to build ###########

tar -xf face_recognition_sface_2021dec_ovx.tgz
tar -xf FaceRecognition_sface_pybind.tgz

export ROOT_DIR=YOUR_PATH

export OPENCV_INCLUDE=$ROOT_DIR/opencv4.10/include
export OPENCV_LIB=$ROOT_DIR/opencv4.10/lib

export CROSS_COMPILE=YOUR_PATH/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-


export VIVANTE_SDK_DIR=YOUR_PATH/6.4.15.9


#example
#export ROOT_DIR=/mnt/i/AnhTu/Internship/working
#export OPENCV_INCLUDE=$ROOT_DIR/opencv4.10/include
#export OPENCV_LIB=$ROOT_DIR/opencv4.10/lib
#export CROSS_COMPILE=$ROOT_DIR/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-
#export VIVANTE_SDK_DIR=$ROOT_DIR/6.4.15.9

cd face_recognition_sface_2021dec_ovx
make clean
make

# No need to build this again if you don't modify binding functions
#cd FaceRecognition_sface_pybind/build
#make clean
#cmake --build .

scp libFaceRecog_wrapper.so itri@10.60.3.235:/home/itri/Working/NATu/FaceRecognition-FAISS




########### How to run ###########

ssh itri@10.60.3.235

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/itri/Working/prebuilt/opencv/lib
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$PWD

cd ~/Working/Demo/
source venv_3.8/bin/activate

cd ~/Working/NATu/FaceRecognition-FAISS
streamlit run app_streamlit.py
