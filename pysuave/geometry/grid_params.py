"""
Grid parameter calculation functions for pySuAVE.

This module contains functions for calculating grid parameters used in
surface fitting and analysis. These functions determine optimal grid spacing
and smoothing parameters based on surface characteristics.

Fortran equivalent: param and param_esf subroutines in funcproc.f90
"""

import numpy as np
from typing import Tuple


def calculate_grid_parameters_cartesian(
    x_max: float,
    x_min: float,
    y_max: float,
    y_min: float,
    num_points: int,
    roughness: float = 1.0
) -> Tuple[float, float]:
    """
    Calculate grid parameters for Cartesian coordinate systems.
    
    This function computes the fitting radius (r_fit) and smoothing parameter (alpha)
    for a rectangular grid based on the surface dimensions and number of grid points.
    
    The fitting radius determines the local neighborhood size for surface fitting,
    while alpha controls the smoothing level applied to the surface.
    
    Mathematical formulation:
        r_fit = 3 * sqrt((x_max - x_min)^2 + (y_max - y_min)^2) / sqrt(num_points - 1)
        
        density = (num_points - 1) * 100 / ((x_max - x_min) * (y_max - y_min))
        alpha = exp(0.4247 * roughness * log(density) - 1.3501 / roughness)
    
    Args:
        x_max: Maximum x coordinate of the surface (Angstroms)
        x_min: Minimum x coordinate of the surface (Angstroms)
        y_max: Maximum y coordinate of the surface (Angstroms)
        y_min: Minimum y coordinate of the surface (Angstroms)
        num_points: Number of grid points to be used
        roughness: Surface roughness parameter (0.0 to 1.0, default 1.0)
                  1.0 = keep 100% of original roughness
                  0.5 = keep 50% of original roughness (smoother)
    
    Returns:
        Tuple containing:
            - r_fit: Fitting radius for local surface approximation (Angstroms)
            - alpha: Smoothing parameter (dimensionless)
    
    Raises:
        ValueError: If num_points < 2 or if dimensions are invalid
    
    Notes:
        - The fitting radius scales with surface size and inversely with point density
        - Alpha parameter is empirically calibrated (coefficients 0.4247 and 1.3501)
        - Roughness parameter allows user control over surface smoothing
        - Original Fortran implementation in funcproc.f90, subroutine param
    
    Example:
        >>> r_fit, alpha = calculate_grid_parameters_cartesian(
        ...     x_max=100.0, x_min=0.0, y_max=100.0, y_min=0.0,
        ...     num_points=1000, roughness=1.0
        ... )
        >>> print(f"Fitting radius: {r_fit:.3f} A")
        >>> print(f"Smoothing parameter: {alpha:.3f}")
    """
    # Validate inputs
    if num_points < 2:
        raise ValueError(f"num_points must be >= 2, got {num_points}")
    
    x_range = x_max - x_min
    y_range = y_max - y_min
    
    if x_range <= 0 or y_range <= 0:
        raise ValueError(
            f"Invalid dimensions: x_range={x_range}, y_range={y_range}. "
            "Both must be positive."
        )
    
    if not 0.0 < roughness <= 1.0:
        raise ValueError(f"roughness must be in (0, 1], got {roughness}")
    
    # Calculate fitting radius
    # This represents 3 times the diagonal distance divided by sqrt(num_points - 1)
    # The factor of 3 ensures adequate local neighborhood for fitting
    diagonal = np.sqrt(x_range**2 + y_range**2)
    r_fit = 3.0 * diagonal / np.sqrt(float(num_points - 1))
    
    # Calculate point density (points per 100 square Angstroms)
    area = x_range * y_range
    density = (num_points - 1) * 100.0 / area
    
    # Calculate smoothing parameter alpha
    # Empirical formula calibrated for optimal surface fitting
    # Higher density -> higher alpha -> more smoothing
    # Roughness parameter allows user to modulate this effect
    log_density = np.log(density)
    alpha = np.exp(0.4247 * roughness * log_density - 1.3501 / roughness)
    
    return float(r_fit), float(alpha)


