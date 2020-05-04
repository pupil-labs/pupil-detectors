# pupil-detectors

[![PyPI](https://img.shields.io/pypi/v/pupil-detectors)](https://pypi.org/project/pupil-detectors/)

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
2. Install dependencies
```
pip install bump2version twine
```

3. Create new tag with bump2version.
    - Decide on type of version bump: major/minor/patch
    - Make sure the working directory is clean! (`git status`)
    - Modify `CHANGELOG.md` to include newest version notes.
    - Stage changelog (don't commit):
    
        ```git add CHANGELOG.md```
    - Run the appropriate bump2version. This will create a new commit with all necessary changes (including the staged changelog) and a new tag!

        ```bash
        # ONLY ONE OF THOSE!
        bump2version major --allow-dirty
        # or
        bump2version minor --allow-dirty
        # or
        bump2version patch --allow-dirty
        ```

4. Push the new commit and (all) tags.
```
git push
git push --tags
```

5. Build the source distribution and wheel (Windows). Use the internal bundle-machine for Pupil for the correct dependency setup!
```
python setup.py sdist
pip wheel --no-deps . -w dist
```

6. Test installing from wheel and from sdist!

7. Upload wheel and sdist to PyPI.
```
twine upload ./dist/*
```
