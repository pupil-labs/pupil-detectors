# cython: profile=False, language_level=3
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

import cv2
import numpy as np

from cython.operator cimport dereference as deref
from libcpp.memory cimport shared_ptr
from numpy.math cimport PI

from ..c_types_wrapper cimport (
    CV_8UC1,
    CV_8UC3,
    Detector2D,
    Detector2DResult,
    Mat,
    Rect_,
)
from ..coarse_pupil cimport center_surround
from ..detector_base cimport DetectorBase

from ..roi import Roi


cdef class Detector2DCore(DetectorBase):

    def __cinit__(self, *args, **kwargs):
        self.thisptr = new Detector2D()

    def __dealloc__(self):
        del self.thisptr

    def __init__(self, properties = None):
        # initialize with defaults first and then update
        self.properties = self.get_default_properties()
        if properties is not None:
            self.update_properties(properties)

    @staticmethod
    def get_default_properties():
        return {
            "coarse_detection": True,
            "coarse_filter_min": 128,
            "coarse_filter_max": 280,
            "intensity_range": 23,
            "blur_size": 5,
            "canny_treshold": 160,
            "canny_ration": 2,
            "canny_aperture": 5,
            "pupil_size_max": 100,
            "pupil_size_min": 10,
            "strong_perimeter_ratio_range_min": 0.8,
            "strong_perimeter_ratio_range_max": 1.1,
            "strong_area_ratio_range_min": 0.6,
            "strong_area_ratio_range_max": 1.1,
            "contour_size_min": 5,
            "ellipse_roundness_ratio": 0.1,
            "initial_ellipse_fit_treshhold": 1.8,
            "final_perimeter_ratio_range_min": 0.6,
            "final_perimeter_ratio_range_max": 1.2,
            "ellipse_true_support_min_dist": 2.5,
            "support_pixel_ratio_exponent": 2.0,
        }

    # Base interface

    def get_properties(self):
        return self.properties.copy()

    def update_properties(self, properties):
        for key, value in properties.items():
            if key not in self.properties:
                continue
            expected_type = type(self.properties[key])
            try:
                self.properties[key] = expected_type(value)
            except ValueError as e:
                raise ValueError(
                    f"Value `{repr(value)}` for key `{key}`"
                    f" could not be converted to expected type: {expected_type}"
                ) from e

    def detect(
        self,
        gray_img: np.ndarray,
        color_img: T.Optional[np.ndarray]=None,
        roi: T.Optional[Roi]=None,
        **kwargs
    ) -> T.Dict[str, T.Any]:
        """Detect pupil location in input image.

        Parameters:
            gray_img: input image as 2D numpy array (grayscale)
            color_img (optional): 3D numpy array (BGR)
                will be used to display debug visualizations
            roi (optional): Roi mask for gray_img to speed up detection

        Returns:
            Dictionary with information about the pupil. Keys:
                location (float, float): location of the pupil in image space
                confidence (float): confidence of the algorithm in [0, 1]
                diameter (float): max diameter of the pupil
                ellipse (dict): exact ellipse parameters of the pupil
        """
        cppResultPtr = self.c_detect(gray_img, color_img, roi)
        result = deref(cppResultPtr)

        result_dict = result2D_to_dict(result)
        return result_dict


    cdef shared_ptr[Detector2DResult] c_detect(
        self,
        gray_img: np.ndarray,
        color_img: T.Optional[np.ndarray]=None,
        roi: T.Optional[Roi]=None,
    ):
        image_height, image_width = gray_img.shape

        # cython memory views for accessing the raw data (does not copy)
        # NOTE: [:, ::1] marks the view as c-contiguous
        cdef unsigned char[:, ::1] gray_img_data = gray_img
        cdef unsigned char[:, :, ::1] color_img_data

        cdef Mat frame_image = Mat(image_height, image_width, CV_8UC1, <void *> &gray_img_data[0, 0])
        cdef Mat frameColor

        # not used, but needed for c++ API
        cdef Mat debug_image

        should_visualize = False if color_img is None else True

        if should_visualize:
            color_img_data = color_img
            frameColor = Mat(image_height, image_width, CV_8UC3, <void *> &color_img_data[0, 0, 0])

        if roi is None:
            roi = Roi.from_rect(0, 0, image_width, image_height)

        cdef int[:, ::1] integral

        if self.properties['coarse_detection'] and roi.width * roi.height > 320 * 240:
            scale = 2 # half the integral image. boost up integral
            # TODO maybe implement our own Integral so we don't have to half the image
            user_roi_image = gray_img[roi.slices]
            integral = cv2.integral(user_roi_image[::scale,::scale])
            coarse_filter_max = self.properties['coarse_filter_max']
            coarse_filter_min = self.properties['coarse_filter_min']
            bounding_box, good_ones, bad_ones = center_surround(
                integral,
                coarse_filter_min / scale,
                coarse_filter_max / scale
            )

            if should_visualize:
                # # draw the candidates
                for v in good_ones:
                    p_x, p_y, w, response = v
                    x = p_x * scale + roi.x_min
                    y = p_y * scale + roi.y_min
                    width = w*scale
                    cv2.rectangle(
                        color_img,
                        (x, y),
                        (x + width, y + width),
                        (255, 255, 0)
                    )

            x1, y1, x2, y2 = bounding_box
            width = x2 - x1
            height = y2 - y1
            roi = Roi.from_rect(
                x=x1 * scale + roi.x_min,
                y=y1 * scale + roi.y_min,
                width=width * scale,
                height=height * scale
            )

        # every coordinates in the result are relative to the current ROI
        cppResultPtr = self.thisptr.detect(
            self.properties,
            frame_image,
            frameColor,
            debug_image,
            Rect_[int](roi.x_min, roi.y_min, roi.width, roi.height),
            should_visualize,
            False
        )

        return cppResultPtr


cdef object result2D_to_dict(Detector2DResult& result):
    data = {}
    data["ellipse"] = {
        "center": (result.ellipse.center[0], result.ellipse.center[1]),
        "axes": (result.ellipse.minor_radius * 2.0, result.ellipse.major_radius * 2.0),
        "angle": result.ellipse.angle * 180.0 / PI - 90.0
    }
    data["diameter"] = max(data["ellipse"]["axes"])
    data["location"] = data["ellipse"]["center"]
    data["confidence"] = result.confidence
    return data
