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
import cv2
import numpy as np
from cython.operator cimport dereference as deref

from pupil_detectors.detector cimport *
from pupil_detectors.coarse_pupil cimport center_surround

from .. cimport cutils
from ..utils import Roi
from ..detector_base cimport DetectorBase

cdef class Detector2DCore(DetectorBase):

    # Python-space properties
    cdef readonly dict detector_properties_2d
    cdef unsigned char[:,:,:] debug_image

    # Cython-space properties
    cdef Detector2D* thisptr
    cdef int coarseDetectionPreviousWidth
    cdef object coarseDetectionPreviousPosition

    def __cinit__(self, *args, **kwargs):
        self.thisptr = new Detector2D()

    def __init__(self, detector_properties_2d):
        self.detector_properties_2d = detector_properties_2d
        self.coarseDetectionPreviousWidth = -1
        self.coarseDetectionPreviousPosition =  (0,0)

    def __dealloc__(self):
        del self.thisptr

    ##### Legacy API

    def set_2d_detector_property(self, name, value):
        cutils.set_detector_property(self.detector_properties_2d, name, value)

    ##### Core API

    def detect(self, frame, user_roi, visualize, pause_video = False, use_debug_image = False):
        image_width = frame.width
        image_height = frame.height

        cdef unsigned char[:,::1] img = frame.gray
        cdef Mat frame_image = Mat(image_height, image_width, CV_8UC1, <void *> &img[0,0] )

        cdef unsigned char[:,:,:] img_color
        cdef Mat frameColor
        cdef Mat debug_image

        if visualize:
            img_color = frame.img
            frameColor = Mat(image_height, image_width, CV_8UC3, <void *> &img_color[0,0,0] )

        if use_debug_image:
            debug_image_array = np.zeros( (image_height, image_width, 3 ), dtype = np.uint8 ) #clear image every frame
            self.debug_image = debug_image_array
            debug_image = Mat(image_height, image_width, CV_8UC3, <void *> &self.debug_image[0,0,0] )

        roi = Roi((0,0))
        roi.set( user_roi.get() )
        roi_x = roi.get()[0]
        roi_y = roi.get()[1]
        roi_width  = roi.get()[2] - roi.get()[0]
        roi_height  = roi.get()[3] - roi.get()[1]
        cdef int[:,::1] integral

        if self.detector_properties_2d['coarse_detection'] and roi_width*roi_height > 320*240:
            scale = 2 # half the integral image. boost up integral
            # TODO maybe implement our own Integral so we don't have to half the image
            user_roi_image = frame.gray[user_roi.view]
            integral = cv2.integral(user_roi_image[::scale,::scale])
            coarse_filter_max = self.detector_properties_2d['coarse_filter_max']
            coarse_filter_min = self.detector_properties_2d['coarse_filter_min']
            bounding_box , good_ones , bad_ones = center_surround( integral, coarse_filter_min/scale , coarse_filter_max/scale )

            if visualize:
                # !! uncomment this to visualize coarse detection
                #  # draw the candidates
                # for v  in bad_ones:
                #     p_x,p_y,w,response = v
                #     x = p_x * scale + roi_x
                #     y = p_y * scale + roi_y
                #     width = w*scale
                #     cv2.rectangle( frame.img , (x,y) , (x+width , y+width) , (0,0,255)  )

                # # draw the candidates
                for v  in good_ones:
                    p_x,p_y,w,response = v
                    x = p_x * scale + roi_x
                    y = p_y * scale + roi_y
                    width = w*scale
                    cv2.rectangle( frame.img , (x,y) , (x+width , y+width) , (255,255,0)  )
                    #responseText = '{:2f}'.format(response)
                    #cv2.putText(frame.img, responseText,(int(x+width*0.5) , int(y+width*0.5)), cv2.FONT_HERSHEY_PLAIN,0.7,(0,0,255) , 1 )

                    #center = (int(x+width*0.5) , int(y+width*0.5))
                    #cv2.circle( frame.img , center , 5 , (255,0,255) , -1  )

            x1 , y1 , x2, y2 = bounding_box
            width = x2 - x1
            height = y2 - y1
            roi_x = x1 * scale + roi_x
            roi_y = y1 * scale + roi_y
            roi_width = width*scale
            roi_height = height*scale
            roi.set((roi_x, roi_y, roi_x+roi_width, roi_y+roi_height))


        # every coordinates in the result are relative to the current ROI
        cppResultPtr =  self.thisptr.detect(self.detector_properties_2d, frame_image, frameColor, debug_image, Rect_[int](roi_x,roi_y,roi_width,roi_height),  visualize , use_debug_image)

        py_result = cutils.convertTo2DPythonResult( deref(cppResultPtr), frame , roi )

        return py_result
