from pupil_detectors.detector_base import PupilDetector
from pupil_detectors.detector_2d import DETECTOR_2D_PROPERTIES_NAMESPACE, detector_2d_properties_from_namespaced_properties, detector_2d_properties_to_namespaced_properties

from .detector_3d_core import Detector3DCore


DETECTOR_3D_PROPERTIES_NAMESPACE = "3d"


def detector_3d_properties_from_namespaced_properties(namespaced_properties: dict) -> dict:
    properties = detector_3d_default_properties()
    properties.update(namespaced_properties.get(DETECTOR_3D_PROPERTIES_NAMESPACE, {}))
    return properties


def detector_3d_properties_to_namespaced_properties(detector_3d_properties: dict) -> dict:
    return {DETECTOR_3D_PROPERTIES_NAMESPACE: detector_3d_properties}


def detector_3d_default_properties():
    properties = {}
    properties["model_sensitivity"] = 0.997
    properties["model_is_frozen"] = False
    return properties


class Detector3D(Detector3DCore, PupilDetector):
    # TODO: Adopt PupilDetector interface

    def __init__(self, namespaced_properties = {}):
        namespaced_properties = _upgade_legacy_namespaced_properties(namespaced_properties)
        detector_properties_2d = detector_2d_properties_from_namespaced_properties(namespaced_properties)
        detector_properties_3d = detector_3d_properties_from_namespaced_properties(namespaced_properties)
        super().__init__(detector_properties_2d, detector_properties_3d)

    ##### Legacy API

    # set_2d_detector_property implemented by Detector3DCore

    # set_3d_detector_property implemented by Detector3DCore

    ##### Core API

    def namespaced_detector_properties(self) -> dict:
        properties = {}
        properties.update(detector_2d_properties_to_namespaced_properties(self.detector_properties_2d))
        properties.update(detector_3d_properties_to_namespaced_properties(self.detector_properties_3d))
        return properties

    def on_resolution_change(self, old_size, new_size):
        self.detector_properties_2d["pupil_size_max"] *= new_size[0] / old_size[0]
        self.detector_properties_3d["pupil_size_min"] *= new_size[0] / old_size[0]


def _upgade_legacy_namespaced_properties(namespaced_properties: dict) -> dict:
    legacy_2d_properties = namespaced_properties.get("2D_Settings", None)
    legacy_3d_properties = namespaced_properties.get("3D_Settings", None)

    # If the new properties are missing, but there are legacy properties - update
    if DETECTOR_2D_PROPERTIES_NAMESPACE not in namespaced_properties and legacy_2d_properties:
        namespaced_properties.update(detector_2d_properties_to_namespaced_properties(legacy_2d_properties))

    # If the new properties are missing, but there are legacy properties - update
    if DETECTOR_3D_PROPERTIES_NAMESPACE not in namespaced_properties and legacy_3d_properties:
        namespaced_properties.update(detector_3d_properties_to_namespaced_properties(legacy_3d_properties))

    return namespaced_properties
