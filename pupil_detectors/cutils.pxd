"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

# cython: profile=False
from .c_types_wrapper cimport (
    ModelDebugProperties,
    Detector3DResult,
)

cdef inline getBinPositions( ModelDebugProperties& result ):
    if result.binPositions.size() == 0:
        return []
    positions = []
    eyePosition = result.sphere.center
    eyeRadius = result.sphere.radius
    #bins are on a unit sphere
    for point in result.binPositions:
        positions.append([point[0]*eyeRadius+eyePosition[0],point[1]*eyeRadius+eyePosition[1],point[2]*eyeRadius+eyePosition[2]])
    return positions


cdef inline getEdges( Detector3DResult& result ):
    if result.edges.size() == 0:
        return []
    edges = []
    for point in result.edges:
        edges.append([point[0],point[1],point[2]])
    return edges


cdef inline getCircle(const Detector3DResult& result):
    center = result.circle.center
    radius = result.circle.radius
    normal = result.circle.normal
    return [ [center[0],center[1],center[2]], [normal[0],normal[1],normal[2]], radius ]


cdef inline getPredictedCircle(const Detector3DResult& result):
    center = result.predictedCircle.center
    radius = result.predictedCircle.radius
    normal = result.predictedCircle.normal
    return [ [center[0],center[1],center[2]], [normal[0],normal[1],normal[2]], radius ]


cdef inline getSphere(const ModelDebugProperties& result ):
    sphere = result.sphere
    return [ [sphere.center[0],sphere.center[1],sphere.center[2]],sphere.radius]


cdef inline getInitialSphere(const ModelDebugProperties& result ):
    sphere = result.initialSphere
    return [ [sphere.center[0],sphere.center[1],sphere.center[2]],sphere.radius]


cdef inline set_detector_property(properties, name, value):
    if name not in properties:
        raise ValueError("No property with name `{}` found.".format(name))
    if not isinstance(value, type(properties[name])):
        raise TypeError("Value {} was not of expected type `{}` found."
                        .format(value, type(properties[name]).__name__))
    properties[name] = value
