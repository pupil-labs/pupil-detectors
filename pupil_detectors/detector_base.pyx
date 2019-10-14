import typing as T

import numpy as np


cdef class DetectorBase:
    def detect(
            self,
            gray_img: np.nparray,
            **kwargs
        ) -> T.Dict[str, T.Any]:
        raise NotImplementedError()
    
    def get_property_namespaces(self) -> T.Iterable[str]:
        raise NotImplementedError()

    def get_properties(self, namespace: str) -> T.Dict[str, T.Any]:
        raise NotImplementedError()

    def set_properties(self, namespace: str, properties: T.Dict[str, T.Any]) -> None:
        raise NotImplementedError()


cdef class TemporalDetectorBase(DetectorBase):
    def detect(
        self,
        gray_img: np.nparray,
        timestamp: float,
        **kwargs
    ) -> T.Dict[str, T.Any]:
        raise NotImplementedError()