def calculate_grid_parameters_spherical(
    radius_mean: float,
    num_points: int,
    roughness: float = 1.0
) -> Tuple[float, float]:
    """
    Calculate grid parameters for spherical coordinate systems.
    
    This function computes the fitting radius (r_fit) and smoothing parameter (alpha)
    for a spherical grid based on the mean radius and number of grid points.
    
    Mathematical formulation:
        r_fit = 6 * radius_mean * pi / sqrt(num_points - 1)
        
        surface_area = 4 * pi * radius_mean^2
        density = (num_points - 1) * 100 / surface_area
        alpha = exp(0.4984 * roughness * log(density) - 1.06016110229 / roughness)
    
    Args:
        radius_mean: Mean radius of the spherical surface (Angstroms)
        num_points: Number of grid points to be used
        roughness: Surface roughness parameter (0.0 to 1.0, default 1.0)
                  1.0 = keep 100% of original roughness
                  0.5 = keep 50% of original roughness (smoother)
    
    Returns:
        Tuple containing:
            - r_fit: Fitting radius for local surface approximation (Angstroms)
            - alpha: Smoothing parameter (dimensionless)
    
    Raises:
        ValueError: If num_points < 2 or radius_mean <= 0
    
    Notes:
        - Fitting radius accounts for spherical geometry (factor of 6*pi)
        - Alpha coefficients (0.4984, 1.06016110229) differ from Cartesian case
        - These coefficients are empirically optimized for spherical surfaces
        - Original Fortran implementation in funcproc.f90, subroutine param_esf
    
    Example:
        >>> r_fit, alpha = calculate_grid_parameters_spherical(
        ...     radius_mean=50.0, num_points=1000, roughness=1.0
        ... )
        >>> print(f"Fitting radius: {r_fit:.3f} A")
        >>> print(f"Smoothing parameter: {alpha:.3f}")
    """
    # Validate inputs
    if num_points < 2:
        raise ValueError(f"num_points must be >= 2, got {num_points}")
    
    if radius_mean <= 0:
        raise ValueError(f"radius_mean must be positive, got {radius_mean}")
    
    if not 0.0 < roughness <= 1.0:
        raise ValueError(f"roughness must be in (0, 1], got {roughness}")
    
    # Calculate fitting radius for spherical geometry
    # Factor of 6*pi accounts for spherical surface curvature
    r_fit = 6.0 * radius_mean * np.pi / np.sqrt(float(num_points - 1))
    
    # Calculate point density on spherical surface
    # Surface area of sphere = 4 * pi * r^2
    surface_area = 4.0 * np.pi * radius_mean**2
    density = (num_points - 1) * 100.0 / surface_area
    
    # Calculate smoothing parameter alpha for spherical geometry
    # Different empirical coefficients than Cartesian case
    # 0.4984 and 1.06016110229 are calibrated for spherical surfaces
    log_density = np.log(density)
    alpha = np.exp(0.4984 * roughness * log_density - 1.06016110229 / roughness)
    
    return float(r_fit), float(alpha)


def calculate_bin_size_cartesian(n_index: int, user_bin: int = None) -> Tuple[int, int]:
    """
    Calculate optimal bin size for Cartesian grid discretization.
    
    Determines the number of bins (grid divisions) along each axis for a
    rectangular grid, based on the number of index points.
    
    Args:
        n_index: Number of index points defining the surface
        user_bin: User-specified bin size (optional). If None, calculates automatically.
    
    Returns:
        Tuple containing:
            - bin_coarse: Bin size for coarse grid
            - n_grid: Bin size for standard grid (same as user_bin if provided)
    
    Notes:
        - Default calculation: n_grid = round(sqrt(n_index - 1) - 1)
        - Coarse grid is always calculated the same way
        - Original Fortran: def_bin subroutine in funcproc.f90
    
    Example:
        >>> bin_coarse, n_grid = calculate_bin_size_cartesian(1000)
        >>> print(f"Grid size: {n_grid} x {n_grid}")
    """
    if n_index < 2:
        raise ValueError(f"n_index must be >= 2, got {n_index}")
    
    # Calculate coarse bin size
    # Formula: round(sqrt(n_index - 1) - 1)
    bin_coarse = int(np.round(np.sqrt(float(n_index - 1)) - 1.0))
    
    # Use user-specified bin size or calculate default
    if user_bin is None:
        n_grid = bin_coarse
        print(f"\nSTD_BIN = {n_grid}")
    else:
        n_grid = user_bin
    
    return bin_coarse, n_grid


def calculate_bin_size_spherical(n_index: int, user_bin: int = None) -> Tuple[int, int]:
    """
    Calculate optimal bin size for spherical grid discretization.
    
    Determines the number of bins for a spherical grid based on the number
    of index points. Accounts for spherical geometry (factor of 2).
    
    Args:
        n_index: Number of index points defining the surface
        user_bin: User-specified bin size (optional). If None, calculates automatically.
    
    Returns:
        Tuple containing:
            - bin_coarse: Bin size for coarse grid
            - n_grid: Bin size for standard grid (same as user_bin if provided)
    
    Notes:
        - Default calculation: n_grid = round(sqrt(2 * (n_index - 1)))
        - Factor of 2 accounts for spherical surface area vs. rectangular
        - Original Fortran: def_bin_sph subroutine in funcproc.f90
    
    Example:
        >>> bin_coarse, n_grid = calculate_bin_size_spherical(1000)
        >>> print(f"Spherical grid size: {n_grid}")
    """
    if n_index < 2:
        raise ValueError(f"n_index must be >= 2, got {n_index}")
    
    # Calculate coarse bin size for spherical geometry
    # Formula: round(sqrt(2 * (n_index - 1)))
    # Factor of 2 accounts for spherical vs rectangular surface area
    bin_coarse = int(np.round(np.sqrt(2.0 * float(n_index - 1))))
    
    # Use user-specified bin size or calculate default
    if user_bin is None:
        n_grid = bin_coarse
        print(f"\nSTD_BIN = {n_grid}")
    else:
        n_grid = user_bin
    
    return bin_coarse, n_grid
