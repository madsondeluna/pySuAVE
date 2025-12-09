"""
Coordinate conversion functions for pySuAVE.

This module provides functions for converting between Cartesian and spherical
coordinate systems, with support for custom centers and grid operations.

Fortran equivalent: cart2sphe and sphe2cart in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import List, Tuple, Optional

from pysuave.core.types import AtomData, Coordinate3D, SphericalCoordinate
from pysuave.core.constants import PI


def cartesian_to_spherical_single(
    point: Coordinate3D,
    center: Optional[Coordinate3D] = None
) -> SphericalCoordinate:
    """
    Convert a single point from Cartesian to spherical coordinates.
    
    Args:
        point: Cartesian coordinates
        center: Center point for spherical system (default: origin)
    
    Returns:
        Spherical coordinates (rho, phi, theta)
    
    Notes:
        - rho: radial distance from center
        - phi: polar angle from z-axis [0, pi]
        - theta: azimuthal angle in xy-plane [0, 2*pi]
        - Uses atan2 for proper quadrant handling
    
    Example:
        >>> p = Coordinate3D(1.0, 1.0, 1.0)
        >>> s = cartesian_to_spherical_single(p)
        >>> print(f"rho={s.rho:.3f}, phi={s.phi:.3f}, theta={s.theta:.3f}")
    """
    if center is None:
        center = Coordinate3D(0.0, 0.0, 0.0)
    
    # Translate to center
    dx = point.x - center.x
    dy = point.y - center.y
    dz = point.z - center.z
    
    # Calculate rho (radial distance)
    rho = np.sqrt(dx**2 + dy**2 + dz**2)
    
    # Calculate phi (polar angle from z-axis)
    if rho > 0:
        phi = np.arccos(dz / rho)
    else:
        phi = 0.0
    
    # Calculate theta (azimuthal angle)
    # Use atan2 for proper quadrant handling
    theta = np.arctan2(dy, dx)
    
    # Ensure theta is in [0, 2*pi]
    if theta < 0:
        theta += 2.0 * PI
    
    return SphericalCoordinate(rho=rho, phi=phi, theta=theta)


def cartesian_to_spherical_atoms(
    atoms: List[AtomData],
    center: Optional[Coordinate3D] = None
) -> Tuple[List[SphericalCoordinate], float]:
    """
    Convert list of atoms from Cartesian to spherical coordinates.
    
    This function converts atomic coordinates and calculates the average
    radial distance, which is useful for defining the reference sphere.
    
    Args:
        atoms: List of atoms with Cartesian coordinates
        center: Center point for spherical system (default: origin)
    
    Returns:
        Tuple containing:
            - List of spherical coordinates
            - Average radial distance
    
    Notes:
        - Calculates running average of rho (Fortran compatibility)
        - Original Fortran: cart2sphe subroutine in funcproc.f90
    
    Example:
        >>> atoms = [AtomData(...), ...]
        >>> spherical_coords, r_avg = cartesian_to_spherical_atoms(atoms)
        >>> print(f"Average radius: {r_avg:.2f} A")
    """
    if center is None:
        center = Coordinate3D(0.0, 0.0, 0.0)
    
    spherical_coords = []
    sum_rho = 0.0
    
    for i, atom in enumerate(atoms):
        # Convert atom position to Coordinate3D
        point = Coordinate3D(x=atom.x, y=atom.y, z=atom.z)
        
        # Translate to center
        dx = point.x - center.x
        dy = point.y - center.y
        dz = point.z - center.z
        
        # Calculate rho
        # Fortran: store%rho = sqrt((spher%x - cent_x)**2 + ...)
        rho = np.sqrt(dx**2 + dy**2 + dz**2)
        
        # Calculate phi
        # Fortran: store%phi = acos((spher%z - cent_z) / store%rho)
        if rho > 0:
            phi = np.arccos(dz / rho)
        else:
            phi = 0.0
        
        # Calculate theta
        # Fortran handles special case when y == 0
        if abs(dy) < 1e-10:
            # Fortran: store%theta = 0.000
            theta = 0.0
        else:
            # Fortran: store%theta = acos((spher%x - cent_x) / sqrt(...))
            rho_xy = np.sqrt(dx**2 + dy**2)
            if rho_xy > 0:
                theta = np.arccos(dx / rho_xy)
                
                # Adjust for quadrant
                # Fortran: if ((spher%y - cent_y) <= 0) then store%theta = 2*pi - store%theta
                if dy < 0:
                    theta = 2.0 * PI - theta
            else:
                theta = 0.0
        
        spherical_coords.append(SphericalCoordinate(rho=rho, phi=phi, theta=theta))
        
        # Update running average
        # Fortran: r_med = (r_med * (num - 1) + store%rho) / num
        sum_rho += rho
    
    # Calculate average radius
    r_avg = sum_rho / len(atoms) if atoms else 0.0
    
    return spherical_coords, r_avg


def spherical_to_cartesian_grid(
    grid_spherical: npt.NDArray[np.float64],
    center: Optional[Coordinate3D] = None
) -> npt.NDArray[np.float64]:
    """
    Convert a grid from spherical to Cartesian coordinates.
    
    This function converts an entire grid of spherical coordinates to
    Cartesian coordinates, useful for visualization and analysis.
    
    Args:
        grid_spherical: Spherical coordinates, shape (n, m, 3)
                       grid[i, j] = [rho, phi, theta]
        center: Center point for spherical system (default: origin)
    
    Returns:
        Cartesian coordinates, shape (n, m, 3)
        grid[i, j] = [x, y, z]
    
    Notes:
        - Conversion formulas:
          x = rho * sin(phi) * cos(theta) + center_x
          y = rho * sin(phi) * sin(theta) + center_y
          z = rho * cos(phi) + center_z
        - Original Fortran: sphe2cart subroutine in funcproc.f90
    
    Example:
        >>> grid_cart = spherical_to_cartesian_grid(grid_sph)
        >>> print(f"Cartesian grid shape: {grid_cart.shape}")
    """
    if center is None:
        center = Coordinate3D(0.0, 0.0, 0.0)
    
    # Validate input
    if grid_spherical.ndim != 3 or grid_spherical.shape[2] != 3:
        raise ValueError(
            f"Grid must have shape (n, m, 3), got {grid_spherical.shape}"
        )
    
    lim_i = grid_spherical.shape[0]
    lim_j = grid_spherical.shape[1]
    
    # Initialize output grid
    grid_cartesian = np.zeros((lim_i, lim_j, 3), dtype=np.float64)
    
    # Convert each point
    # Fortran: do i=1, lim_i; do j=1, lim_j
    for i in range(lim_i):
        for j in range(lim_j):
            rho = grid_spherical[i, j, 0]
            phi = grid_spherical[i, j, 1]
            theta = grid_spherical[i, j, 2]
            
            # Convert to Cartesian
            # Fortran: grid3(i,j)%x = grid(i,j)%rho * sin(grid(i,j)%phi) * cos(grid(i,j)%theta) + cent_x
            x = rho * np.sin(phi) * np.cos(theta) + center.x
            y = rho * np.sin(phi) * np.sin(theta) + center.y
            z = rho * np.cos(phi) + center.z
            
            grid_cartesian[i, j, 0] = x
            grid_cartesian[i, j, 1] = y
            grid_cartesian[i, j, 2] = z
    
    return grid_cartesian


def spherical_to_cartesian_vectorized(
    grid_spherical: npt.NDArray[np.float64],
    center: Optional[Coordinate3D] = None
) -> npt.NDArray[np.float64]:
    """
    Convert a grid from spherical to Cartesian coordinates (vectorized).
    
    This is a faster, vectorized version of spherical_to_cartesian_grid
    using NumPy array operations.
    
    Args:
        grid_spherical: Spherical coordinates, shape (n, m, 3)
        center: Center point (default: origin)
    
    Returns:
        Cartesian coordinates, shape (n, m, 3)
    
    Example:
        >>> grid_cart = spherical_to_cartesian_vectorized(grid_sph)
    """
    if center is None:
        center = Coordinate3D(0.0, 0.0, 0.0)
    
    # Extract components
    rho = grid_spherical[:, :, 0]
    phi = grid_spherical[:, :, 1]
    theta = grid_spherical[:, :, 2]
    
    # Vectorized conversion
    x = rho * np.sin(phi) * np.cos(theta) + center.x
    y = rho * np.sin(phi) * np.sin(theta) + center.y
    z = rho * np.cos(phi) + center.z
    
    # Stack into output array
    grid_cartesian = np.stack([x, y, z], axis=-1)
    
    return grid_cartesian
