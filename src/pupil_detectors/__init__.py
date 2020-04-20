"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

__version__ = "1.0.5"

import platform

if platform.system() == "Windows":
    # On Windows wheels we ship custom opencv DLLs that we need to inject into PATH
    import os
    from pathlib import Path

    data_path = Path(__file__).parent / ".package_data"
    os.environ["PATH"] = str(data_path.resolve()) + os.pathsep + os.environ["PATH"]


from .utils import Roi
from .detector_base import DetectorBase
from .detector_2d import Detector2D
from .detector_3d import Detector3D
