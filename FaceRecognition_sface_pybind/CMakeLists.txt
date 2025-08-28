cmake_minimum_required(VERSION 3.4...3.18)
project(face_recognition)

set(PYBIND11_FINDPYTHON OFF)
# set(PYBIND11_PYTHON_VERSION 3.8)

set(ROOT_DIR "/working/workspace/VNEMEX/SOM-VIP9000/FaceRecognition")
set(PYTHON_MODULE_EXTENSION ".so" CACHE INTERNAL "Cross python lib extension")
set(PYTHONLIBS_FOUND TRUE CACHE INTERNAL "")
# set(PYTHON_INCLUDE_DIRS "/working/workspace/VNEMEX/Demo/FaceRecognition/ARM/prebuilt/python-3.8-aarch64/3.8.18/include/python3.8" CACHE INTERNAL "Cross python include path")
set(PYTHON_INCLUDE_DIRS ${ROOT_DIR}/prebuilt/python-3.8-aarch64/3.8.18/include/python3.8 CACHE INTERNAL "Cross python include path")
# set(PYTHON_INCLUDE_DIRS "" CACHE INTERNAL "Cross python include path")
# set(PYTHON_INCLUDE_DIRS "/usr/include/python3.8")

add_subdirectory(pybind11)

pybind11_add_module(face_recognition_pybind face_recognition_pybind.cpp)

# add_library(face_recognition_wrapper SHARED face_recognition_wrapper.cpp)

# set(ROOT_DIR "/working/workspace/VNEMEX/SOM-VIP9000/FaceRecognition")
set(OpenCV_INCLUDE_DIRS ${ROOT_DIR}/prebuilt/opencv/include)
set(OpenCV_LIB_DIR ${ROOT_DIR}/prebuilt/opencv/lib)
# set(OpenCV_LIBS "-lopencv_core -lopencv_imgproc -lopencv_videoio -lopencv_dnn -lopencv_objdetect -lopencv_imgcodecs -lopencv_highgui")
# set(OpenCV_LIBS "-lopencv_core")

# set(LFLAGS_ -Wl,-rpath-link=${OPENCV_LIB})

# target_include_directories(face_recognition_wrapper PRIVATE ${OpenCV_INCLUDE_DIRS})
# target_link_libraries(face_recognition_wrapper PRIVATE pybind11::module ${OpenCV_LIBS})

include_directories(${OpenCV_INCLUDE_DIRS})
include_directories(${OpenCV_INCLUDE_DIRS}/opencv2)


#**************************************************************************************************

# EXAMPLE_VERSION_INFO is defined by setup.py and passed into the C++ code as a
# define (VERSION_INFO) here.
# target_compile_definitions(face_recognition_pybind
#                            PRIVATE VERSION_INFO=${EXAMPLE_VERSION_INFO})


target_link_libraries(face_recognition_pybind PRIVATE ${ROOT_DIR}/models/FaceRecognition_sface_pybind/libFaceRecog_wrapper.so)


