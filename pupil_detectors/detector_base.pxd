import numpy as np
cimport numpy as np

cdef class DetectorBase:

    cpdef object detect(
        self,
        np.ndarray gray_img,
        double timestamp,
        np.ndarray color_img=*
    )
    """
    Detect pupil in image.
    
    Parameters:
        gray_img: read-only input image for detection (gray values)
        timestamp: timestamp of the image for temporal inference
        color_img: optional image for writing debug information

    Returns Python dict with minimal keys:
        "confidence"
        "norm_pos"
        "timestamp"
    """
    