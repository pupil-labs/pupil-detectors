try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version

try:
    __version__ = version("pupil_detectors")
except PackageNotFoundError:
    # package is not installed
    pass

from .detector_2d import Detector2D
from .detector_base import DetectorBase
from .roi import Roi

__all__ = ["__version__", "DetectorBase", "Detector2D", "Roi"]
