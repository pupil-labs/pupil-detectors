"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

import ctypes.util
import os
import platform
import shutil
import sysconfig
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, find_packages, setup

package_dir = "src"
package = "pupil_detectors"

install_requires = [
    "numpy",
]

if platform.system() == "Windows":
    # The prebuilt versions of opencv for Windows do not contain python bindings. For
    # ease of use we install these via pip. On Unix we get cv2 from the documented ways
    # of installing opencv with python bindings.
    install_requires.append("opencv-python")
else:
    # Better cython interfacing, not available for windows.
    install_requires.append("cysignals")

########################################################################################
# Setup Libraries

include_dirs = []
libraries = []
library_dirs = []
external_package_data = []


@contextmanager
def collect_external_package_data(external_package_data):
    # Temporarily copies external package data into the package and removes it again.
    # This function can be wrapped around setup(). Package data will onyl be used for
    # wheels though.
    root = Path(__file__).parent
    temp_path = root / package_dir / package / ".package_data"
    temp_path.mkdir(exist_ok=True)

    collected_data = []
    for raw_file in external_package_data:
        raw_file_path = Path(raw_file)
        shutil.copy(raw_file_path, temp_path)
        # NOTE: This needs to be separated by forward-slashes '/' otherwise it will not
        # work! See # https://setuptools.readthedocs.io/en/latest/setuptools.html#including-data-files
        collected_data.append(f".package_data/{raw_file_path.name}")
        if not (temp_path / raw_file_path.name).exists():
            raise FileNotFoundError(f"Could not copy data file {raw_file_path.name}")

    yield collected_data

    shutil.rmtree(temp_path)


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
    OPENCV_VERSION = "345"
    OPENCV_DLL_NAME = f"opencv_world{OPENCV_VERSION}"
    include_dirs.append(f"{OPENCV}\\include")
    library_dirs.append(f"{OPENCV}\\x64\\vc14\\lib")
    libraries.append(OPENCV_DLL_NAME)
    # We want to ship opencv in windows wheels, so that we don't have any external
    # dependencies. Ceres is statically compiled and opencv will be supplied.
    opencv_dll = ctypes.util.find_library(OPENCV_DLL_NAME)
    if opencv_dll is None:
        raise FileNotFoundError(
            f"Could not find {OPENCV_DLL_NAME}.dll."
            f" Please add the location to your PATH!"
        )
    external_package_data.append(opencv_dll)

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
    "-w",  # suppress all warnings (we get a lot of warnings from the c++ code)
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

# TODO: Cython recommends to include the generated cpp files in the source distribution
# and try to build from those first, only regenerating the cpp files from cython as a
# fallback. We don't do this currently, but since we are going to ship wheels, it won't
# be so bad since most users can just install the wheels. Read about this here:
# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
# Also: Does that mean we have to store the generated cpp files in git?

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

with open("README.md") as f:
    readme = f.read()

with open("CHANGELOG.md") as f:
    changelog = f.read()

long_description = f"{readme}\n\n{changelog}"

if __name__ == "__main__":
    with collect_external_package_data(external_package_data) as package_data:
        setup(
            author="Pupil Labs GmbH",
            author_email="pypi@pupil-labs.com",
            classifiers=[
                "Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
                "Natural Language :: English",
                "Programming Language :: C++",
                "Programming Language :: Cython",
                "Programming Language :: Python :: 3",
                "Topic :: Scientific/Engineering",
            ],
            description="Pupil detectors",
            extras_require={"dev": ["pytest", "tox"]},
            ext_modules=cythonize(extensions, quiet=True, nthreads=8),
            install_requires=install_requires,
            license="GNU",
            long_description=long_description,
            long_description_content_type="text/markdown",
            name="pupil-detectors",
            packages=find_packages(package_dir),
            package_data={package: package_data},
            package_dir={"": package_dir},
            url="https://github.com/pupil-labs/pupil-detectors",
            version="1.0.5",
            zip_save=False,
        )
