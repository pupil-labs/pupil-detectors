"""
(*)~---------------------------------------------------------------------------
Pupil - eye tracking platform
Copyright (C) 2012-2019 Pupil Labs

Distributed under the terms of the GNU
Lesser General Public License (LGPL v3.0).
See COPYING and COPYING.LESSER for license details.
---------------------------------------------------------------------------~(*)
"""

from libcpp.memory cimport shared_ptr
from libcpp.vector cimport vector


cdef extern from '<opencv2/core.hpp>':

  int CV_8UC1
  int CV_8UC3


cdef extern from '<opencv2/core.hpp>' namespace 'cv':

  cdef cppclass Mat :
      Mat() except +
      Mat( int height, int width, int type, void* data  ) except+
      Mat( int height, int width, int type ) except+

  cdef cppclass Rect_[T]:
    Rect_() except +
    Rect_( T x, T y, T width, T height ) except +
    T x, y, width, height

  cdef cppclass Point_[T]:
    Point_() except +


cdef extern from '<Eigen/Eigen>' namespace 'Eigen':

    cdef cppclass Matrix21d "Eigen::Matrix<double,2,1>": # eigen defaults to column major layout
        Matrix21d() except +
        double& operator[](size_t)


cdef extern from 'common/types.h':

    cdef cppclass Ellipse2D[T]:
        Ellipse2D()
        Ellipse2D(T x, T y, T major_radius, T minor_radius, T angle) except +
        Matrix21d center
        T major_radius
        T minor_radius
        T angle

    # typdefs
    ctypedef Matrix21d Vector2
    ctypedef vector[Point_[int]] Edges2D
    ctypedef Ellipse2D[double] Ellipse

    cdef struct Detector2DResult:
        double confidence
        Ellipse ellipse
        Edges2D final_edges
        Edges2D raw_edges
        Rect_[int] current_roi
        double timestamp
        int image_width
        int image_height

    cdef struct Detector2DProperties:
        int intensity_range
        int blur_size
        float canny_treshold
        float canny_ration
        int canny_aperture
        int pupil_size_max
        int pupil_size_min
        float strong_perimeter_ratio_range_min
        float strong_perimeter_ratio_range_max
        float strong_area_ratio_range_min
        float strong_area_ratio_range_max
        int contour_size_min
        float ellipse_roundness_ratio
        float initial_ellipse_fit_treshhold
        float final_perimeter_ratio_range_min
        float final_perimeter_ratio_range_max
        float ellipse_true_support_min_dist
        float support_pixel_ratio_exponent

cdef extern from 'detect_2d.hpp':

  cdef cppclass Detector2D:
    Detector2D() except +
    shared_ptr[Detector2DResult] detect( Detector2DProperties& prop, Mat& image, Mat& color_image, Mat& debug_image, Rect_[int]& roi, bint visualize , bint use_debug_image )
