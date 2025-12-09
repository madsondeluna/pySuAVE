"""
Core data types for pySuAVE.

This module provides dataclasses that replace the Fortran TYPE definitions
from the original types.f90 module.

Fortran equivalents:
    - vet1 -> AtomData
    - vet2 -> Coordinate3D
    - vet3 -> SphericalCoordinate
"""

from dataclasses import dataclass
from typing import Optional
import numpy as np
import numpy.typing as npt


@dataclass
class AtomData:
    """
    Complete atomic data including coordinates and metadata.
    
    Fortran equivalent: type vet1
    
    Attributes:
        x, y, z: Cartesian coordinates (Å)
        n_atom: Atom number
        n_resid: Residue number
        atom: Atom name (e.g., 'CA', 'O', 'N')
        resid: Residue name (e.g., 'ALA', 'GLY')
        ident: Identifier/chain
        code: Additional code/label
    """
    x: float
    y: float
    z: float
    n_atom: int
    n_resid: int
    atom: str = ""
    resid: str = ""
    ident: str = ""
    code: str = ""
    
    def to_array(self) -> npt.NDArray[np.float64]:
        """Return coordinates as numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z], dtype=np.float64)
    
    @classmethod
    def from_array(
        cls,
        coords: npt.NDArray[np.float64],
        n_atom: int = 0,
        n_resid: int = 0,
        **kwargs
    ) -> "AtomData":
        """Create AtomData from coordinate array."""
        return cls(
            x=float(coords[0]),
            y=float(coords[1]),
            z=float(coords[2]),
            n_atom=n_atom,
            n_resid=n_resid,
            **kwargs
        )


@dataclass
class Coordinate3D:
    """
    Simple 3D Cartesian coordinate.
    
    Fortran equivalent: type vet2
    
    Attributes:
        x, y, z: Cartesian coordinates (Å)
    """
    x: float
    y: float
    z: float
    
    def to_array(self) -> npt.NDArray[np.float64]:
        """Return coordinates as numpy array [x, y, z]."""
        return np.array([self.x, self.y, self.z], dtype=np.float64)
    
    @classmethod
    def from_array(cls, coords: npt.NDArray[np.float64]) -> "Coordinate3D":
        """Create Coordinate3D from array."""
        return cls(x=float(coords[0]), y=float(coords[1]), z=float(coords[2]))
    
    def distance_to(self, other: "Coordinate3D") -> float:
        """Calculate Euclidean distance to another coordinate."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def __add__(self, other: "Coordinate3D") -> "Coordinate3D":
        """Vector addition."""
        return Coordinate3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: "Coordinate3D") -> "Coordinate3D":
        """Vector subtraction."""
        return Coordinate3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> "Coordinate3D":
        """Scalar multiplication."""
        return Coordinate3D(self.x * scalar, self.y * scalar, self.z * scalar)


@dataclass
class SphericalCoordinate:
    """
    Spherical coordinate system (ρ, φ, θ).
    
    Fortran equivalent: type vet3
    
    Attributes:
        rho: Radial distance (ρ)
        phi: Azimuthal angle (φ) in radians
        theta: Polar angle (θ) in radians
    """
    rho: float
    phi: float
    theta: float
    
    def to_array(self) -> npt.NDArray[np.float64]:
        """Return coordinates as numpy array [ρ, φ, θ]."""
        return np.array([self.rho, self.phi, self.theta], dtype=np.float64)
    
    @classmethod
    def from_array(cls, coords: npt.NDArray[np.float64]) -> "SphericalCoordinate":
        """Create SphericalCoordinate from array."""
        return cls(rho=float(coords[0]), phi=float(coords[1]), theta=float(coords[2]))
    
    def to_cartesian(self) -> Coordinate3D:
        """
        Convert spherical to Cartesian coordinates.
        
        Returns:
            Coordinate3D with (x, y, z) values
        """
        x = self.rho * np.sin(self.theta) * np.cos(self.phi)
        y = self.rho * np.sin(self.theta) * np.sin(self.phi)
        z = self.rho * np.cos(self.theta)
        return Coordinate3D(x=float(x), y=float(y), z=float(z))
    
    @classmethod
    def from_cartesian(cls, coord: Coordinate3D) -> "SphericalCoordinate":
        """
        Convert Cartesian to spherical coordinates.
        
        Args:
            coord: Cartesian coordinate
            
        Returns:
            SphericalCoordinate with (ρ, φ, θ) values
        """
        rho = np.sqrt(coord.x**2 + coord.y**2 + coord.z**2)
        
        if rho < 1e-10:
            # Handle origin case
            return cls(rho=0.0, phi=0.0, theta=0.0)
        
        theta = np.arccos(coord.z / rho)
        phi = np.arctan2(coord.y, coord.x)
        
        return cls(rho=float(rho), phi=float(phi), theta=float(theta))


# Type aliases for arrays of coordinates
AtomDataArray = list[AtomData]
Coordinate3DArray = list[Coordinate3D]
SphericalCoordinateArray = list[SphericalCoordinate]

# NumPy array type aliases
CoordinateArray = npt.NDArray[np.float64]  # Shape: (N, 3)
GridArray2D = npt.NDArray[np.float64]      # Shape: (M, N)
GridArray3D = npt.NDArray[np.float64]      # Shape: (M, N, 3)
