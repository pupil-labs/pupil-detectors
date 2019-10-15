# %% imports
from pprint import pprint

import cv2
import matplotlib.pyplot as plt
import numpy as np

import pupil_detectors
from pupil_detectors.utils import Roi

# %% Create detector, print all properties
a = pupil_detectors.Detector2D({})
pprint(a.get_all_properties())

# %% load and display input img
img = cv2.imread("pupil.png")
plt.imshow(img)

# %% convert to gray image
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
plt.imshow(gray, cmap=plt.cm.gray)


# %% detect pupil
roi = Roi(gray.shape)
roi.set((50, 50, 150, 150))
results = a.detect(gray, color_img=img, user_roi=roi)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
print(results)
plt.imshow(img_rgb)


#%%
