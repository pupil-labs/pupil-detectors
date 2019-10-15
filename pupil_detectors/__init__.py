"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

from .utils import Roi
from .detector_base import DetectorBase
from .detector_2d import Detector2D
from .detector_3d import Detector3D

# TODO: Find out if this is still the case
# # explicit import here for pyinstaller because it will not search .pyx source files.
# from .detector_3d import Eye_Visualizer
