import platform

from setuptools import find_packages
from skbuild import setup

package = "pupil_detectors"
package_dir = "src"

cmake_args = []

if platform.system() == "Windows":
    # The Ninja cmake generator will use mingw (gcc) on windows travis instances, but we
    # need to use msvc for compatibility.
    cmake_args.append("-GVisual Studio 17 2022")


if __name__ == "__main__":
    setup(
        cmake_args=cmake_args,
        cmake_install_dir="src/pupil_detectors",
        cmake_source_dir="src/pupil_detectors",
        packages=find_packages(package_dir),
        package_dir={"": package_dir},
        include_package_data=False,
    )
