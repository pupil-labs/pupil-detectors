# pupil-detectors

This is a python-package containing standalone pupil detectors for the [Pupil-Labs](https://pupil-labs.com/) software stack. It contains the following detectors:

- Detector2D
- Detector3D

## Installation

### macOS and Linux
This package has a couple of non-python dependencies that you will have to install yourself before you can install **pupil-detectors**. We are working on clean setup instructions, but until then you can just install all dependencies from the Pupil software stack. You can find installation guides [on the Pupil GitHub page (section: Installing Dependencies)](https://github.com/pupil-labs/pupil#installing-dependencies).

Then you can install **pupil-detectors** with pip:
```bash
pip install pupil-detectors
```

### Windows
Since the dependency setup is very complex on Windows, we provide prebuilt-wheels. This means you don't have to install any dependencies and can just install **pupil-detectors**:
```bash
pip install pupil-detectors
```
If you don't want to use our prebuilt versions, see the section **Building from Source** further below.


## Usage

Here's a quick example on how to detect and draw an ellipse.

```python
import cv2
from pupil_detectors import Detector2D, Detector3D

detector = Detector2D()

# read image as numpy array from somewhere, e.g. here from a file
img = cv2.imread("pupil.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

result = detector.detect(gray)
ellipse = result["ellipse"]

# draw the ellipse outline onto the input image
# note that cv2.ellipse() cannot deal with float values
# also it expects the axes to be semi-axes (half the size)
cv2.ellipse(
    img,
    tuple(int(v) for v in ellipse["center"]),
    tuple(int(v / 2) for v in ellipse["axes"]),
    ellipse["angle"],
    0, 360, # start/end angle for drawing
    (0, 0, 255) # color (BGR): red
)
cv2.imshow("Image", img)
cv2.waitKey(0)
```

## Developers

### Building from Source

You can install this package locally from source. Make sure you have all necessary dependencies setup (see Installation section above). 

**NOTE:** For Windows the dependency setup is quite complex. Until we have clean instructions, please follow the guide for [setting up Windows dependencies for Pupil](https://github.com/pupil-labs/pupil/blob/master/docs/dependencies-windows.md).

**NOTE:** When building the package on your own, you can experience severe performance differences when not having setup your dependencies correctly. Make sure to compare performance to prebuilt wheels or to bundled versions of [Pupil](https://github.com/pupil-labs/pupil).

```bash
# Clone repository
git clone git@github.com:pupil-labs/pupil-detectors.git
cd pupil-detectors

# Install from source with development extras
pip install ".[dev]"

# Run tests
pytest tests
```

## Maintainers

### Distribution

This project does not currently support automated distribution.
Steps for a new release:
1. Make sure the code works.
2. Run bumpversion (major/minor/patch). This will bump the version, create a new commit and a new tag! Git must be clean of modifications.
```
bumpversion minor
```

3. Push the new commit and (all) tags.
```
git push --tags
```

4. Build the source distribution and upload to PyPI.
```
python setup.py sdist
twine upload ./dist/*
```

5. Build wheels and upload to PyPi. Use the internal bundle-machines for Pupil for the correct dependency setup!
```
pip wheel --no-deps . -w dist
twine upload ./dist/*
```
