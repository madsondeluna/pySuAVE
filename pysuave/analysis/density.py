"""
Density calculation functions for pySuAVE.

This module provides functions for calculating density profiles in spherical
coordinate systems. Density is calculated by binning particles into radial
shells and normalizing by shell volume.

Fortran equivalent: calc_dens_sph in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import List

from pysuave.core.types import SphericalCoordinate


def calculate_density_profile_spherical(
    density_coords: List[SphericalCoordinate],
    grid1: npt.NDArray[np.float64],
    grid2: npt.NDArray[np.float64],
    dphi: float,
    dtheta: float,
    n_divisions: int,
    total_volume: float
) -> npt.NDArray[np.float64]:
    """
    Calculate radial density profile for spherical surfaces.
    
    This function computes a density profile by binning particles into radial
    shells relative to a reference surface. The density is normalized by the
    volume of each shell.
    
    Mathematical approach:
        1. For each particle, find corresponding grid point using (phi, theta)
        2. Calculate average radius at that grid point: r_avg = (r1 + r2) / 2
        3. Normalize particle radius: r_norm = r_particle / r_avg
        4. Bin into radial shells
        5. Normalize by shell volume: rho = count / (V_total * (r_outer^3 - r_inner^3))
    
    Args:
        density_coords: List of particle coordinates in spherical system
        grid1: First surface grid, shape (n_grid, n_grid, 3)
               grid[i, j] = [rho, phi, theta]
        grid2: Second surface grid, shape (n_grid, n_grid, 3)
               grid[i, j] = [rho, phi, theta]
        dphi: Grid spacing in phi direction (radians)
        dtheta: Grid spacing in theta direction (radians)
        n_divisions: Number of radial divisions for binning
        total_volume: Total volume for normalization (cubic Angstroms)
    
    Returns:
        Density histogram array, shape (1000,)
        Centered at index 500, covering range from -1 to +1 in normalized radius
    
    Notes:
        - Histogram is centered at index 500
        - Bins cover normalized radius range: r_norm = r_particle / r_avg
        - Density units: particles per 1000 cubic Angstroms
        - Shell volume: V_shell = V_total * (r_outer^3 - r_inner^3)
        - Original Fortran: calc_dens_sph subroutine in funcproc.f90
    
    Mathematical formulation:
        For each particle i:
            1. Find grid indices: a = round(phi_i / dphi), b = round(theta_i / dtheta)
            2. r_avg = (grid1[a,b].rho + grid2[a,b].rho) / 2
            3. bin_width = 2.0 / n_divisions
            4. r_norm = r_i / r_avg
            5. bin_index = int(r_norm / bin_width)
            6. r_inner = bin_index * bin_width
            7. r_outer = (bin_index + 1) * bin_width
            8. V_shell = V_total * (r_outer^3 - r_inner^3)
            9. density[bin_index + 500] += 1000 / V_shell
    
    Example:
        >>> coords = [SphericalCoordinate(50.0, 1.5, 2.0), ...]
        >>> density = calculate_density_profile_spherical(
        ...     coords, grid1, grid2, dphi=0.1, dtheta=0.1,
        ...     n_divisions=100, total_volume=1000.0
        ... )
        >>> print(f"Density at center: {density[500]:.3f}")
    """
    # Validate inputs
    if len(density_coords) == 0:
        raise ValueError("No density coordinates provided")
    
    if grid1.shape != grid2.shape:
        raise ValueError(
            f"Grid shapes must match: grid1={grid1.shape}, grid2={grid2.shape}"
        )
    
    if n_divisions <= 0:
        raise ValueError(f"n_divisions must be positive, got {n_divisions}")
    
    if total_volume <= 0:
        raise ValueError(f"total_volume must be positive, got {total_volume}")
    
    # Initialize histogram
    # Fortran: hist(1000)
    # Centered at index 500 to allow negative and positive deviations
    histogram = np.zeros(1000, dtype=np.float64)
    
    # Calculate bin width
    # Fortran: del = 2.0 / div
    # Range is [-1, +1] in normalized radius
    bin_width = 2.0 / n_divisions
    
    # Process each particle
    # Fortran: do i=1, a_dens - 1
    for coord in density_coords:
        # Find grid indices based on angular coordinates
        # Fortran: a = nint((dens(i)%phi) / dph) + 1
        #          b = nint((dens(i)%theta) / dth) + 1
        # Python: 0-indexed
        a = int(np.round(coord.phi / dphi))
        b = int(np.round(coord.theta / dtheta))
        
        # Validate indices
        if a < 0 or a >= grid1.shape[0] or b < 0 or b >= grid1.shape[1]:
            # Skip particles outside grid
            continue
        
        # Calculate average radius at this grid point
        # Fortran: rad_aver = (grid(a,b)%rho + grid2(a,b)%rho) / 2
        r_avg = (grid1[a, b, 0] + grid2[a, b, 0]) / 2.0
        
        if r_avg <= 0:
            # Skip if average radius is invalid
            continue
        
        # Calculate normalized radius
        # r_norm = r_particle / r_avg
        r_norm = coord.rho / r_avg
        
        # Calculate bin index
        # Fortran: bini = int((dens(i)%rho / rad_aver) / del)
        bin_index = int(r_norm / bin_width)
        
        # Calculate shell boundaries in normalized coordinates
        # Fortran: k_inf = bini * del
        #          k_sup = bini * del + del
        r_inner = bin_index * bin_width
        r_outer = (bin_index + 1) * bin_width
        
        # Calculate shell volume
        # V_shell = V_total * (r_outer^3 - r_inner^3)
        # This is the volume of the spherical shell in normalized coordinates
        shell_volume = total_volume * (r_outer**3 - r_inner**3)
        
        if shell_volume <= 0:
            # Skip if shell volume is invalid
            continue
        
        # Add to histogram
        # Fortran: hist(bini+500) = hist(bini+500) + 1*1000/(s_vol*(k_sup**3 - k_inf**3))
        # Factor of 1000 converts to density per 1000 cubic Angstroms
        # Centered at index 500 to allow negative bins
        hist_index = bin_index + 500
        
        # Validate histogram index
        if 0 <= hist_index < 1000:
            histogram[hist_index] += 1000.0 / shell_volume
    
    return histogram


def calculate_density_profile_with_grid(
    density_coords: List[SphericalCoordinate],
    grid1_spherical: npt.NDArray[np.float64],
    grid2_spherical: npt.NDArray[np.float64],
    dphi: float,
    dtheta: float,
    n_divisions: int = 100
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """
    Calculate density profile and return both histogram and radial bins.
    
    This is a convenience wrapper around calculate_density_profile_spherical
    that also returns the radial bin centers for plotting.
    
    Args:
        density_coords: List of particle coordinates
        grid1_spherical: First surface grid (rho, phi, theta)
        grid2_spherical: Second surface grid (rho, phi, theta)
        dphi: Grid spacing in phi (radians)
        dtheta: Grid spacing in theta (radians)
        n_divisions: Number of radial divisions (default: 100)
    
    Returns:
        Tuple of:
            - histogram: Density values, shape (1000,)
            - radial_bins: Radial bin centers in normalized coordinates, shape (1000,)
    
    Example:
        >>> hist, bins = calculate_density_profile_with_grid(
        ...     coords, grid1, grid2, dphi=0.1, dtheta=0.1
        ... )
        >>> import matplotlib.pyplot as plt
        >>> plt.plot(bins, hist)
        >>> plt.xlabel('Normalized radius')
        >>> plt.ylabel('Density (per 1000 A^3)')
    """
    # Estimate total volume from grid
    # Simple approximation: use mean radius
    mean_r1 = np.mean(grid1_spherical[:, :, 0])
    mean_r2 = np.mean(grid2_spherical[:, :, 0])
    mean_r = (mean_r1 + mean_r2) / 2.0
    
    # Approximate volume as spherical shell
    total_volume = (4.0 / 3.0) * np.pi * (mean_r1**3 - mean_r2**3)
    total_volume = abs(total_volume)
    
    # Calculate density profile
    histogram = calculate_density_profile_spherical(
        density_coords,
        grid1_spherical,
        grid2_spherical,
        dphi,
        dtheta,
        n_divisions,
        total_volume
    )
    
    # Create radial bin centers
    # Bins are centered at 500, with width = 2.0 / n_divisions
    bin_width = 2.0 / n_divisions
    radial_bins = np.array([(i - 500) * bin_width + bin_width/2 for i in range(1000)])
    
    return histogram, radial_bins
