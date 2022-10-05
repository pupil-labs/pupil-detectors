cmake_minimum_required(VERSION 3.24)

project("pupil_detector_base"
    LANGUAGES C CXX
    DESCRIPTION "Pupil Labs Base Pupil Detector"
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

add_cython_target(detector_base CXX PY3)
add_library(detector_base MODULE ${detector_base})
python_extension_module(detector_base)

add_subdirectory(detector_2d)

install(TARGETS detector_base LIBRARY DESTINATION ".")
