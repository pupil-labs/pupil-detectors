# %%
import pupil_detectors
import numpy as np
import imageio
import matplotlib.pyplot as plt
from pupil_detectors.utils import Roi


# %%
a = pupil_detectors.Detector2D({})
a.get_all_properties()

# %%
img = imageio.imread("pupil.png").astype(np.uint8)
plt.imshow(img)

#%%
def rgb2gray(rgb):

    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray


gray = rgb2gray(img).astype(np.uint8)
plt.imshow(gray, cmap=plt.cm.gray)


#%%

roi = Roi(img.shape)
roi.set((100, 100, 200, 200))
results = a.detect(gray.astype(np.uint8), color_img=img, user_roi=roi)
print(results)
plt.imshow(img)


#%%
