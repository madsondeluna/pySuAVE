"""
Topography and inertia calculation functions for pySuAVE.

This module provides functions for calculating surface topography (average position)
and moment of inertia tensor for molecular surfaces.

Fortran equivalent: calc_topog and calc_inertia in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple

from pysuave.core.types import SphericalCoordinate


def calculate_topography(
    grid1: npt.NDArray[np.float64],
    grid2: npt.NDArray[np.float64]
) -> Tuple[npt.NDArray[np.float64], float, float]:
    """
    Calculate surface topography (average z-position between two surfaces).
    
    This function computes the average position between two surfaces, which
    represents the topography or midplane of a bilayer/membrane system.
    
    Mathematical approach:
        For each grid cell:
            z1_avg = average of 4 corner z-values from grid1
            z2_avg = average of 4 corner z-values from grid2
            topography = (z1_avg + z2_avg) / 2
    
    Args:
        grid1: First surface, shape (n_grid, n_grid, 3)
               grid[i, j] = [x, y, z]
        grid2: Second surface, shape (n_grid, n_grid, 3)
               grid[i, j] = [x, y, z]
    
    Returns:
        Tuple containing:
            - topography_map: Average z-position at each grid point
            - average: Average topography value
            - std_dev: Standard deviation
    
    Notes:
        - Division by 10 for unit conversion (kept for Fortran compatibility)
        - Topography represents the midplane between two surfaces
        - Original Fortran: calc_topog subroutine in funcproc.f90
    
    Example:
        >>> topo_map, avg, std = calculate_topography(grid1, grid2)
        >>> print(f"Average topography: {avg:.2f} +/- {std:.2f} A")
    """
    # Validate grids
    if grid1.shape != grid2.shape:
        raise ValueError(
            f"Grids must have same shape: grid1={grid1.shape}, grid2={grid2.shape}"
        )
    
    if grid1.ndim != 3 or grid1.shape[2] != 3:
        raise ValueError(f"Grids must have shape (n, n, 3), got {grid1.shape}")
    
    n_grid = grid1.shape[0]
    
    if n_grid < 2:
        raise ValueError(f"Grid must have at least 2 points, got {n_grid}")
    
    # Initialize outputs
    topography_map = np.zeros((n_grid - 1, n_grid - 1), dtype=np.float64)
    
    sum_topo = 0.0
    sum_topo_sq = 0.0
    count = 0
    
    # Loop over grid cells
    # Fortran: do i=2, n_grid+1; do j=2, n_grid+1
    for i in range(1, n_grid):
        for j in range(1, n_grid):
            # Calculate average z at 4 corners for grid1
            # Fortran: la = (grid(i-1,j-1)%z + grid(i-1,j)%z + grid(i,j-1)%z + grid(i,j)%z) / 4
            z1_avg = (grid1[i-1, j-1, 2] + grid1[i-1, j, 2] + 
                     grid1[i, j-1, 2] + grid1[i, j, 2]) / 4.0
            
            # Calculate average z at 4 corners for grid2
            # Fortran: lb = (grid2(i-1,j-1)%z + grid2(i-1,j)%z + grid2(i,j-1)%z + grid2(i,j)%z) / 4
            z2_avg = (grid2[i-1, j-1, 2] + grid2[i-1, j, 2] + 
                     grid2[i, j-1, 2] + grid2[i, j, 2]) / 4.0
            
            # Calculate topography (average position)
            # Fortran: lc = (la + lb)
            topography = (z1_avg + z2_avg)
            
            # Store in map (divided by 10)
            # Fortran: r_xpm(i-1,j-1) = r_xpm(i-1,j-1) + lc / 10
            topography_map[i-1, j-1] += topography / 10.0
            
            # Update statistics
            # Fortran: aver = aver + lc/10/(n_grid*n_grid)
            #          aver2 = aver2 + lc*lc/100/(n_grid*n_grid)
            topo_scaled = topography / 10.0
            sum_topo += topo_scaled
            sum_topo_sq += (topography * topography) / 100.0
            count += 1
    
    # Calculate statistics
    if count > 0:
        average = sum_topo / count
        average_sq = sum_topo_sq / count
        std_dev = np.sqrt(abs(average_sq - average**2))
    else:
        average = 0.0
        std_dev = 0.0
    
    return topography_map, average, std_dev


def calculate_moment_of_inertia(
    grid_spherical: npt.NDArray[np.float64]
) -> npt.NDArray[np.float64]:
    """
    Calculate moment of inertia tensor for a spherical surface.
    
    This function computes the 3x3 moment of inertia tensor for a surface
    defined in spherical coordinates. The tensor is calculated about the
    center of mass of the surface.
    
    Mathematical approach:
        1. Convert spherical to Cartesian coordinates
        2. Calculate center of mass
        3. Compute moment of inertia tensor:
           I_xx = sum((y - y_cm)^2 + (z - z_cm)^2)
           I_yy = sum((x - x_cm)^2 + (z - z_cm)^2)
           I_zz = sum((x - x_cm)^2 + (y - y_cm)^2)
           I_xy = -sum((x - x_cm) * (y - y_cm))
           I_xz = -sum((x - x_cm) * (z - z_cm))
           I_yz = -sum((y - y_cm) * (z - z_cm))
    
    Args:
        grid_spherical: Spherical coordinates, shape (n_grid, n_grid, 3)
                       grid[i, j] = [rho, phi, theta]
    
    Returns:
        Moment of inertia tensor, shape (3, 3)
        Symmetric matrix with:
            MI[0,0] = I_xx, MI[1,1] = I_yy, MI[2,2] = I_zz
            MI[0,1] = MI[1,0] = I_xy
            MI[0,2] = MI[2,0] = I_xz
            MI[1,2] = MI[2,1] = I_yz
    
    Notes:
        - Coordinates divided by 10 for unit conversion
        - Tensor is symmetric
        - Can be diagonalized to find principal axes
        - Original Fortran: calc_inertia subroutine in funcproc.f90
    
    Example:
        >>> MI = calculate_moment_of_inertia(grid_sph)
        >>> eigenvalues, eigenvectors = np.linalg.eig(MI)
        >>> print(f"Principal moments: {eigenvalues}")
    """
    # Validate grid
    if grid_spherical.ndim != 3 or grid_spherical.shape[2] != 3:
        raise ValueError(
            f"Grid must have shape (n, n, 3), got {grid_spherical.shape}"
        )
    
    n_grid = grid_spherical.shape[0]
    
    if n_grid < 1:
        raise ValueError(f"Grid must have at least 1 point, got {n_grid}")
    
    # Initialize moment of inertia tensor
    # Fortran: MI(3,3) = 0
    MI = np.zeros((3, 3), dtype=np.float64)
    
    # Convert spherical to Cartesian and calculate center of mass
    # Fortran uses grid3 to store Cartesian coordinates
    cartesian_coords = np.zeros((n_grid, n_grid, 3), dtype=np.float64)
    
    sum_x = 0.0
    sum_y = 0.0
    sum_z = 0.0
    
    # Fortran: do i=1, n_grid; do j=1, n_grid
    for i in range(n_grid):
        for j in range(n_grid):
            rho = grid_spherical[i, j, 0]
            phi = grid_spherical[i, j, 1]
            theta = grid_spherical[i, j, 2]
            
            # Convert to Cartesian (divided by 10)
            # Fortran: grid3(i,j)%x = grid(i,j)%rho * sin(grid(i,j)%phi) * cos(grid(i,j)%theta) / 10
            x = rho * np.sin(phi) * np.cos(theta) / 10.0
            y = rho * np.sin(phi) * np.sin(theta) / 10.0
            z = rho * np.cos(phi) / 10.0
            
            cartesian_coords[i, j, 0] = x
            cartesian_coords[i, j, 1] = y
            cartesian_coords[i, j, 2] = z
            
            sum_x += x
            sum_y += y
            sum_z += z
    
    # Calculate center of mass
    # Fortran: averx = averx / (n_grid * n_grid)
    total_points = n_grid * n_grid
    cm_x = sum_x / total_points
    cm_y = sum_y / total_points
    cm_z = sum_z / total_points
    
    # Calculate moment of inertia tensor
    for i in range(n_grid):
        for j in range(n_grid):
            x = cartesian_coords[i, j, 0]
            y = cartesian_coords[i, j, 1]
            z = cartesian_coords[i, j, 2]
            
            dx = x - cm_x
            dy = y - cm_y
            dz = z - cm_z
            
            # Diagonal elements
            # Fortran: MI(1,1) = MI(1,1) + (grid3(i,j)%y - avery)**2 + (grid3(i,j)%z - averz)**2
            MI[0, 0] += dy**2 + dz**2  # I_xx
            MI[1, 1] += dx**2 + dz**2  # I_yy
            MI[2, 2] += dx**2 + dy**2  # I_zz
            
            # Off-diagonal elements
            # Fortran: MI(1,2) = MI(1,2) - (grid3(i,j)%x - averx) * (grid3(i,j)%y - avery)
            MI[0, 1] += -dx * dy  # I_xy
            MI[0, 2] += -dx * dz  # I_xz
            MI[1, 2] += -dy * dz  # I_yz
    
    # Normalize by number of points
    # Fortran: MI(i,j) = MI(i,j) / (n_grid * n_grid)
    MI = MI / total_points
    
    # Make symmetric
    # Fortran: MI(2,1) = MI(1,2), etc.
    MI[1, 0] = MI[0, 1]
    MI[2, 0] = MI[0, 2]
    MI[2, 1] = MI[1, 2]
    
    return MI
