#include <stdio.h>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

// extern "C" {
#include "FaceRecog_wrapper.h"
// }


namespace py = pybind11;
using namespace std;

#define STRINGIFY(x) #x
#define MACRO_STRINGIFY(x) STRINGIFY(x)



#if 1

int32_t init_neural_networks_py() {
    return init_neural_networks();
}

std::tuple<uint8_t, std::vector<float>> register_user_py(py::array_t<uint8_t> _img_buf, uint16_t height, uint16_t width, const uint8_t chanels) {
    int depth = CV_8UC1; // unsigned char - 1 channel

    std::cout << __FUNCTION__ << "():" << __LINE__ << std::endl;
    std::cout << "height: " << height << std::endl;
    std::cout << "width: " << width << std::endl;
    std::cout << "chanels: " << chanels << std::endl;

    // auto img_buf = _img_buf.unchecked<3>();
    py::buffer_info img_buf = _img_buf.request();
    // uint16_t height = img_buf.shape(0);
    // uint16_t width = img_buf.shape(1);
    std::cout << "img_buf.shape(0): " << img_buf.shape[0] << std::endl;
    std::cout << "img_buf.shape(1): " << img_buf.shape[1] << std::endl;
    std::cout << "img_buf.shape(2): " << img_buf.shape[2] << std::endl;
    // std::cout << "img_buf.ndim(): " << img_buf.ndim() << std::endl;
    uint8_t chanels_ = img_buf.shape[2];
    switch (chanels_)
    {
    case 1:
        depth = CV_8UC1;
        break;
    case 3:
        depth = CV_8UC3;
        break;

    default:
        depth = CV_8UC4;
        break;
    }

    cv::Mat image( height, width, depth, img_buf.ptr, cv::Mat::AUTO_STEP );

    return register_user(image);
}

std::tuple<uint16_t, uint16_t, uint16_t, uint16_t, float, std::vector<float>> detect_face_py(py::array_t<uint8_t> _img_buf, uint16_t height, uint16_t width, const uint8_t chanels) {
    int depth = CV_8UC1; // unsigned char - 1 channel
    // std::vector<uint16_t> result = {0, 0, 0, 0};

    // std::cout << __FUNCTION__ << "():" << __LINE__ << std::endl;
    // std::cout << "height: " << height << std::endl;
    // std::cout << "width: " << width << std::endl;
    // std::cout << "chanels: " << chanels << std::endl;
    // auto img_buf = _img_buf.unchecked<3>();
    py::buffer_info img_buf = _img_buf.request();
    // std::cout << "img_buf.shape(0): " << img_buf.shape[0] << std::endl;
    // std::cout << "img_buf.shape(1): " << img_buf.shape[1] << std::endl;
    // std::cout << "img_buf.shape(2): " << img_buf.shape[2] << std::endl;
    // std::cout << "img_buf.ndim(): " << img_buf.ndim() << std::endl;
    // std::cout << "chanels: " << chanels << std::endl;
    uint16_t chanels_ = img_buf.shape[2];
    // std::cout << "chanels_: " << chanels_ << std::endl;
    switch (chanels_)
    {
    case 1:
        depth = CV_8UC1;
        break;
    case 3:
        depth = CV_8UC3;
        break;

    default:
        depth = CV_8UC4;
        break;
    }

    cv::Mat image( height, width, depth, img_buf.ptr, cv::Mat::AUTO_STEP );

    // result = detect_face(image);
    // std::cout << "left: " << result[0] << std::endl;
    // std::cout << "top: " << result[1] << std::endl;
    // std::cout << "right: " << result[2] << std::endl;
    // std::cout << "bottom: " << result[3] << std::endl;

    return detect_face(image);
}


PYBIND11_MODULE(face_recognition_pybind, m) {
    init_neural_networks();

    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: face_recognition_pybind

        .. autosummary::
           :toctree: _generate

           init_neural_networks
           register_user
    )pbdoc";

    m.def("init_neural_networks", &init_neural_networks_py, R"pbdoc(
        init_neural_networks
        
    )pbdoc");

    m.def("register_user", &register_user_py, R"pbdoc(
        register_user

    )pbdoc");

    m.def("detect_face", &detect_face_py, R"pbdoc(
        detect_face

    )pbdoc");

    // m.def("multiply", [](int i, int j) { return i * j; }, R"pbdoc(
    //     Multiply two numbers

    //     Some other explanation about the multiply function.
    // )pbdoc");

    //   m.def("divide", &divide_py, R"pbdoc(
    //     Divide two numbers

    //     Some other explanation about the divide function.
    // )pbdoc");

    //   m.def("detect_face", &detect_face_py, R"pbdoc(
    //     Detect face

    //     Some other explanation about the detect_face function.
    // )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
#endif




#if 0
string printName_py(string name, string lastname) {
    greet("NhanTran");
    return "This function works " + name + " " + lastname + "!";
}

double divide_py(double num1, double num2) {

    //  Calculator calculator;
     double result = 0;

     result = divide(num1, num2);
    

    return result;
}

#if 1
// OpenCV
void detect_face_py() {
    detect_face();
}


#endif



namespace py = pybind11;

PYBIND11_MODULE(face_recognition_pybind, m) {
    m.doc() = R"pbdoc(
        Pybind11 example plugin
        -----------------------

        .. currentmodule:: face_recognition_pybind

        .. autosummary::
           :toctree: _generate

           add
           subtract
    )pbdoc";

    m.def("printName", &printName_py, R"pbdoc(
        Print first and last name

        Some other explanation about the printName function.
    )pbdoc");

    // m.def("multiply", [](int i, int j) { return i * j; }, R"pbdoc(
    //     Multiply two numbers

    //     Some other explanation about the multiply function.
    // )pbdoc");

      m.def("divide", &divide_py, R"pbdoc(
        Divide two numbers

        Some other explanation about the divide function.
    )pbdoc");

      m.def("detect_face", &detect_face_py, R"pbdoc(
        Detect face

        Some other explanation about the detect_face function.
    )pbdoc");

#ifdef VERSION_INFO
    m.attr("__version__") = MACRO_STRINGIFY(VERSION_INFO);
#else
    m.attr("__version__") = "dev";
#endif
}
#endif

