import abc
import typing as T

from plugin import Plugin


class Detector_Base(abc.ABC, Plugin):

    ### Core

    @abc.abstractmethod
    def detector_properties(self) -> dict:
        pass

    @abc.abstractmethod
    def detect(self, frame, user_roi, visualize, pause_video: bool = False):
        pass

    ### GUI

    @abc.abstractmethod
    def visualize(self):
        pass

    @abc.abstractmethod
    def on_resolution_change(self, *args, **kwargs):
        pass

    ### Legacy

    def get_settings(self):
        return self.detector_properties

    def get_detector_properties(self):
        return self.detector_properties

    def set_2d_detector_property(self, name, value):
        pass

    def set_3d_detector_property(self, name, value):
        pass
