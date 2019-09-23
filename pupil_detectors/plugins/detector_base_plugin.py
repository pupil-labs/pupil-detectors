import abc
import typing as T

from pupil_detectors import PupilDetector


class PupilDetectorPlugin(PupilDetector):

    # TODO: Fill out Plugin API

    @property
    @abc.abstractmethod
    def pupil_detector(self) -> PupilDetector:
        pass

    @abc.abstractmethod
    def gl_display(self):
        pass

    ########## PupilDetector API

    ##### Legacy API

    def set_2d_detector_property(self, name: str, value: T.Any):
        return self.pupil_detector.set_2d_detector_property(name=name, value=value)

    def set_3d_detector_property(self, name: str, value: T.Any):
        return self.pupil_detector.set_3d_detector_property(name=name, value=value)

    ##### Core API

    def detect(self, frame, user_roi, visualize, pause_video: bool = False, **kwargs):
        return self.pupil_detector.detect(frame=frame, user_roi=user_roi, visualize=visualize, pause_video=pause_video, **kwargs)

    def namespaced_detector_properties(self) -> dict:
        return self.pupil_detector.namespaced_detector_properties()

    def on_resolution_change(self, old_size, new_size):
        return self.pupil_detector.on_resolution_change(old_size=old_size, new_size=new_size)
