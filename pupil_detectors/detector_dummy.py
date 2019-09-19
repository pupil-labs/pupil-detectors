"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""
from .detector_base import Detector_Base


class Detector_Dummy(Detector_Base):

    ### Core

    def detector_properties(self) -> dict:
        return {}

    def detect(self, frame, user_roi, visualize, pause_video: bool = False):
        return None

    ### GUI

    def visualize(self):
        pass

    def on_resolution_change(self, *args, **kwargs):
        pass
