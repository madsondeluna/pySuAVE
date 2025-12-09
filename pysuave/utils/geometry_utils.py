"""
Solid angle and geometric utility functions for pySuAVE.

This module provides functions for calculating solid angles and other
geometric utilities needed for spherical surface analysis.

Fortran equivalent: ang function and related utilities in funcproc.f90
"""

import numpy as np
from pysuave.core.types import Coordinate3D


def calculate_solid_angle(
    p1: Coordinate3D,
    p2: Coordinate3D,
    p3: Coordinate3D,
    phi: float,
    theta: float
) -> float:
    """
    Calculate the solid angle for a triangular element on a spherical surface.
    
    This function computes the solid angle subtended by a triangle defined by
    three points (p1, p2, p3) at the origin. The solid angle is used in volume
    calculations for spherical surfaces.
    
    Mathematical approach:
        1. Calculate vectors v1 = p2 - p1 and v2 = p3 - p2
        2. Calculate cross product v3 = v1 x v2 (normal to triangle)
        3. Calculate radial direction vector at (phi, theta)
        4. Compute cosine of angle between normal and radial direction
        5. Return absolute value (solid angle proportional to this)
    
    Args:
        p1: First vertex of the triangle (Cartesian coordinates)
        p2: Second vertex of the triangle (Cartesian coordinates)
        p3: Third vertex of the triangle (Cartesian coordinates)
        phi: Azimuthal angle at triangle center (radians)
        theta: Polar angle at triangle center (radians)
    
    Returns:
        Solid angle factor (dimensionless, range [0, 1])
        Returns 1.0 for degenerate triangles (zero area)
    
    Notes:
        - This is a simplified solid angle calculation
        - For degenerate triangles (area ~ 0), returns 1.0
        - The threshold for degeneracy is 1e-6
        - Used in volume calculations for spherical surfaces
        - Original Fortran: ang function in funcproc.f90
    
    Mathematical formulation:
        v1 = p2 - p1
        v2 = p3 - p2
        v3 = v1 x v2  (cross product, normal to triangle)
        
        radial = [sin(phi)*cos(theta), sin(phi)*sin(theta), cos(phi)]
        
        cos_angle = (v3 · radial) / (|v3| * |radial|)
        solid_angle = |cos_angle|
    
    Example:
        >>> p1 = Coordinate3D(1.0, 0.0, 0.0)
        >>> p2 = Coordinate3D(0.0, 1.0, 0.0)
        >>> p3 = Coordinate3D(0.0, 0.0, 1.0)
        >>> angle = calculate_solid_angle(p1, p2, p3, np.pi/4, np.pi/4)
        >>> print(f"Solid angle factor: {angle:.3f}")
    """
    # Calculate vector v1 = p2 - p1
    # Fortran: v1%x = p2%x - p1%x, etc.
    v1_x = p2.x - p1.x
    v1_y = p2.y - p1.y
    v1_z = p2.z - p1.z
    
    # Calculate vector v2 = p3 - p2
    # Fortran: v2%x = p3%x - p2%x, etc.
    v2_x = p3.x - p2.x
    v2_y = p3.y - p2.y
    v2_z = p3.z - p2.z
    
    # Calculate cross product v3 = v1 x v2
    # This gives the normal vector to the triangle
    # Fortran: v3%x = -v2%y*v1%z + v2%z*v1%y, etc.
    v3_x = -v2_y * v1_z + v2_z * v1_y
    v3_y = -v2_z * v1_x + v2_x * v1_z
    v3_z = -v2_x * v1_y + v2_y * v1_x
    
    # Calculate magnitude squared of cross product
    v3_mag_sq = v3_x**2 + v3_y**2 + v3_z**2
    
    # Check for degenerate triangle (zero or very small area)
    # Fortran: if (v3%x**2 + v3%y**2 + v3%z**2 < 0.000001)
    # This occurs at phi extremities where triangle area is null
    if v3_mag_sq < 1e-6:
        # For degenerate triangles, return 1.0
        # The area is already zero, so the angle doesn't matter
        return 1.0
    
    # Calculate radial direction vector at (phi, theta)
    # This is the direction from origin to the triangle center
    # Fortran: v1%x = sin(phi)*cos(theta), etc.
    # (reusing v1 variable in Fortran for efficiency)
    radial_x = np.sin(phi) * np.cos(theta)
    radial_y = np.sin(phi) * np.sin(theta)
    radial_z = np.cos(phi)
    
    # Calculate dot product between normal and radial direction
    # Fortran: la = v1%x*v3%x + v1%y*v3%y + v1%z*v3%z
    dot_product = radial_x * v3_x + radial_y * v3_y + radial_z * v3_z
    
    # Normalize by magnitudes
    # Fortran: la = la / sqrt(v3%x**2 + v3%y**2 + v3%z**2)
    #          la = la / sqrt(v1%x**2 + v1%y**2 + v1%z**2)
    v3_mag = np.sqrt(v3_mag_sq)
    radial_mag = np.sqrt(radial_x**2 + radial_y**2 + radial_z**2)
    
    cos_angle = dot_product / (v3_mag * radial_mag)
    
    # Return absolute value
    # Fortran: ang = abs(la)
    solid_angle = abs(cos_angle)
    
    return float(solid_angle)


def calculate_cross_product(
    v1: Coordinate3D,
    v2: Coordinate3D
) -> Coordinate3D:
    """
    Calculate the cross product of two 3D vectors.
    
    Args:
        v1: First vector
        v2: Second vector
    
    Returns:
        Cross product v1 x v2
    
    Notes:
        Cross product formula:
        (v1 x v2)_x = v1_y * v2_z - v1_z * v2_y
        (v1 x v2)_y = v1_z * v2_x - v1_x * v2_z
        (v1 x v2)_z = v1_x * v2_y - v1_y * v2_x
    
    Example:
        >>> v1 = Coordinate3D(1.0, 0.0, 0.0)
        >>> v2 = Coordinate3D(0.0, 1.0, 0.0)
        >>> v3 = calculate_cross_product(v1, v2)
        >>> print(f"Cross product: ({v3.x}, {v3.y}, {v3.z})")
    """
    cross_x = v1.y * v2.z - v1.z * v2.y
    cross_y = v1.z * v2.x - v1.x * v2.z
    cross_z = v1.x * v2.y - v1.y * v2.x
    
    return Coordinate3D(x=cross_x, y=cross_y, z=cross_z)


def calculate_dot_product(
    v1: Coordinate3D,
    v2: Coordinate3D
) -> float:
    """
    Calculate the dot product of two 3D vectors.
    
    Args:
        v1: First vector
        v2: Second vector
    
    Returns:
        Dot product v1 · v2
    
    Example:
        >>> v1 = Coordinate3D(1.0, 2.0, 3.0)
        >>> v2 = Coordinate3D(4.0, 5.0, 6.0)
        >>> dot = calculate_dot_product(v1, v2)
        >>> print(f"Dot product: {dot}")
    """
    return v1.x * v2.x + v1.y * v2.y + v1.z * v2.z


def calculate_vector_magnitude(v: Coordinate3D) -> float:
    """
    Calculate the magnitude (length) of a 3D vector.
    
    Args:
        v: Input vector
    
    Returns:
        Magnitude |v| = sqrt(x^2 + y^2 + z^2)
    
    Example:
        >>> v = Coordinate3D(3.0, 4.0, 0.0)
        >>> mag = calculate_vector_magnitude(v)
        >>> print(f"Magnitude: {mag}")  # Should be 5.0
    """
    return np.sqrt(v.x**2 + v.y**2 + v.z**2)
