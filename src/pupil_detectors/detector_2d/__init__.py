"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

# rename from python side, since Detector2D is already defined in cython from c++
from .detector_2d import Detector2DCore as Detector2D

__all__ = ["Detector2D"]
