cmake_minimum_required(VERSION 3.24)
cmake_policy(SET CMP0076 NEW)

project("pupil_detector_2d"
    LANGUAGES C CXX
    DESCRIPTION "Pupil Labs 2D Pupil Detector"
    HOMEPAGE_URL "https://github.com/pupil-labs/pupil-detectors"
)

# OpenCV 4 requires at least C++11, but we should be fine even selecting C++17 now
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

if(APPLE)
    # We target macOS 10.12, which does not offer c++17, but we can use c++1z instead.
    # See https://clang.llvm.org/cxx_status.html
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++1z")
endif()

# apply all recommended speed optimization (note -O3 is typically not recommeded
# as it heavily relies on well-written code)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")

if(MSVC)
    # for M_PI
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_USE_MATH_DEFINES")

    # TODO: This is a quick and dirty fix for:
    # https://github.com/pupil-labs/pupil/issues/1331 We should investigate this more
    # and fix it correctly at some point.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_ENABLE_EXTENDED_ALIGNED_STORAGE")
endif()

find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)
find_package(NumPy REQUIRED)
find_package(Eigen3 REQUIRED NO_MODULE)
find_package(OpenCV REQUIRED core imgproc) # add highgui to use imshow/waitKey

add_cython_target(detector_2d CXX PY3)
add_library(detector_2d MODULE ${detector_2d})
python_extension_module(detector_2d)

target_include_directories(
    detector_2d
    PUBLIC

    # external
    ${NumPy_INCLUDE_DIRS}
    ${OpenCV_INCLUDE_DIRS}
    ${EIGEN3_INCLUDE_DIRS}

    # local
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../cpp/shared/include>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../cpp>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../cpp/singleeyefitter>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../cpp/singleeyefitter/ImageProcessing>
)

target_sources(
    detector_2d
    PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../cpp/singleeyefitter/detectorUtils.cpp>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../cpp/singleeyefitter/utils.cpp>
    $<BUILD_INTERFACE:${CMAKE_CURRENT_LIST_DIR}/../cpp/singleeyefitter/ImageProcessing/cvx.cpp>
)

target_link_libraries(detector_2d ${OpenCV_LIBS} ${EIGEN3_LIBS})

install(TARGETS detector_2d LIBRARY DESTINATION "detector_2d")
