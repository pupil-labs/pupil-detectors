.. image:: https://img.shields.io/pypi/v/pupil-detectors.svg
   :target: `PyPI link`_

.. image:: https://img.shields.io/pypi/pyversions/pupil-detectors.svg
   :target: `PyPI link`_

.. _PyPI link: https://pypi.org/project/pupil-detectors

.. image:: https://github.com/pupil-labs/pupil-detectors/workflows/tests/badge.svg
   :target: https://github.com/pupil-labs/pupil-detectors/actions?query=workflow%3A%22tests%22
   :alt: tests

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: Black

.. .. image:: https://readthedocs.org/projects/skeleton/badge/?version=latest
..    :target: https://skeleton.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/badge/skeleton-2022-informational
   :target: https://blog.jaraco.com/skeleton

***************
pupil-detectors
***************

This Python package contains the standalone 2D pupil detectors for the
`Pupil Core <https://github.com/pupil-labs/pupil/>`__ software stack.

Install via PyPI
################

.. code-block::

   pip install pupil-detectors


Usage
#####

Here's a quick example on how to detect and draw an ellipse.

.. code-block:: python

   import cv2
   from pupil_detectors import Detector2D

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


Developers
##########

Building from Source
********************

Installing the dependencies
===========================

- macOS: ``brew install eigen opencv``
- Windows: ``choco install eigen opencv``
- Ubuntu: ``apt-get install libeigen3-dev libeigen3-dev``

Building the Python package
===========================

.. code-block:: bash

   # Clone repository
   git clone git@github.com:pupil-labs/pupil-detectors.git
   cd pupil-detectors

   # Install from source
   pip install .
