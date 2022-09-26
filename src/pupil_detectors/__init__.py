try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("pupil_detectors")
except PackageNotFoundError:
    # package is not installed
    pass

from .roi import Roi
from .detector_base import DetectorBase
from .detector_2d import Detector2D

__all__ = ["__version__", "DetectorBase", "Detector2D", "Roi"]
