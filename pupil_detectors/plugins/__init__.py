from .plugin_registry import PupilDetectorPluginRegistry

from .detector_base_plugin import PupilDetectorPlugin
from .detector_dummy_plugin import DetectorDummyPlugin
from .detector_2d_plugin import Detector2DPlugin
from .detector_3d_plugin import Detector3DPlugin


PupilDetectorPluginRegistry.shared_registry().register(plugin_label="disabled", plugin_class=DetectorDummyPlugin)
PupilDetectorPluginRegistry.shared_registry().register(plugin_label="C++ 2d detector", plugin_class=Detector2DPlugin)
PupilDetectorPluginRegistry.shared_registry().register(plugin_label="C++ 3d detector", plugin_class=Detector3DPlugin)
