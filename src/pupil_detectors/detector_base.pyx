import typing as T

import numpy as np

NamespacedProperties = T.Dict[str, T.Dict[str, T.Any]]

cdef class DetectorBase:
    """Base interface for pupil detectors."""

    # abstract interface

    def __init__(self, properties:T.Optional[NamespacedProperties]=None):
        """Construct a new detector.
        
        Parameters:
            properties (optional): dicts of properties, grouped by namespaces
        """
        raise NotImplementedError()

    def detect(self, gray_img: np.nparray, **kwargs) -> T.Dict[str, T.Any]:
        """Detect pupil location in input image.
        
        Parameters:
            gray_img: input image as 2D numpy array (grayscale)

        Returns:
            Dictionary with information about the pupil.
            Minimum required keys are:
                location (float, float): location of the pupil in image space
                confidence (float): confidence of the algorithm in [0, 1]
            More keys can be added for custom functionality when subclassing.
        """
        raise NotImplementedError()
    
    def get_property_namespaces(self) -> T.Iterable[str]:
        """Returns a list of property namespaces that the detector supports."""
        raise NotImplementedError()

    def get_properties(self) -> NamespacedProperties:
        """Returns a copy of the properties and values of the detector."""
        raise NotImplementedError()

    def update_properties(self, properties: NamespacedProperties) -> None:
        """Update existing properties of the detector."""
        raise NotImplementedError()


cdef class TemporalDetectorBase(DetectorBase):
    """Base interface for pupil detectors that work on temporal data."""

    def detect(
        self,
        gray_img: np.nparray,
        timestamp: float,
        **kwargs
    ) -> T.Dict[str, T.Any]:
        """Detect pupil location in input image.
        
        Parameters:
            gray_img: input image as 2D numpy array (grayscale)
            timestamp: timing information for correlating sequential images

        Returns:
            Dictionary with information about the pupil.
            Minimum required keys are:
                location (float, float): location of the pupil in image space
                confidence (float): confidence of the algorithm in [0, 1]
                timestamp (float): the timestamp of the input
            More keys can be added for custom functionality when subclassing.
        """
        raise NotImplementedError()
