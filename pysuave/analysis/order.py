"""
Order parameter calculation functions for pySuAVE.

This module provides functions for calculating orientational order parameters
of surfaces. The order parameter quantifies how aligned surface normals are
with respect to a reference direction (typically the z-axis or radial direction).

Fortran equivalent: calc_order and calc_order_sph in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple

from pysuave.core.types import Coordinate3D
from pysuave.utils.geometry_utils import calculate_cross_product


def calculate_order_parameter_cartesian(
    grid: npt.NDArray[np.float64]
) -> Tuple[npt.NDArray[np.float64], float, float, npt.NDArray[np.float64]]:
    """
    Calculate orientational order parameter for Cartesian grid.
    
    This function computes the order parameter P2 = 0.5 * (3*cos^2(theta) - 1)
    where theta is the angle between the surface normal and the z-axis.
    
    Mathematical approach:
        1. For each grid cell, calculate two diagonal vectors
        2. Compute cross product to get surface normal
        3. Calculate angle between normal and z-axis
        4. Compute order parameter: P2 = 0.5 * (3*cos^2(theta) - 1)
    
    Args:
        grid: 3D coordinate grid, shape (n_grid, n_grid, 3)
              grid[i, j] = [x, y, z] coordinates
    
    Returns:
        Tuple containing:
            - order_map: Order parameter at each grid point, shape (n_grid-1, n_grid-1)
            - average: Average order parameter
            - std_dev: Standard deviation of order parameter
            - angle_histogram: Histogram of angles (0-90 degrees), shape (100,)
    
    Notes:
        - P2 = 1: Perfect alignment with z-axis
        - P2 = 0: Random orientation
        - P2 = -0.5: Perfect alignment perpendicular to z-axis
        - Angle is calculated in degrees (0-90)
        - Original Fortran: calc_order subroutine in funcproc.f90
    
    Mathematical formulation:
        For each grid cell (i, j):
            v1 = grid[i,j] - grid[i-1,j-1]  (diagonal vector 1)
            v2 = grid[i-1,j] - grid[i,j-1]  (diagonal vector 2)
            normal = v1 x v2  (cross product, surface normal)
            
            theta = arccos(normal_z / |normal|)  (angle with z-axis)
            P2 = 0.5 * (3*cos^2(theta) - 1)  (order parameter)
    
    Example:
        >>> order_map, avg, std, hist = calculate_order_parameter_cartesian(grid)
        >>> print(f"Average order: {avg:.3f} +/- {std:.3f}")
    """
    # Validate grid
    if grid.ndim != 3 or grid.shape[2] != 3:
        raise ValueError(f"Grid must have shape (n, n, 3), got {grid.shape}")
    
    n_grid = grid.shape[0]
    
    if n_grid < 2:
        raise ValueError(f"Grid must have at least 2 points, got {n_grid}")
    
    # Initialize outputs
    order_map = np.zeros((n_grid - 1, n_grid - 1), dtype=np.float64)
    angle_histogram = np.zeros(100, dtype=np.float64)
    
    sum_order = 0.0
    sum_order_sq = 0.0
    count = 0
    
    # Loop over grid cells
    # Fortran: do i=2, n_grid+1; do j=2, n_grid+1
    # Python: for i in range(1, n_grid); for j in range(1, n_grid)
    for i in range(1, n_grid):
        for j in range(1, n_grid):
            # Calculate diagonal vectors
            # Fortran: v1 = grid(i,j) - grid(i-1,j-1)
            v1 = Coordinate3D(
                x=grid[i, j, 0] - grid[i-1, j-1, 0],
                y=grid[i, j, 1] - grid[i-1, j-1, 1],
                z=grid[i, j, 2] - grid[i-1, j-1, 2]
            )
            
            # Fortran: v2 = grid(i-1,j) - grid(i,j-1)
            v2 = Coordinate3D(
                x=grid[i-1, j, 0] - grid[i, j-1, 0],
                y=grid[i-1, j, 1] - grid[i, j-1, 1],
                z=grid[i-1, j, 2] - grid[i, j-1, 2]
            )
            
            # Calculate cross product (surface normal)
            # Fortran: v3 = v1 x v2
            # v3%x = -v2%y*v1%z + v2%z*v1%y, etc.
            normal = calculate_cross_product(v1, v2)
            
            # Calculate magnitude of normal
            normal_mag = np.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
            
            if normal_mag < 1e-10:
                # Skip degenerate cells
                continue
            
            # Calculate angle with z-axis
            # Fortran: la = acos(v3%z / sqrt(v3%x**2 + v3%y**2 + v3%z**2)) * 180/pi
            cos_theta = normal.z / normal_mag
            
            # Clamp to [-1, 1] to avoid numerical errors in acos
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
            
            # Angle in radians, then convert to degrees
            theta_rad = np.arccos(cos_theta)
            theta_deg = theta_rad * 180.0 / np.pi
            
            # Validate angle range
            if theta_deg < 0 or theta_deg > 90:
                # This should not happen with proper clipping
                # But keep check for safety
                continue
            
            # Calculate order parameter
            # Fortran: aux2 = 0.5 * (3*cos(la*pi/180)**2 - 1)
            # Note: cos(theta_rad) = cos_theta (already calculated)
            order_param = 0.5 * (3.0 * cos_theta**2 - 1.0)
            
            # Store in order map
            # Fortran: r_xpm(i-1, j-1) = r_xpm(i-1, j-1) + aux2
            order_map[i-1, j-1] += order_param
            
            # Update statistics
            sum_order += order_param
            sum_order_sq += order_param * order_param
            count += 1
            
            # Update angle histogram
            # Fortran: bini = nint(la) + 1; hist(bini) = hist(bini) + 1
            bin_index = int(np.round(theta_deg))
            if 0 <= bin_index < 100:
                angle_histogram[bin_index] += 1
    
    # Calculate average and standard deviation
    if count > 0:
        average = sum_order / count
        average_sq = sum_order_sq / count
        std_dev = np.sqrt(average_sq - average**2)
    else:
        average = 0.0
        std_dev = 0.0
    
    return order_map, average, std_dev, angle_histogram


def calculate_order_parameter_spherical(
    grid_cartesian: npt.NDArray[np.float64],
    dphi: float,
    dtheta: float
) -> Tuple[npt.NDArray[np.float64], float, float, npt.NDArray[np.float64]]:
    """
    Calculate orientational order parameter for spherical grid.
    
    This function computes the order parameter for spherical surfaces by
    comparing the surface normal with the radial direction at each point.
    
    Mathematical approach:
        1. For each grid cell, calculate surface normal (cross product)
        2. Calculate radial direction at cell center
        3. Compute dot product between normal and radial direction
        4. Calculate order parameter: P2 = 0.5 * (3*cos^2(alpha) - 1)
    
    Args:
        grid_cartesian: Cartesian coordinates, shape (n_grid, n_grid, 3)
                       grid[i, j] = [x, y, z]
        dphi: Grid spacing in phi direction (radians)
        dtheta: Grid spacing in theta direction (radians)
    
    Returns:
        Tuple containing:
            - order_map: Order parameter at each grid point
            - average: Average order parameter
            - std_dev: Standard deviation
            - angle_histogram: Histogram of angles (0-90 degrees), shape (1000,)
    
    Notes:
        - For spherical surfaces, normal should align with radial direction
        - P2 = 1: Perfect radial alignment
        - P2 = 0: Random orientation
        - P2 = -0.5: Tangential alignment
        - Original Fortran: calc_order_sph subroutine in funcproc.f90
    
    Mathematical formulation:
        For each grid cell (i, j):
            v1 = grid[i,j] - grid[i-1,j-1]
            v2 = grid[i-1,j] - grid[i,j-1]
            normal = v1 x v2
            
            phi_center = (i - 1.5) * dphi
            theta_center = (j - 1.5) * dtheta
            radial = [sin(phi)*cos(theta), sin(phi)*sin(theta), cos(phi)]
            
            cos_alpha = (normal · radial) / (|normal| * |radial|)
            P2 = 0.5 * (3*cos^2(alpha) - 1)
    
    Example:
        >>> order_map, avg, std, hist = calculate_order_parameter_spherical(
        ...     grid, dphi=0.1, dtheta=0.1
        ... )
        >>> print(f"Average order: {avg:.3f}")
    """
    # Validate grid
    if grid_cartesian.ndim != 3 or grid_cartesian.shape[2] != 3:
        raise ValueError(
            f"Grid must have shape (n, n, 3), got {grid_cartesian.shape}"
        )
    
    lim_i = grid_cartesian.shape[0]
    lim_j = grid_cartesian.shape[1]
    
    if lim_i < 2 or lim_j < 2:
        raise ValueError(f"Grid must have at least 2 points, got ({lim_i}, {lim_j})")
    
    # Initialize outputs
    order_map = np.zeros((lim_i - 1, lim_j - 1), dtype=np.float64)
    angle_histogram = np.zeros(1000, dtype=np.float64)
    
    sum_order = 0.0
    sum_order_sq = 0.0
    count = 0
    
    # Loop over grid cells
    for i in range(1, lim_i):
        for j in range(1, lim_j):
            # Calculate diagonal vectors
            v1 = Coordinate3D(
                x=grid_cartesian[i, j, 0] - grid_cartesian[i-1, j-1, 0],
                y=grid_cartesian[i, j, 1] - grid_cartesian[i-1, j-1, 1],
                z=grid_cartesian[i, j, 2] - grid_cartesian[i-1, j-1, 2]
            )
            
            v2 = Coordinate3D(
                x=grid_cartesian[i-1, j, 0] - grid_cartesian[i, j-1, 0],
                y=grid_cartesian[i-1, j, 1] - grid_cartesian[i, j-1, 1],
                z=grid_cartesian[i-1, j, 2] - grid_cartesian[i, j-1, 2]
            )
            
            # Calculate surface normal
            normal = calculate_cross_product(v1, v2)
            normal_mag = np.sqrt(normal.x**2 + normal.y**2 + normal.z**2)
            
            if normal_mag < 1e-10:
                continue
            
            # Calculate radial direction at cell center
            # Fortran: v1 = [sin((i-1-0.5)*dph)*cos((j-1-0.5)*dth), ...]
            # (reusing v1 variable)
            phi_center = (i - 1 - 0.5) * dphi
            theta_center = (j - 1 - 0.5) * dtheta
            
            radial = Coordinate3D(
                x=np.sin(phi_center) * np.cos(theta_center),
                y=np.sin(phi_center) * np.sin(theta_center),
                z=np.cos(phi_center)
            )
            
            radial_mag = np.sqrt(radial.x**2 + radial.y**2 + radial.z**2)
            
            # Calculate dot product
            # Fortran: la = v1%x*v3%x + v1%y*v3%y + v1%z*v3%z
            dot_product = (normal.x * radial.x + normal.y * radial.y + 
                          normal.z * radial.z)
            
            # Normalize
            # Fortran: la = la / sqrt(v3%x**2 + v3%y**2 + v3%z**2)
            #          la = la / sqrt(v1%x**2 + v1%y**2 + v1%z**2)
            cos_alpha = dot_product / (normal_mag * radial_mag)
            
            # Clamp to avoid numerical errors
            # Fortran: la = min(la, 1.00)
            cos_alpha = np.clip(cos_alpha, -1.0, 1.0)
            
            # Calculate order parameter
            # Fortran: aux2 = 0.5 * (3*(la)**2 - 1)
            order_param = 0.5 * (3.0 * cos_alpha**2 - 1.0)
            
            # Store in order map
            order_map[i-1, j-1] += order_param
            
            # Update statistics
            sum_order += order_param
            sum_order_sq += order_param * order_param
            count += 1
            
            # Calculate angle in degrees for histogram
            # Fortran: la = acos(la) * 180/pi
            alpha_rad = np.arccos(cos_alpha)
            alpha_deg = alpha_rad * 180.0 / np.pi
            
            # Validate angle range
            if alpha_deg < 0 or alpha_deg > 90:
                continue
            
            # Update histogram
            bin_index = int(np.round(alpha_deg))
            if 0 <= bin_index < 1000:
                angle_histogram[bin_index] += 1
    
    # Calculate statistics
    if count > 0:
        average = sum_order / count
        average_sq = sum_order_sq / count
        std_dev = np.sqrt(average_sq - average**2)
    else:
        average = 0.0
        std_dev = 0.0
    
    return order_map, average, std_dev, angle_histogram
