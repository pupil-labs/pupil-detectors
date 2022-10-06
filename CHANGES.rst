2.0.2 (2022-10-06)
##################

- Update project structure and build wheels with cibuildwheel

2.0.1 (2020-12-03)
##################

Removed all remaining Ceres references. Eigen3 remains a dependency.

2.0.0 (2020-12-02)
##################

Removed Detector3D - `#17 <https://github.com/pupil-labs/pupil-detectors/pull/17>`__
************************************************************************************

In favor of our new `pye3d detector <https://github.com/pupil-labs/pye3d-detector/>`__,
we have removed the previous ``Detector3D`` class. This allows us to remove Ceres as a
dependency and to cleanup the detector class interface.

Specifically, getting and setting properties has been simplified by removing property
namespaces.

.. code-block:: diff

    - NamespacedProperties = T.Dict[str, T.Dict[str, T.Any]]
    + DetectorProperties = T.Dict[str, T.Any]

    - def get_property_namespaces(self) -> T.Iterable[str]

    - def get_properties(self) -> NamespacedProperties:
    + def get_properties(self) -> DetectorProperties:

    - def update_properties(self, properties: NamespacedProperties) -> None
    + def update_properties(self, properties: DetectorProperties) -> None


The ``Roi`` class has been moved from ``pupil_detectors.utils`` to ``pupil_detectors.roi``.

1.1.1 (2020-08-26)
##################

Improvements
************
- Added default lookup paths for OpenCV on Ubuntu 20.04, enabling building from source out of the box there.
- Added parameter to specify the focal length of the camera supplying the eye images for a more accurate 3D model.

1.1.0 (2020-05-04)
##################

Changed
*******
- Changed the default 2D detector properties to be the same as the default overrides that the 3D detector applies.

1.0.5 (2020-04-20)
##################
Added
*****
- Added option to run 3D detector without internal 2D detector, but from serialized data of external 2D detector

1.0.4 (2020-01-13)
##################
Fixed
*****
- Fixed crash when installing from source distribution package

1.0.3 (2020-01-07)
##################
Fixed
*****
- Wrong ``Roi.rect()`` computation.

1.0.2 (2019-12-03)
##################
- Initial release.
