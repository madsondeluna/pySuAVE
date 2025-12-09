"""
Thickness calculation functions for pySuAVE.

This module provides functions for calculating membrane or surface thickness
from dual-surface representations. Thickness is measured as the distance
between two parallel surfaces.

Fortran equivalent: calc_thick and calc_thick_sph in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple

from pysuave.core.types import Coordinate3D
from pysuave.utils.geometry_utils import calculate_cross_product


def calculate_thickness_cartesian(
    grid1: npt.NDArray[np.float64],
    grid2: npt.NDArray[np.float64],
    grid3: npt.NDArray[np.float64],
    dx: float,
    dy: float
) -> Tuple[npt.NDArray[np.float64], float, float, float]:
    """
    Calculate membrane thickness for Cartesian surfaces.
    
    This function computes the thickness between two surfaces (grid1 and grid2)
    by projecting the distance along the local surface normal direction.
    
    Mathematical approach:
        1. Calculate surface normal from grid3 (average surface)
        2. Calculate average z-coordinates of both surfaces at each cell
        3. Project distance along normal: thickness = |normal_z * (z1 - z2)| / |normal|
        4. Accumulate statistics and volume
    
    Args:
        grid1: First surface (e.g., upper leaflet), shape (n_grid, n_grid, 3)
               grid[i, j] = [x, y, z]
        grid2: Second surface (e.g., lower leaflet), shape (n_grid, n_grid, 3)
               grid[i, j] = [x, y, z]
        grid3: Average surface (for normal calculation), shape (n_grid, n_grid, 3)
               grid[i, j] = [x, y, z]
        dx: Grid spacing in x direction (Angstroms)
        dy: Grid spacing in y direction (Angstroms)
    
    Returns:
        Tuple containing:
            - thickness_map: Thickness at each grid point, shape (n_grid-1, n_grid-1)
            - average: Average thickness (Angstroms)
            - std_dev: Standard deviation (Angstroms)
            - total_volume: Total volume between surfaces (cubic Angstroms)
    
    Notes:
        - Thickness is projected along local surface normal
        - Division by 10 in Fortran for unit conversion (kept for compatibility)
        - Volume calculated as sum of |delta_z * dx * dy|
        - Original Fortran: calc_thick subroutine in funcproc.f90
    
    Mathematical formulation:
        For each grid cell (i, j):
            normal = cross_product(diagonal1, diagonal2)
            z1_avg = average of 4 corner z-values from grid1
            z2_avg = average of 4 corner z-values from grid2
            
            thickness = |normal_z * (z1 - z2)| / |normal|
            volume += |z1 - z2| * dx * dy
    
    Example:
        >>> thick_map, avg, std, vol = calculate_thickness_cartesian(
        ...     grid1, grid2, grid3, dx=1.0, dy=1.0
        ... )
        >>> print(f"Average thickness: {avg:.2f} +/- {std:.2f} A")
        >>> print(f"Total volume: {vol:.2f} A^3")
    """
    # Validate grids
    if grid1.shape != grid2.shape or grid1.shape != grid3.shape:
        raise ValueError(
            f"All grids must have same shape: "
            f"grid1={grid1.shape}, grid2={grid2.shape}, grid3={grid3.shape}"
        )
    
    if grid1.ndim != 3 or grid1.shape[2] != 3:
        raise ValueError(f"Grids must have shape (n, n, 3), got {grid1.shape}")
    
    n_grid = grid1.shape[0]
    
    if n_grid < 2:
        raise ValueError(f"Grid must have at least 2 points, got {n_grid}")
    
    # Initialize outputs
    thickness_map = np.zeros((n_grid - 1, n_grid - 1), dtype=np.float64)
    
    total_volume = 0.0
    sum_thickness = 0.0
    sum_thickness_sq = 0.0
    count = 0
    
    # Loop over grid cells
    # Fortran: do i=2, n_grid+1; do j=2, n_grid+1
    # Python: for i in range(1, n_grid); for j in range(1, n_grid)
    for i in range(1, n_grid):
        for j in range(1, n_grid):
            # Calculate surface normal from grid3 (average surface)
            # Fortran: v1 = grid3(i,j) - grid3(i-1,j-1)
            v1 = Coordinate3D(
                x=grid3[i, j, 0] - grid3[i-1, j-1, 0],
                y=grid3[i, j, 1] - grid3[i-1, j-1, 1],
                z=grid3[i, j, 2] - grid3[i-1, j-1, 2]
            )
            
            # Fortran: v2 = grid3(i-1,j) - grid3(i,j-1)
            v2 = Coordinate3D(
                x=grid3[i-1, j, 0] - grid3[i, j-1, 0],
                y=grid3[i-1, j, 1] - grid3[i, j-1, 1],
                z=grid3[i-1, j, 2] - grid3[i, j-1, 2]
            )
            
            # Calculate cross product (surface normal)
            normal = calculate_cross_product(v1, v2)
            normal_mag = np.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
            
            if normal_mag < 1e-10:
                # Skip degenerate cells
                continue
            
            # Calculate average z-coordinate at 4 corners for grid1
            # Fortran: la = (grid(i-1,j-1)%z + grid(i-1,j)%z + grid(i,j-1)%z + grid(i,j)%z) / 4
            z1_avg = (grid1[i-1, j-1, 2] + grid1[i-1, j, 2] + 
                     grid1[i, j-1, 2] + grid1[i, j, 2]) / 4.0
            
            # Calculate average z-coordinate at 4 corners for grid2
            # Fortran: lb = (grid2(i-1,j-1)%z + grid2(i-1,j)%z + grid2(i,j-1)%z + grid2(i,j)%z) / 4
            z2_avg = (grid2[i-1, j-1, 2] + grid2[i-1, j, 2] + 
                     grid2[i, j-1, 2] + grid2[i, j, 2]) / 4.0
            
            # Calculate thickness projected along normal
            # Fortran: r_xpm(i-1,j-1) = abs(v3%z * (la - lb)) / sqrt(v3%x**2 + v3%y**2 + v3%z**2)
            thickness_projected = abs(normal.z * (z1_avg - z2_avg)) / normal_mag
            thickness_map[i-1, j-1] += thickness_projected
            
            # Accumulate volume
            # Fortran: s_v = s_v + abs((la - lb) * dx * dy)
            volume_element = abs((z1_avg - z2_avg) * dx * dy)
            total_volume += volume_element
            
            # Calculate thickness for statistics (divided by 10 for unit conversion)
            # Fortran: aux2 = abs(v3%z * (la - lb)) / sqrt(v3%x**2 + v3%y**2 + v3%z**2) / 10
            thickness_stat = thickness_projected / 10.0
            
            sum_thickness += thickness_stat
            sum_thickness_sq += thickness_stat * thickness_stat
            count += 1
    
    # Calculate statistics
    # Fortran normalizes by (n_grid+1)*(n_grid+1), but we use actual count
    if count > 0:
        average = sum_thickness / count
        average_sq = sum_thickness_sq / count
        std_dev = np.sqrt(abs(average_sq - average**2))
    else:
        average = 0.0
        std_dev = 0.0
    
    return thickness_map, average, std_dev, total_volume


def calculate_thickness_spherical(
    grid1_spherical: npt.NDArray[np.float64],
    grid2_spherical: npt.NDArray[np.float64]
) -> Tuple[npt.NDArray[np.float64], float, float]:
    """
    Calculate membrane thickness for spherical surfaces.
    
    This function computes the radial thickness between two spherical surfaces
    by calculating the difference in radial coordinates (rho).
    
    Mathematical approach:
        1. For each grid cell, average rho values at 4 corners for both surfaces
        2. Calculate thickness as difference: thickness = |rho1 - rho2|
        3. Accumulate statistics
    
    Args:
        grid1_spherical: First surface in spherical coords, shape (n_grid, n_grid, 3)
                        grid[i, j] = [rho, phi, theta]
        grid2_spherical: Second surface in spherical coords, shape (n_grid, n_grid, 3)
                        grid[i, j] = [rho, phi, theta]
    
    Returns:
        Tuple containing:
            - thickness_map: Thickness at each grid point
            - average: Average thickness (Angstroms)
            - std_dev: Standard deviation (Angstroms)
    
    Notes:
        - For spherical surfaces, thickness is simply radial difference
        - Division by 10 for statistics (unit conversion, kept for compatibility)
        - Multiplication by 10 when storing in map (reverses the division)
        - Original Fortran: calc_thick_sph subroutine in funcproc.f90
    
    Mathematical formulation:
        For each grid cell (i, j):
            rho1_avg = average of 4 corner rho values from grid1
            rho2_avg = average of 4 corner rho values from grid2
            thickness = |rho1_avg - rho2_avg|
    
    Example:
        >>> thick_map, avg, std = calculate_thickness_spherical(
        ...     grid1_sph, grid2_sph
        ... )
        >>> print(f"Average thickness: {avg:.2f} +/- {std:.2f} A")
    """
    # Validate grids
    if grid1_spherical.shape != grid2_spherical.shape:
        raise ValueError(
            f"Grids must have same shape: "
            f"grid1={grid1_spherical.shape}, grid2={grid2_spherical.shape}"
        )
    
    if grid1_spherical.ndim != 3 or grid1_spherical.shape[2] != 3:
        raise ValueError(
            f"Grids must have shape (n, n, 3), got {grid1_spherical.shape}"
        )
    
    lim_i = grid1_spherical.shape[0]
    lim_j = grid1_spherical.shape[1]
    
    if lim_i < 2 or lim_j < 2:
        raise ValueError(f"Grid must have at least 2 points, got ({lim_i}, {lim_j})")
    
    # Initialize outputs
    thickness_map = np.zeros((lim_i - 1, lim_j - 1), dtype=np.float64)
    
    sum_thickness = 0.0
    sum_thickness_sq = 0.0
    count = 0
    
    # Loop over grid cells
    # Fortran: do i=2, lim_i; do j=2, lim_j
    # Python: for i in range(1, lim_i); for j in range(1, lim_j)
    for i in range(1, lim_i):
        for j in range(1, lim_j):
            # Calculate average rho at 4 corners for grid1
            # Fortran: aux2 = grid(i,j)%rho + grid(i-1,j)%rho + grid(i,j-1)%rho + grid(i-1,j-1)%rho
            rho1_sum = (grid1_spherical[i, j, 0] + grid1_spherical[i-1, j, 0] + 
                       grid1_spherical[i, j-1, 0] + grid1_spherical[i-1, j-1, 0])
            
            # Calculate average rho at 4 corners for grid2
            # Fortran: aux2 = aux2 - (grid2(i,j)%rho + grid2(i-1,j)%rho + grid2(i,j-1)%rho + grid2(i-1,j-1)%rho)
            rho2_sum = (grid2_spherical[i, j, 0] + grid2_spherical[i-1, j, 0] + 
                       grid2_spherical[i, j-1, 0] + grid2_spherical[i-1, j-1, 0])
            
            # Calculate thickness (average of 4 corners, divided by 10)
            # Fortran: aux2 = abs(aux2 / 4) / 10
            thickness = abs((rho1_sum - rho2_sum) / 4.0) / 10.0
            
            # Update statistics
            sum_thickness += thickness
            sum_thickness_sq += thickness * thickness
            count += 1
            
            # Store in thickness map (multiply by 10 to reverse division)
            # Fortran: r_xpm1(i-1,j-1) = r_xpm1(i-1,j-1) + aux2 * 10
            thickness_map[i-1, j-1] += thickness * 10.0
    
    # Calculate statistics
    # Fortran normalizes by lim_i * lim_j, but we use actual count
    if count > 0:
        average = sum_thickness / count
        average_sq = sum_thickness_sq / count
        std_dev = np.sqrt(abs(average_sq - average**2))
    else:
        average = 0.0
        std_dev = 0.0
    
    return thickness_map, average, std_dev
