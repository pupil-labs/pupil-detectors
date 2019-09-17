"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""


class Detector_Dummy:

    def __init__(*args, **kwargs):
        pass

    def detect(self, frame, *args, **kwargs):
        return None

    def visualize(self):
        pass

    def get_settings(self):
        return {}

    def on_resolution_change(self, *args, **kwargs):
        pass

    def set_2d_detector_property(self, *args, **kwargs):
        pass

    def get_detector_properties(self):
        return {}
