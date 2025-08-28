# AUTO GENERATED FILE, BUILD AND RUN IN OVXLIB

package(default_visibility = ["//visibility:public"])

filegroup(
    name = "srcs",
    srcs =
        [
        "vnn_.c",
        "vnn_.h",
        "vnn_post_process.c",
        "vnn_post_process.h",
        "vnn_pre_process.c",
        "vnn_pre_process.h",
        "vnn_global.h",
        "main.c",
        "Android.mk",
        ],
)

cc_binary(
    name = "inference",
    srcs = [":srcs"] + ["//:ovxlib"],
    deps = [
        "//third-party/jpeg-9b:libjpeg",
        "//:ovxlib",
        "@VIV_SDK//:VIV_SDK_LIB",
    ],
)
