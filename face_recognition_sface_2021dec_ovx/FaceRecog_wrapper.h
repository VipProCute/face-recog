#ifndef _WRAPPER_H_
#define _WRAPPER_H_

#include <opencv2/opencv.hpp>


extern "C" {
    int32_t init_neural_networks();
    std::tuple<uint8_t, std::vector<float>> register_user(cv::Mat img);
    std::tuple<uint16_t, uint16_t, uint16_t, uint16_t, float, std::vector<float>> detect_face(cv::Mat img);
}




#endif // _WRAPPER_H_
