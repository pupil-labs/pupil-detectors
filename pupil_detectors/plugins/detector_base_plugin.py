import abc
import typing as T

from pupil_detectors import PupilDetector

from plugin import Plugin


class PupilDetectorPlugin(PupilDetector, Plugin):

    ########## PupilDetectorPlugin API

    @property
    @abc.abstractmethod
    def pupil_detector(self) -> PupilDetector:
        pass

    ##### Plugin API

    def __init__(self, g_pool):
        super().__init__(g_pool=g_pool)

    def init_ui(self):
        super().init_ui()

    def gl_display(self):
        super().gl_display()

    def recent_events(self, event):
        super().recent_events(event)

        frame = event.get("frame")
        if not frame:
            return

        # TODO: Extract event handling logic from eye.py

        # Pupil ellipse detection
        event["pupil_detection_result"] = self.detect(
            frame=frame,
            user_roi=self.g_pool.u_r,
            visualize=self.g_pool.display_mode == "algorithm",
        )

    def on_notify(self, notification):
        super().on_notify(notification)
        # TODO: Extract notification handling logic from eye.py

    def deinit_ui(self):
        super().deinit_ui()

    def cleanup(self):
        super().cleanup()

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
