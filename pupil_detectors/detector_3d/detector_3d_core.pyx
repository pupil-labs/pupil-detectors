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
from cython.operator cimport dereference as deref

from pupil_detectors.coarse_pupil cimport center_surround
from pupil_detectors.detector cimport *
from pupil_detectors.detector_utils cimport *

from methods import Roi, normalize


cdef class Detector3DCore:

    # Python-space properties
    cdef readonly dict detectProperties2D, detectProperties3D #TODO: Rename to detector_properties_2d and detector_properties_3d
    cdef readonly object pyResult3D #TODO: Rename to debug_result_3d

    # Cython-space properties
    cdef Detector2D* detector2DPtr
    cdef EyeModelFitter *detector3DPtr

    def __cinit__(self, *args, **kwargs):
        self.detector2DPtr = new Detector2D()
        focal_length = 620.
        '''
        K for 30hz eye cam:
        [ 634.16873016    0.          343.40537637]
        [   0.          605.57862234  252.3924477 ]
        [   0.            0.            1.        ]
        '''
        #region_band_width = 5
        #region_step_epsilon = 0.5
        self.detector3DPtr = new EyeModelFitter(focal_length)

    def __init__(self, detector_properties_2d, detector_properties_3d):

        # Overwrite default 2D detector properties
        self.detectProperties2D = {}
        self.detectProperties2D["strong_perimeter_ratio_range_min"] = 0.8
        self.detectProperties2D["strong_area_ratio_range_min"] = 0.6
        self.detectProperties2D["ellipse_roundness_ratio"] = 0.1
        self.detectProperties2D["initial_ellipse_fit_treshhold"] = 1.8
        self.detectProperties2D["final_perimeter_ratio_range_min"] = 0.6
        self.detectProperties2D["final_perimeter_ratio_range_max"] = 1.2
        self.detectProperties2D["ellipse_true_support_min_dist"] = 2.5
        self.detectProperties2D.update(detector_properties_2d)

        # Overwrite default 3D detector properties
        self.detectProperties3D = {}
        # Never freeze model in the beginning to allow initial model fitting.
        self.detectProperties3D["model_is_frozen"] = False
        self.detectProperties3D.update(detector_properties_3d)

    def __dealloc__(self):
      del self.detector2DPtr
      del self.detector3DPtr

    ##### Public API

    def focal_length(self):
        return self.detector3DPtr.getFocalLength()

    def reset_model(self):
        self.detector3DPtr.reset()

    ##### Legacy API

    def set_2d_detector_property(self, name, value):
        set_detector_property(self.detectProperties2D, name, value)

    def set_3d_detector_property(self, name, value):
        set_detector_property(self.detectProperties3D, name, value)

    ##### Core API

    def detect(self, frame, user_roi, visualize, pause_video = False, is_debugging_enabled = False, **kwargs):
        image_width = frame.width
        image_height = frame.height

        cdef unsigned char[:,::1] img = frame.gray
        cdef Mat cv_image = Mat(image_height, image_width, CV_8UC1, <void *> &img[0,0] )

        cdef unsigned char[:,:,:] img_color
        cdef Mat cv_image_color
        cdef Mat debug_image

        if visualize:
            img_color = frame.img
            cv_image_color = Mat(image_height, image_width, CV_8UC3, <void *> &img_color[0,0,0] )

        roi = Roi((0,0))
        roi.set( user_roi.get() )
        roi_x = roi.get()[0]
        roi_y = roi.get()[1]
        roi_width  = roi.get()[2] - roi.get()[0]
        roi_height  = roi.get()[3] - roi.get()[1]
        cdef int[:,::1] integral

        if self.detectProperties2D['coarse_detection'] and roi_width*roi_height > 320*240:
            scale = 2 # half the integral image. boost up integral
            # TODO maybe implement our own Integral so we don't have to half the image
            user_roi_image = frame.gray[user_roi.view]
            integral = cv2.integral(user_roi_image[::scale,::scale])
            coarse_filter_max = self.detectProperties2D['coarse_filter_max']
            coarse_filter_min = self.detectProperties2D['coarse_filter_min']
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
        cpp2DResultPtr =  self.detector2DPtr.detect(self.detectProperties2D, cv_image, cv_image_color, debug_image, Rect_[int](roi_x,roi_y,roi_width,roi_height), visualize , False ) #we don't use debug image in 3d model

        deref(cpp2DResultPtr).timestamp = frame.timestamp #timestamp doesn't get set elsewhere and it is needt in detector3D

        ######### 3D Model Part ############
        cdef Detector3DResult cpp3DResult  = self.detector3DPtr.updateAndDetect( cpp2DResultPtr , self.detectProperties3D, is_debugging_enabled)

        pyResult = convertTo3DPythonResult(cpp3DResult , frame )

        if is_debugging_enabled:
            self.pyResult3D = prepareForVisualization3D(cpp3DResult)

        return pyResult
