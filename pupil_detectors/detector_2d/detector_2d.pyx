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

from pupil_detectors.detector cimport *
from pupil_detectors.coarse_pupil cimport center_surround

from .. cimport cutils
from ..utils import Roi, normalize
from ..detector_base cimport DetectorBase

cdef class Detector2DCore(DetectorBase):

    # Python-space properties
    cdef readonly dict properties
    cdef unsigned char[:,:,:] debug_image

    # Cython-space properties
    cdef Detector2D* thisptr
    cdef int coarseDetectionPreviousWidth
    cdef object coarseDetectionPreviousPosition

    def __cinit__(self, *args, **kwargs):
        self.thisptr = new Detector2D()

    def __dealloc__(self):
        del self.thisptr

    def __init__(self, properties = None):
        self.coarseDetectionPreviousWidth = -1
        self.coarseDetectionPreviousPosition =  (0,0)

        # initialize with defaults first and then set_properties to use type checking
        self.properties = self.get_default_properties()
        if properties is not None:
            self.set_properties('2d', properties)

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
            "strong_perimeter_ratio_range_min": 0.6,
            "strong_perimeter_ratio_range_max": 1.1,
            "strong_area_ratio_range_min": 0.8,
            "strong_area_ratio_range_max": 1.1,
            "contour_size_min": 5,
            "ellipse_roundness_ratio": 0.09,
            "initial_ellipse_fit_treshhold": 4.3,
            "final_perimeter_ratio_range_min": 0.5,
            "final_perimeter_ratio_range_max": 1.0,
            "ellipse_true_support_min_dist": 3.0,
            "support_pixel_ratio_exponent": 2.0,
        }

    # Base interface
    
    def get_property_namespaces(self) -> T.Iterable[str]:
        return ["2d"]

    def get_properties(self, namespace: str) -> T.Dict[str, T.Any]:
        if namespace != "2d":
            raise ValueError(f"Unsupported property namespace: {namespace}")
        return self.properties

    def set_properties(self, namespace: str, properties: T.Dict[str, T.Any]) -> None:
        if namespace != "2d":
            raise ValueError(f"Unsupported property namespace: {namespace}")
        for key, value in properties:
            if key not in self.properties:
                raise KeyError(f"No property with name '{key}' found!")
            expected_type = type(self.properties[key])
            if type(value) != expected_type:
                raise ValueError(
                    f"Property value {repr(value)} "
                    f"does not match expected type: {expected_type}"
                )
        self.properties.update(properties)

    def detect(
        self,
        gray_img: np.ndarray,
        color_img: T.Optional[np.ndarray]=None,
        user_roi: T.Optional[Roi]=None,
        **kwargs
    ) -> T.Dict[str, T.Any]:

        image_width = gray_img.shape[1]
        image_height = gray_img.shape[0]

        # TODO: remove img_color and img
        cdef unsigned char[:,::1] img = gray_img
        cdef Mat frame_image = Mat(image_height, image_width, CV_8UC1, <void *> &img[0,0])

        cdef unsigned char[:,:,:] img_color
        cdef Mat frameColor
        cdef Mat debug_image

        should_visualize = False if color_img is None else True

        if should_visualize:
            img_color = color_img
            frameColor = Mat(image_height, image_width, CV_8UC3, <void *> &img_color[0,0,0])
        
        if user_roi is None:
            user_roi = Roi(gray_img.shape)

        roi = Roi((0,0))
        roi.set( user_roi.get() )
        roi_x = roi.get()[0]
        roi_y = roi.get()[1]
        roi_width  = roi.get()[2] - roi.get()[0]
        roi_height  = roi.get()[3] - roi.get()[1]
        cdef int[:,::1] integral

        if self.properties['coarse_detection'] and roi_width*roi_height > 320*240:
            print("Using coarse detection!")
            scale = 2 # half the integral image. boost up integral
            # TODO maybe implement our own Integral so we don't have to half the image
            user_roi_image = gray_img[user_roi.view]
            integral = cv2.integral(user_roi_image[::scale,::scale])
            coarse_filter_max = self.properties['coarse_filter_max']
            coarse_filter_min = self.properties['coarse_filter_min']
            bounding_box , good_ones , bad_ones = center_surround( integral, coarse_filter_min/scale , coarse_filter_max/scale )

            if should_visualize:
                # # draw the candidates
                for v  in good_ones:
                    p_x,p_y,w,response = v
                    x = p_x * scale + roi_x
                    y = p_y * scale + roi_y
                    width = w*scale
                    cv2.rectangle( color_img , (x,y) , (x+width , y+width) , (255,255,0)  )

            x1 , y1 , x2, y2 = bounding_box
            width = x2 - x1
            height = y2 - y1
            roi_x = x1 * scale + roi_x
            roi_y = y1 * scale + roi_y
            roi_width = width*scale
            roi_height = height*scale
            roi.set((roi_x, roi_y, roi_x+roi_width, roi_y+roi_height))


        # every coordinates in the result are relative to the current ROI
        cppResultPtr =  self.thisptr.detect(
            self.properties,
            frame_image,
            frameColor,
            debug_image,
            Rect_[int](roi_x,roi_y,roi_width,roi_height),
            should_visualize,
            False
        )

        py_result = cutils.convertTo2DPythonResult(deref(cppResultPtr), image_width, image_height)

        return py_result
