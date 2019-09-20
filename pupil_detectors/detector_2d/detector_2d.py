from pupil_detectors.detector_base import PupilDetector

from .detector_2d_core import Detector2DCore


DETECTOR_2D_PROPERTIES_NAMESPACE = "2d"

def detector_2d_properties_from_namespaced_properties(namespaced_properties: dict) -> dict:
    properties = detector_2d_default_properties()
    properties.update(namespaced_properties.get(DETECTOR_2D_PROPERTIES_NAMESPACE, {}))
    return properties


def detector_2d_properties_to_namespaced_properties(detector_2d_properties: dict) -> dict:
    return {DETECTOR_2D_PROPERTIES_NAMESPACE: detector_2d_properties}


def detector_2d_default_properties():
    properties = {}
    properties["coarse_detection"] = True
    properties["coarse_filter_min"] = 128
    properties["coarse_filter_max"] = 280
    properties["intensity_range"] = 23
    properties["blur_size"] = 5
    properties["canny_treshold"] = 160
    properties["canny_ration"] = 2
    properties["canny_aperture"] = 5
    properties["pupil_size_max"] = 100
    properties["pupil_size_min"] = 10
    properties["strong_perimeter_ratio_range_min"] = 0.6
    properties["strong_perimeter_ratio_range_max"] = 1.1
    properties["strong_area_ratio_range_min"] = 0.8
    properties["strong_area_ratio_range_max"] = 1.1
    properties["contour_size_min"] = 5
    properties["ellipse_roundness_ratio"] = 0.09
    properties["initial_ellipse_fit_treshhold"] = 4.3
    properties["final_perimeter_ratio_range_min"] = 0.5
    properties["final_perimeter_ratio_range_max"] = 1.0
    properties["ellipse_true_support_min_dist"] = 3.0
    properties["support_pixel_ratio_exponent"] = 2.0
    return properties


class Detector2D(Detector2DCore, PupilDetector):
    # TODO: Adopt PupilDetector interface

    def __init__(self, namespaced_properties = {}):
        detector_2d_properties = detector_2d_properties_from_namespaced_properties(namespaced_properties)
        super().__init__(detector_2d_properties)

    ##### Legacy API

    # set_2d_detector_property implemented by Detector_2D_Core

    ##### Core API

    # detect implemented by Detector_2D_Core

    def namespaced_detector_properties(self) -> dict:
        return detector_2d_properties_to_namespaced_properties(self.detector_2d_properties)

    def on_resolution_change(self, old_size, new_size):
        self.detector_properties_2d["pupil_size_max"] *= new_size[0] / old_size[0]
        self.detector_properties_2d["pupil_size_min"] *= new_size[0] / old_size[0]
