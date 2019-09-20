import abc
import typing as T


class PupilDetector(abc.ABC):

    ##### Legacy API

    def set_2d_detector_property(self, name: str, value: T.Any):
        raise TypeError(f"2d properties not available for detectior: {type(self)}")

    def set_3d_detector_property(self, name: str, value: T.Any):
        raise TypeError(f"3d properties not available for detectior: {type(self)}")

    ##### Core API

    @abc.abstractmethod
    def detect(self, frame, user_roi, visualize, pause_video: bool = False, **kwargs):
        pass

    @abc.abstractmethod
    def namespaced_detector_properties(self) -> dict:
        pass

    @abc.abstractmethod
    def on_resolution_change(self, old_size, new_size):
        pass

