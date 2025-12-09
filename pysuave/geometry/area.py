"""
Surface area calculation functions for pySuAVE.

This module provides functions to calculate surface areas using Heron's formula
for triangulation. The surface is discretized into a grid, and each grid cell
is divided into two triangles for area calculation.

Fortran equivalent: calc_area and calc_area_sph in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple

from pysuave.core.types import Coordinate3D
from pysuave.utils.geometry_utils import calculate_solid_angle


def calculate_triangle_area_heron(
    p1: Coordinate3D,
    p2: Coordinate3D,
    p3: Coordinate3D
) -> float:
    """
    Calculate area of a triangle using Heron's formula.
    
    Heron's formula computes triangle area from the lengths of its three sides:
        s = (a + b + c) / 2  (semi-perimeter)
        Area = sqrt(s * (s - a) * (s - b) * (s - c))
    
    where a, b, c are the side lengths.
    
    Args:
        p1: First vertex of the triangle
        p2: Second vertex of the triangle
        p3: Third vertex of the triangle
    
    Returns:
        Area of the triangle in square Angstroms
    
    Notes:
        - Numerically stable for all triangle shapes
        - Returns 0 for degenerate triangles (collinear points)
        - Uses Euclidean distance in 3D space
    
    Example:
        >>> p1 = Coordinate3D(0.0, 0.0, 0.0)
        >>> p2 = Coordinate3D(1.0, 0.0, 0.0)
        >>> p3 = Coordinate3D(0.0, 1.0, 0.0)
        >>> area = calculate_triangle_area_heron(p1, p2, p3)
        >>> print(f"Triangle area: {area:.3f} A^2")
    """
    # Calculate side lengths
    # Side a: from p1 to p2
    a = p1.distance_to(p2)
    
    # Side b: from p1 to p3
    b = p1.distance_to(p3)
    
    # Side c: from p2 to p3
    c = p2.distance_to(p3)
    
    # Calculate semi-perimeter
    s = (a + b + c) / 2.0
    
    # Apply Heron's formula
    # Use max(0, ...) to handle numerical errors that might give slightly negative values
    area_squared = s * (s - a) * (s - b) * (s - c)
    area = np.sqrt(max(0.0, area_squared))
    
    return float(area)


def calculate_surface_area_cartesian(
    grid: npt.NDArray[np.float64]
) -> float:
    """
    Calculate total surface area from a Cartesian grid using triangulation.
    
    This function computes the surface area by dividing each grid cell into
    two triangles and summing their areas using Heron's formula.
    
    Grid cell triangulation:
        Each cell (i, j) is divided into two triangles:
        Triangle 1: (i-1,j-1), (i-1,j), (i,j-1)
        Triangle 2: (i-1,j), (i,j-1), (i,j)
    
    Mathematical approach:
        1. For each grid cell, calculate distances between vertices
        2. Apply Heron's formula to each triangle
        3. Sum all triangle areas
    
    Args:
        grid: 3D coordinate grid, shape (n_grid, n_grid, 3)
              grid[i, j] = [x, y, z] coordinates at grid point (i, j)
    
    Returns:
        Total surface area in square Angstroms
    
    Notes:
        - Grid must have shape (n, n, 3) where n >= 2
        - Uses all grid points from index 1 to n (0-based indexing)
        - Each grid cell contributes 2 triangles to the total area
        - Original Fortran: calc_area function in funcproc.f90
        - Fortran loops: do i=2, n_grid+1; do j=2, n_grid+1
        - Python loops: for i in range(1, n_grid); for j in range(1, n_grid)
    
    Raises:
        ValueError: If grid dimensions are invalid
    
    Example:
        >>> # Create a flat 10x10 grid
        >>> n = 10
        >>> x = np.linspace(0, 10, n)
        >>> y = np.linspace(0, 10, n)
        >>> xx, yy = np.meshgrid(x, y)
        >>> zz = np.zeros_like(xx)
        >>> grid = np.stack([xx, yy, zz], axis=-1)
        >>> area = calculate_surface_area_cartesian(grid)
        >>> print(f"Surface area: {area:.2f} A^2")
    """
    # Validate grid shape
    if grid.ndim != 3 or grid.shape[2] != 3:
        raise ValueError(
            f"Grid must have shape (n, n, 3), got {grid.shape}"
        )
    
    n_grid = grid.shape[0]
    
    if n_grid < 2:
        raise ValueError(f"Grid must have at least 2 points per dimension, got {n_grid}")
    
    # Initialize total area
    total_area = 0.0
    
    # Loop over grid cells
    # Fortran: do i=2, n_grid+1 (1-indexed, inclusive)
    # Python: for i in range(1, n_grid) (0-indexed, exclusive upper bound)
    for i in range(1, n_grid):
        for j in range(1, n_grid):
            # First triangle: vertices at (i-1,j-1), (i-1,j), (i,j-1)
            # These correspond to Fortran indices (i-1,j-1), (i-1,j), (i,j-1)
            
            p1 = Coordinate3D(
                x=grid[i-1, j-1, 0],
                y=grid[i-1, j-1, 1],
                z=grid[i-1, j-1, 2]
            )
            p2 = Coordinate3D(
                x=grid[i-1, j, 0],
                y=grid[i-1, j, 1],
                z=grid[i-1, j, 2]
            )
            p3 = Coordinate3D(
                x=grid[i, j-1, 0],
                y=grid[i, j-1, 1],
                z=grid[i, j-1, 2]
            )
            
            # Calculate area of first triangle
            area1 = calculate_triangle_area_heron(p1, p2, p3)
            total_area += area1
            
            # Second triangle: vertices at (i-1,j), (i,j-1), (i,j)
            # Reuse p2 and p3 from above, define new p4
            p4 = Coordinate3D(
                x=grid[i, j, 0],
                y=grid[i, j, 1],
                z=grid[i, j, 2]
            )
            
            # Calculate area of second triangle
            # Triangle: p2, p3, p4
            area2 = calculate_triangle_area_heron(p2, p3, p4)
            total_area += area2
    
    return float(total_area)


def calculate_surface_area_and_volume_spherical(
    grid_spherical: npt.NDArray[np.float64],
    grid_cartesian: npt.NDArray[np.float64],
    dphi: float,
    dtheta: float
) -> Tuple[float, float]:
    """
    Calculate surface area and enclosed volume for spherical surfaces.
    
    This function computes both the surface area (using triangulation) and
    the enclosed volume (using solid angle integration) for spherical surfaces.
    
    Volume calculation:
        For each triangular element:
            1. Calculate solid angle subtended by triangle
            2. Volume contribution = (solid_angle * area * radius) / 3
        
        Total volume = sum of all contributions
    
    Args:
        grid_spherical: Spherical coordinates, shape (n_grid, n_grid, 3)
                       grid[i, j] = [rho, phi, theta]
        grid_cartesian: Cartesian coordinates, shape (n_grid, n_grid, 3)
                       grid[i, j] = [x, y, z]
                       Same points as grid_spherical, in Cartesian form
        dphi: Grid spacing in phi direction (radians)
        dtheta: Grid spacing in theta direction (radians)
    
    Returns:
        Tuple containing:
            - surface_area: Total surface area (square Angstroms)
            - volume: Enclosed volume (cubic Angstroms)
    
    Notes:
        - Requires both spherical and Cartesian representations
        - Spherical grid stores (rho, phi, theta) for volume calculation
        - Cartesian grid stores (x, y, z) for area calculation
        - Uses solid angle calculation (ang function, needs implementation)
        - Original Fortran: calc_area_sph subroutine in funcproc.f90
    
    Raises:
        ValueError: If grid dimensions don't match or are invalid
    
    Example:
        >>> area, volume = calculate_surface_area_and_volume_spherical(
        ...     grid_sph, grid_cart, dphi=0.1, dtheta=0.1
        ... )
        >>> print(f"Surface area: {area:.2f} A^2")
        >>> print(f"Volume: {volume:.2f} A^3")
    """
    # Validate grid shapes
    if grid_spherical.shape != grid_cartesian.shape:
        raise ValueError(
            f"Grid shapes must match: spherical={grid_spherical.shape}, "
            f"cartesian={grid_cartesian.shape}"
        )
    
    if grid_spherical.ndim != 3 or grid_spherical.shape[2] != 3:
        raise ValueError(
            f"Grids must have shape (n, n, 3), got {grid_spherical.shape}"
        )
    
    n_i = grid_spherical.shape[0]
    n_j = grid_spherical.shape[1]
    
    if n_i < 2 or n_j < 2:
        raise ValueError(
            f"Grid must have at least 2 points per dimension, got ({n_i}, {n_j})"
        )
    
    # Initialize area and volume
    total_area = 0.0
    total_volume = 0.0
    
    # Loop over grid cells
    # Fortran: do i=2, lim_i; do j=2, lim_j
    # Python: for i in range(1, n_i); for j in range(1, n_j)
    for i in range(1, n_i):
        for j in range(1, n_j):
            # First triangle vertices in Cartesian coordinates
            p1 = Coordinate3D(
                x=grid_cartesian[i-1, j-1, 0],
                y=grid_cartesian[i-1, j-1, 1],
                z=grid_cartesian[i-1, j-1, 2]
            )
            p2 = Coordinate3D(
                x=grid_cartesian[i-1, j, 0],
                y=grid_cartesian[i-1, j, 1],
                z=grid_cartesian[i-1, j, 2]
            )
            p3 = Coordinate3D(
                x=grid_cartesian[i, j-1, 0],
                y=grid_cartesian[i, j-1, 1],
                z=grid_cartesian[i, j-1, 2]
            )
            
            # Calculate area of first triangle using Heron's formula
            # Note: Fortran uses abs() for safety, we use max(0, ...) in Heron
            area1 = calculate_triangle_area_heron(p1, p2, p3)
            total_area += area1
            
            # Calculate solid angle for first triangle
            # Center point for solid angle calculation
            # Fortran: (i-1-0.5)*dph, (j-1-0.5)*dth
            phi_center = (i - 1 - 0.5) * dphi
            theta_center = (j - 1 - 0.5) * dtheta
            
            # Calculate solid angle using ang function
            # Fortran: c_angle = ang(grid3(i-1,j-1), grid3(i-1,j), grid3(i,j-1), (i-1-0.5)*dph, (j-1-0.5)*dth)
            solid_angle1 = calculate_solid_angle(p1, p2, p3, phi_center, theta_center)
            
            # Get radius at this point
            rho1 = grid_spherical[i-1, j-1, 0]  # rho coordinate
            
            # Volume contribution from first triangle
            # Formula: V = (solid_angle * area * radius) / 3
            # Fortran: s_vol = s_vol + c_angle*aux2*grid(i-1,j-1)%rho/3
            volume1 = solid_angle1 * area1 * rho1 / 3.0
            total_volume += volume1
            
            # Second triangle
            p4 = Coordinate3D(
                x=grid_cartesian[i, j, 0],
                y=grid_cartesian[i, j, 1],
                z=grid_cartesian[i, j, 2]
            )
            
            area2 = calculate_triangle_area_heron(p2, p3, p4)
            total_area += area2
            
            # Solid angle for second triangle
            # Fortran: c_angle = ang(grid3(i-1,j), grid3(i,j-1), grid3(i,j), (i-1-0.5)*dph, (j-1-0.5)*dth)
            solid_angle2 = calculate_solid_angle(p2, p3, p4, phi_center, theta_center)
            
            # Get radius at second triangle vertex
            rho2 = grid_spherical[i, j, 0]
            
            # Volume contribution from second triangle
            # Fortran: s_vol = s_vol + c_angle*aux2*grid(i,j)%rho/3
            volume2 = solid_angle2 * area2 * rho2 / 3.0
            total_volume += volume2
    
    return float(total_area), float(total_volume)
