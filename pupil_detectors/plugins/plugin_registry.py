import collections
import typing as T


class PupilDetectorPluginRegistry:

    @staticmethod
    def shared_registry():
        return _shared_global_pupil_detector_registry

    def __init__(self):
        self._class_and_label_by_name = collections.OrderedDict()

    def registered_plugin_names(self) -> T.List[str]:
        return list(self._class_and_label_by_name.keys())

    def registered_plugin_classes(self) -> T.List[str]:
        return list(map(self.class_by_name, self.registered_plugin_names()))

    def registered_plugin_labels(self) -> T.List[str]:
        return list(map(self.label_by_name, self.registered_plugin_names()))

    def class_by_name(self, plugin_name: str):
        try:
            klass, _ = self._class_and_label_by_name[plugin_name]
            return klass
        except KeyError:
            raise self._unregistered_name_exception(plugin_name)

    def label_by_name(self, plugin_name: str):
        try:
            _, label = self._class_and_label_by_name[plugin_name]
            return label
        except KeyError:
            raise self._unregistered_name_exception(plugin_name)

    def register(self, plugin_label, plugin_class):
        plugin_name = self.name_from_class(plugin_class)
        if self._is_name_registered(plugin_name):
            raise ValueError(f"Plugin already registered for name \"{plugin_name}\"")
        self._class_and_label_by_name[plugin_name] = (plugin_class, plugin_label)

    @staticmethod
    def name_from_class(plugin_class):
        return plugin_class.__name__

    def _is_name_registered(self, plugin_name: str):
        return plugin_name in self.registered_plugin_names()
    
    def _unregistered_name_exception(self, plugin_name: str):
        return ValueError("Unregistered plugin name \"{plugin_name}\"")


_shared_global_pupil_detector_registry = PupilDetectorPluginRegistry()
