"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

import typing as T

import numpy as np

DetectorProperties = T.Dict[str, T.Any]

cdef class DetectorBase:
    """Base interface for pupil detectors."""

    # abstract interface

    def __init__(self, properties:T.Optional[DetectorProperties]=None):
        """Construct a new detector.

        Parameters:
            properties (optional): dict of property names and values
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

    def get_properties(self) -> DetectorProperties:
        """Returns a copy of the properties and values of the detector."""
        raise NotImplementedError()

    def update_properties(self, properties: DetectorProperties) -> None:
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
