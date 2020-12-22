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
from setuptools import find_packages
from skbuild import setup

package = "pupil_detectors"
package_dir = "src"
package_data = []

install_requires = [
    "numpy",
    # The prebuilt versions of opencv for Windows do not contain python bindings. For
    # ease of use we install these via pip. On Unix we get cv2 from the documented ways
    # of installing opencv with python bindings.
    'opencv-python ; platform_system == "Windows"',
    # Better cython interfacing, not available for windows.
    'cysignals ; platform_system != "Windows"',
]

extras_require = {
    "dev": ["pytest", "tox"],
}

cmake_args = []

if os.environ.get("CI", "false") == "true" and platform.system() == "Windows":
    # The Ninja cmake generator will use mingw (gcc) on windows travis instances, but we
    # need to use msvc for compatibility.
    cmake_args.append("-GVisual Studio 16 2019")

with open("README.md") as f:
    readme = f.read()

with open("CHANGELOG.md") as f:
    changelog = f.read()

long_description = f"{readme}\n\n{changelog}"

if __name__ == "__main__":
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
        cmake_args=cmake_args,
        cmake_install_dir="src/pupil_detectors",
        cmake_source_dir="src/pupil_detectors",
        description="Pupil detectors",
        extras_require=extras_require,
        install_requires=install_requires,
        license="GNU",
        long_description=long_description,
        long_description_content_type="text/markdown",
        name="pupil-detectors",
        packages=find_packages(package_dir),
        package_data={package: package_data},
        package_dir={"": package_dir},
        url="https://github.com/pupil-labs/pupil-detectors",
        version="2.0.1",
        zip_save=False,
    )
