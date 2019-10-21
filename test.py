# %% imports
from pprint import pprint

import cv2
import matplotlib.pyplot as plt
import numpy as np

import pupil_detectors
from pupil_detectors.utils import Roi

# %% Create detector, print all properties
a = pupil_detectors.Detector2D()
pprint(a.get_properties())

# %% Test property interface
a.update_properties({"2d": {"blur_size": 10}})
a.update_properties({"3d": {"blur_size": 10}})
a.update_properties({"2d": {"dummy": 42}})
pprint(a.get_properties())

try:
    a.update_properties({"2d": {"blur_size": 1.0}})
    assert False, "This should crash"
except ValueError as e:
    pprint(e)

props = a.get_properties()
a = pupil_detectors.Detector2D(props)
pprint(a.get_properties())

a = pupil_detectors.Detector2D()

# %% load and display input img
img = cv2.imread("pupil.png")
plt.imshow(img)

# %% convert to gray image
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
plt.imshow(gray, cmap=plt.cm.gray)


# %% detect pupil
results = a.detect(gray)
el = results["ellipse"]
img_tmp = img.copy()
cv2.ellipse(
    img_tmp,
    center=tuple(int(v) for v in el["center"]),
    axes=tuple(int(v / 2) for v in el["axes"]),
    angle=int(el["angle"]),
    startAngle=0,
    endAngle=360,
    color=[0, 0, 255],
)
img_rgb = cv2.cvtColor(img_tmp, cv2.COLOR_BGR2RGB)
pprint(results)
plt.imshow(img_rgb)


# %% algorithm view and roi
roi = Roi(50, 50, 150, 150)
img_tmp = img.copy()
a.detect(gray, color_img=img_tmp, roi=roi)
img_rgb = cv2.cvtColor(img_tmp, cv2.COLOR_BGR2RGB)
plt.imshow(img_rgb)

# %% 3D detector

b = pupil_detectors.Detector3D()
pprint(b.get_properties())

# %% feed 10 images to 3D detector
for t in range(10):
    pprint(b.detect(gray, timestamp=t, debug=True))
    pprint(b.debug_result)
    pprint("==========================================================================")
