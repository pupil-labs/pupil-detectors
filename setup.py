"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

import os
import platform
import sysconfig

import numpy as np
from Cython.Build import cythonize
from setuptools import find_packages, setup, Extension
from pathlib import Path

package_dir = "src"
package = "pupil_detectors"

########################################################################################
# Setup Libraries

include_dirs = []
libraries = []
library_dirs = []

# Cross-platform setup
include_dirs += [
    package_dir,
    f"{package_dir}/pupil_detectors/detector_2d",
    f"{package_dir}/shared_cpp/include",
    f"{package_dir}/singleeyefitter/",
    np.get_include(),
]

# Platform-specific setup
if platform.system() == "Windows":
    OPENCV = "C:\\work\\opencv\\build"
    include_dirs.append(f"{OPENCV}\\include")
    library_dirs.append(f"{OPENCV}\\x64\\vc14\\lib")
    libraries.append("opencv_world345")

    EIGEN = "C:\\work\\ceres-windows\\Eigen"
    include_dirs.append(f"{EIGEN}")

    CERES = "C:\\work\\ceres-windows"
    # NOTE: ceres for windows needs to link against glog
    include_dirs.append(f"{CERES}")
    include_dirs.append(f"{CERES}\\ceres-solver\\include")
    include_dirs.append(f"{CERES}\\glog\\src\\windows")
    library_dirs.append(f"{CERES}\\x64\\Release")
    libraries.append("ceres_static")
    libraries.append("libglog_static")

else:
    # Opencv
    opencv_include_dirs = [
        "/usr/local/opt/opencv/include",  # old opencv brew (v3)
        "/usr/local/opt/opencv@3/include",  # new opencv@3 brew
        "/usr/local/include/opencv4",  # new opencv brew (v4)
    ]
    opencv_library_dirs = [
        "/usr/local/opt/opencv/lib",  # old opencv brew (v3)
        "/usr/local/opt/opencv@3/lib",  # new opencv@3 brew
        "/usr/local/lib",  # new opencv brew (v4)
    ]
    opencv_libraries = [
        "opencv_core",
        "opencv_highgui",
        "opencv_videoio",
        "opencv_imgcodecs",
        "opencv_imgproc",
        "opencv_video",
    ]
    # Check if OpenCV has been installed through ROS
    opencv_core_found = any(
        os.path.isfile(path + "/libopencv_core.so") for path in opencv_library_dirs
    )
    if not opencv_core_found:
        ros_dists = ["kinetic", "jade", "indigo"]
        for ros_dist in ros_dists:
            ros_candidate_path = "/opt/ros/" + ros_dist + "/lib"
            if os.path.isfile(ros_candidate_path + "/libopencv_core3.so"):
                opencv_library_dirs = [ros_candidate_path]
                opencv_include_dirs = [
                    "/opt/ros/" + ros_dist + "/include/opencv-3.1.0-dev"
                ]
                opencv_libraries = [lib + "3" for lib in opencv_libraries]
                break
    include_dirs += opencv_include_dirs
    library_dirs += opencv_library_dirs
    libraries += opencv_libraries

    # Eigen
    include_dirs += [
        "/usr/local/include/eigen3",
        "/usr/include/eigen3",
    ]

    # Ceres
    libraries.append("ceres")

########################################################################################
# Setup Compile Args

extra_compile_args = []
extra_compile_args += [
    "-w",  # suppress all warnings (TODO: Why do we do this?)
]
if platform.system() == "Windows":
    # NOTE: c++11 is not available as compiler flag on MSVC
    extra_compile_args += [
        "-O2",  # best speed optimization for MSVC
        "-D_USE_MATH_DEFINES",  # for M_PI
        # TODO: This is a quick and dirty fix for:
        # https://github.com/pupil-labs/pupil/issues/1331 We should investigate this more
        # and fix it correctly at some point.
        "-D_ENABLE_EXTENDED_ALIGNED_STORAGE",
    ]
else:
    extra_compile_args += [
        "-std=c++11",
        # apply all recommended speed optimization (note -O3 is typically not recommeded
        # as it heavily relies on well-written code)
        "-O2",
    ]


########################################################################################
# Extension specs

extensions = [
    Extension(
        name="pupil_detectors.detector_base",
        sources=[f"{package_dir}/pupil_detectors/detector_base.pyx"],
        language="c++",
        extra_compile_args=extra_compile_args,
    ),
    Extension(
        name="pupil_detectors.detector_2d.detector_2d",
        sources=[
            f"{package_dir}/pupil_detectors/detector_2d/detector_2d.pyx",
            f"{package_dir}/singleeyefitter/ImageProcessing/cvx.cpp",
            f"{package_dir}/singleeyefitter/utils.cpp",
            f"{package_dir}/singleeyefitter/detectorUtils.cpp",
        ],
        language="c++",
        include_dirs=include_dirs,
        libraries=libraries,
        library_dirs=library_dirs,
        extra_compile_args=extra_compile_args,
    ),
    Extension(
        name="pupil_detectors.detector_3d.detector_3d",
        sources=[
            f"{package_dir}/pupil_detectors/detector_3d/detector_3d.pyx",
            f"{package_dir}/singleeyefitter/ImageProcessing/cvx.cpp",
            f"{package_dir}/singleeyefitter/utils.cpp",
            f"{package_dir}/singleeyefitter/detectorUtils.cpp",
            f"{package_dir}/singleeyefitter/EyeModelFitter.cpp",
            f"{package_dir}/singleeyefitter/EyeModel.cpp",
        ],
        language="c++",
        include_dirs=include_dirs,
        libraries=libraries,
        library_dirs=library_dirs,
        extra_compile_args=extra_compile_args,
    ),
]
########################################################################################
# Setup Script

print("INCLUDE DIRS:")
print(*(f" - {v}\n" for v in include_dirs), sep="")

print("LIBRARY DIRS:")
print(*(f" - {v}\n" for v in library_dirs), sep="")

print("LIBRARIES:")
print(*(f" - {v}\n" for v in libraries), sep="")

print("COMPILE ARGS:")
print(*(f" - {v}\n" for v in extra_compile_args), sep="")

if __name__ == "__main__":
    setup(
        name="pupil-detectors",
        version="0.2",
        packages=find_packages(package_dir),
        package_dir={"": package_dir},
        url="https://github.com/pupil-labs/pupil-detectors",
        author="Pupil Labs",
        author_email="info@pupil-labs.com",
        license="GNU",
        ext_modules=cythonize(extensions, quiet=True, nthreads=8),
    )
