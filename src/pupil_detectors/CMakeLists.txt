cmake_minimum_required (VERSION 3.8)

project("pupil_detectors")

# OpenCV 4 requires at least C++11, but we should be fine even selecting C++17 now
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)

if (APPLE)
    # We target macOS 10.12, which does not offer c++17, but we can use c++1z instead.
    # See https://clang.llvm.org/cxx_status.html
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++1z")
endif ()

# apply all recommended speed optimization (note -O3 is typically not recommeded
# as it heavily relies on well-written code)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O2")

if (MSVC)
    # for M_PI
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_USE_MATH_DEFINES")
    # TODO: This is a quick and dirty fix for:
    # https://github.com/pupil-labs/pupil/issues/1331 We should investigate this more
    # and fix it correctly at some point.
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -D_ENABLE_EXTENDED_ALIGNED_STORAGE")
endif ()

# find skbuild cmake packages
find_package(PythonExtensions REQUIRED)
find_package(Cython REQUIRED)

# find external cmake packages
find_package(NumPy REQUIRED)
find_package(Eigen3 3.3 REQUIRED NO_MODULE)
# Find OpenCV. Needs to be on cmake search path, or specify OpenCV_DIR variable.
find_package(OpenCV REQUIRED)

# include "cpp" and "detector_2d" for finding headers
include_directories("cpp")
include_directories("detector_2d")
# include numpy headers
include_directories(${NumPy_INCLUDE_DIRS})

# Note: add_cython_target does not actually add a target, but fills a variable with the
# corresponding compiled source file, e.g. here 'pupil_detection_3d.cxx'. If only the
# name is specified, it will look for a cython file with the same base name:
# 'pupil_detection_3d.pyx' in this case.
add_cython_target(detector_2d "detector_2d/detector_2d.pyx" CXX PY3)
# Create a module library from the source file and wrap it with settings for
# creating a python extension.
add_library(detector_2d MODULE ${detector_2d})
python_extension_module(detector_2d)
# link against external libraries
target_link_libraries(detector_2d ${OpenCV_LIBS})
target_link_libraries(detector_2d Eigen3::Eigen)


add_cython_target(detector_base CXX PY3)
add_library(detector_base MODULE ${detector_base})
python_extension_module(detector_base)

# TODO: Need to do the same for all the other cython modules?

# install in detector_2d
install(
    TARGETS detector_2d
    LIBRARY DESTINATION "detector_2d")

# install in here
install(
    TARGETS detector_base
    LIBRARY DESTINATION ".")
