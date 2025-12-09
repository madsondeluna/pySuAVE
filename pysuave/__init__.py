"""
pySuAVE - Surface Assessment Via grid Evaluation

Python implementation of the SuAVE software for analyzing curvature-dependent
properties in chemical interfaces.

Original Fortran code by Denys E. S. Santos
Python migration: 2025

Citation:
    Santos, D. E. S., Coutinho, K., & Soares, T. A. (2022).
    Surface Assessment via Grid Evaluation (SuAVE) for Every Surface Curvature
    and Cavity Shape. J. Chem. Inf. Model., 62, 4690-4701.
    https://doi.org/10.1021/acs.jcim.2c00673
"""

__version__ = "0.1.0"
__author__ = "Denys E. S. Santos"
__email__ = "suave.biomat@gmail.com"

from pysuave.core.types import AtomData, Coordinate3D, SphericalCoordinate

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "AtomData",
    "Coordinate3D",
    "SphericalCoordinate",
]
