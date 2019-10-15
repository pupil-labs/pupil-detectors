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

from ..coarse_pupil cimport center_surround
from ..detector cimport *
from ..cutils cimport *

from ..detector_base cimport TemporalDetectorBase
from ..detector_2d.detector_2d cimport Detector2DCore
from ..utils import Roi


cdef class Detector3DCore(TemporalDetectorBase):

    # Python-space properties
    cdef readonly object debug_result

    # Cython-space properties
    cdef dict properties
    cdef Detector2DCore detector2D
    cdef EyeModelFitter *detector3DPtr

    def __cinit__(self, *args, **kwargs):
        focal_length = 620.
        self.detector3DPtr = new EyeModelFitter(focal_length)
        
    def __dealloc__(self):
        del self.detector3DPtr

    def __init__(self, properties=None):
        self.detector2D = Detector2DCore(properties)
        if properties is None:
            # Overwrite default 2D detector properties
            overwrite_2d = {
                "2d": {
                    "strong_perimeter_ratio_range_min": 0.8,
                    "strong_area_ratio_range_min": 0.6,
                    "ellipse_roundness_ratio": 0.1,
                    "initial_ellipse_fit_treshhold": 1.8,
                    "final_perimeter_ratio_range_min": 0.6,
                    "final_perimeter_ratio_range_max": 1.2,
                    "ellipse_true_support_min_dist": 2.5,
                }
            }
            self.detector2D.update_properties(overwrite_2d)

        # initialize with defaults first and then set_properties to use type checking
        self.properties = self.get_default_properties()
        if properties is not None:
            self.update_properties(properties)
        
        # Never freeze model in the beginning to allow initial model fitting.
        self.update_properties({"3d": {"model_is_frozen": False}})

    @staticmethod
    def get_default_properties():
        return {
            "model_is_frozen": False,
            "model_sensitivity": 0.997
        }

    

    ##### Public API

    def focal_length(self):
        return self.detector3DPtr.getFocalLength()

    def reset_model(self):
        self.detector3DPtr.reset()

    # Base interface

    def get_property_namespaces(self):
        return ["2d", "3d"]

    def get_properties(self):
        all_properties = self.detector2D.get_properties()
        all_properties["3d"] = self.properties
        return all_properties

    def update_properties(self, properties):
        self.detector2D.update_properties(properties)
        relevant_properties = properties.get("3d", {})
        for key, value in relevant_properties.items():
            if key not in self.properties:
                continue
            expected_type = type(self.properties[key])
            if type(value) != expected_type:
                raise ValueError(
                    f"Property value {repr(value)} "
                    f"does not match expected type: {expected_type}"
                )
            self.properties[key] = value


    ##### Core API
    def detect(
        self,
        gray_img: np.ndarray,
        timestamp: float,
        color_img: T.Optional[np.ndarray]=None,
        roi: T.Optional[Roi]=None,
        debug=False,
        **kwargs
    ) -> T.Dict[str, T.Any]:
        
        cpp2DResultPtr = self.detector2D.c_detect(gray_img, color_img, roi)

        # timestamp doesn't get set elsewhere and it is needed in detector3D
        deref(cpp2DResultPtr).timestamp = timestamp

        cpp3DResult  = self.detector3DPtr.updateAndDetect(cpp2DResultPtr, self.properties, debug)

        height, width = gray_img.shape
        pyResult = self.convertTo3DPythonResult(cpp3DResult, timestamp, width, height)

        if debug:
            self.debug_result = self.prepareForVisualization3D(cpp3DResult)

        return pyResult


    cdef convertTo3DPythonResult(self, Detector3DResult& result, timestamp, width, height):
        #use negative z-coordinates to get from left-handed to right-handed coordinate system
        py_result = {}

        circle = {}
        circle['center'] =  (result.circle.center[0],-result.circle.center[1], result.circle.center[2])
        circle['normal'] =  (result.circle.normal[0],-result.circle.normal[1], result.circle.normal[2])
        circle['radius'] =  result.circle.radius
        py_result['circle_3d'] = circle


        py_result['confidence'] = result.confidence
        py_result['timestamp'] = timestamp
        py_result['diameter_3d'] = result.circle.radius * 2.0

        ellipse = {}
        ellipse['center'] = (result.ellipse.center[0] + width / 2.0 ,height / 2.0  -  result.ellipse.center[1])
        ellipse['axes'] =  (result.ellipse.minor_radius * 2.0 ,result.ellipse.major_radius * 2.0)
        ellipse['angle'] = - (result.ellipse.angle * 180.0 / PI - 90.0)
        py_result['ellipse'] = ellipse
        # norm_center = normalize( ellipse['center'] , (width, height),flip_y=True)
        # py_result['norm_pos'] = norm_center
        py_result["location"] = ellipse['center']

        py_result['diameter'] = max(ellipse['axes'])

        sphere = {}
        sphere['center'] =  (result.sphere.center[0],-result.sphere.center[1], result.sphere.center[2])
        sphere['radius'] =  result.sphere.radius
        py_result['sphere'] = sphere

        if str(result.projectedSphere.center[0]) == 'nan':
            projectedSphere = {'axes': (0.,0.), 'angle': 90.0, 'center': (0.,0.)}
        else:
            projectedSphere = {}
            projectedSphere['center'] = (result.projectedSphere.center[0] + width / 2.0 ,height / 2.0  -  result.projectedSphere.center[1])
            projectedSphere['axes'] =  (result.projectedSphere.minor_radius * 2.0 ,result.projectedSphere.major_radius * 2.0)
            #TODO result.projectedSphere.angle is always 0
            projectedSphere['angle'] = - (result.projectedSphere.angle * 180.0 / PI - 90.0)
        py_result['projected_sphere'] = projectedSphere

        py_result['model_confidence'] = result.modelConfidence
        py_result['model_id'] = result.modelID
        py_result['model_birth_timestamp'] = result.modelBirthTimestamp


        coords = cart2sph(result.circle.normal)
        if str(coords[0]) == 'nan':
            py_result['theta'] = 0.0
            py_result['phi'] = 0.0
        else:
            py_result['theta'] = coords[0]
            py_result['phi'] = coords[1]
        py_result['method'] = '3d c++'

        return py_result


    cdef prepareForVisualization3D(self, Detector3DResult& result):

        py_visualizationResult = {}

        py_visualizationResult['edges'] = getEdges(result)
        py_visualizationResult['circle'] = getCircle(result)
        py_visualizationResult['predicted_circle'] = getPredictedCircle(result)

        models = []
        for model in result.models:
            props = {}
            props['bin_positions'] = getBinPositions(model)
            props['sphere'] = getSphere(model)
            props['initial_sphere'] = getInitialSphere(model)
            props['maturity'] = model.maturity
            props['solver_fit'] = model.solverFit
            props['confidence'] = model.confidence
            props['performance'] = model.performance
            props['performance_gradient'] = model.performanceGradient
            props['model_id'] = model.modelID
            props['birth_timestamp'] = model.birthTimestamp
            models.append(props)

        py_visualizationResult['models'] = models

        return py_visualizationResult