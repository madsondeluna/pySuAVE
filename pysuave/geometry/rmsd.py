"""
RMSD (Root Mean Square Deviation) calculation functions for pySuAVE.

This module provides functions to calculate RMSD between fitted grid surfaces
and original atomic coordinates. RMSD is used to assess the quality of the
surface fitting procedure.

Fortran equivalent: calc_rmsd, calc_rmsd_sph, calc_rmsd_inert in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import List

from pysuave.core.types import AtomData, Coordinate3D, SphericalCoordinate


def calculate_rmsd_cartesian(
    atoms1: List[AtomData],
    atoms2: List[AtomData],
    grid1: npt.NDArray[np.float64],
    grid2: npt.NDArray[np.float64],
    x_min: float,
    y_min: float,
    dx: float,
    dy: float
) -> float:
    """
    Calculate RMSD between atomic coordinates and fitted grid surfaces (Cartesian).
    
    This function computes the root mean square deviation between the z-coordinates
    of atoms and their corresponding positions on fitted grid surfaces. It measures
    how well the grid approximates the actual atomic surface.
    
    Mathematical formulation:
        For each atom at (x, y, z):
            1. Find grid indices: i = round((x - x_min) / dx), j = round((y - y_min) / dy)
            2. Get grid z-value: z_grid = grid[i, j]
            3. Calculate deviation: delta_z = z - z_grid
        
        RMSD = sqrt(sum(delta_z^2) / (n1 + n2))
    
    Args:
        atoms1: First set of atoms (e.g., upper leaflet)
        atoms2: Second set of atoms (e.g., lower leaflet)
        grid1: Fitted grid for first atom set, shape (n_grid, n_grid)
               Contains z-coordinates at each grid point
        grid2: Fitted grid for second atom set, shape (n_grid, n_grid)
               Contains z-coordinates at each grid point
        x_min: Minimum x coordinate of the grid (Angstroms)
        y_min: Minimum y coordinate of the grid (Angstroms)
        dx: Grid spacing in x direction (Angstroms)
        dy: Grid spacing in y direction (Angstroms)
    
    Returns:
        RMSD value in Angstroms
    
    Notes:
        - Grid indices are 0-based in Python (1-based in original Fortran)
        - RMSD is normalized by total number of atoms (n1 + n2)
        - Lower RMSD indicates better surface fitting
        - Typical good values: RMSD < 1.0 Angstrom
        - Original Fortran: calc_rmsd function in funcproc.f90
    
    Raises:
        ValueError: If grid dimensions don't match or if atoms fall outside grid
    
    Example:
        >>> rmsd = calculate_rmsd_cartesian(
        ...     atoms1, atoms2, grid1, grid2,
        ...     x_min=0.0, y_min=0.0, dx=1.0, dy=1.0
        ... )
        >>> print(f"Surface fitting RMSD: {rmsd:.3f} A")
    """
    if len(atoms1) == 0 and len(atoms2) == 0:
        raise ValueError("No atoms provided for RMSD calculation")
    
    # Initialize sum of squared deviations
    sum_squared_dev = 0.0
    total_atoms = len(atoms1) + len(atoms2)
    
    # Process first atom set
    for atom in atoms1:
        # Calculate grid indices (0-based)
        # Fortran: a = nint((store(i)%x - x_min) / dx) + 1
        # Python:  a = round((atom.x - x_min) / dx)
        i = int(np.round((atom.x - x_min) / dx))
        j = int(np.round((atom.y - y_min) / dy))
        
        # Validate indices
        if i < 0 or i >= grid1.shape[0] or j < 0 or j >= grid1.shape[1]:
            raise ValueError(
                f"Atom at ({atom.x}, {atom.y}) falls outside grid bounds. "
                f"Grid indices: ({i}, {j}), Grid shape: {grid1.shape}"
            )
        
        # Calculate z-deviation
        # grid1[i, j] contains the z-coordinate at this grid point
        delta_z = atom.z - grid1[i, j]
        sum_squared_dev += delta_z * delta_z
    
    # Process second atom set
    for atom in atoms2:
        # Calculate grid indices (0-based)
        i = int(np.round((atom.x - x_min) / dx))
        j = int(np.round((atom.y - y_min) / dy))
        
        # Validate indices
        if i < 0 or i >= grid2.shape[0] or j < 0 or j >= grid2.shape[1]:
            raise ValueError(
                f"Atom at ({atom.x}, {atom.y}) falls outside grid bounds. "
                f"Grid indices: ({i}, {j}), Grid shape: {grid2.shape}"
            )
        
        # Calculate z-deviation
        delta_z = atom.z - grid2[i, j]
        sum_squared_dev += delta_z * delta_z
    
    # Calculate RMSD
    # Normalize by total number of atoms
    rmsd = np.sqrt(sum_squared_dev / total_atoms)
    
    return float(rmsd)


def calculate_rmsd_spherical(
    coords1: List[SphericalCoordinate],
    coords2: List[SphericalCoordinate],
    grid1: npt.NDArray[np.float64],
    grid2: npt.NDArray[np.float64],
    dphi: float,
    dtheta: float
) -> float:
    """
    Calculate RMSD between coordinates and fitted grid surfaces (Spherical).
    
    This function computes the root mean square deviation between the radial
    coordinates (rho) and their corresponding positions on fitted spherical grids.
    
    Mathematical formulation:
        For each coordinate at (rho, phi, theta):
            1. Find grid indices: i = round(phi / dphi), j = round(theta / dtheta)
            2. Get grid rho-value: rho_grid = grid[i, j]
            3. Calculate deviation: delta_rho = rho - rho_grid
        
        RMSD = sqrt(sum(delta_rho^2) / (n1 + n2))
    
    Args:
        coords1: First set of spherical coordinates
        coords2: Second set of spherical coordinates
        grid1: Fitted grid for first coordinate set, shape (n_grid, n_grid)
               Contains rho values at each (phi, theta) grid point
        grid2: Fitted grid for second coordinate set, shape (n_grid, n_grid)
               Contains rho values at each (phi, theta) grid point
        dphi: Grid spacing in phi direction (radians)
        dtheta: Grid spacing in theta direction (radians)
    
    Returns:
        RMSD value in Angstroms (same units as rho)
    
    Notes:
        - Phi and theta are in radians
        - Grid stores radial distances (rho) at each angular position
        - Original Fortran: calc_rmsd_sph function in funcproc.f90
    
    Example:
        >>> rmsd = calculate_rmsd_spherical(
        ...     coords1, coords2, grid1, grid2,
        ...     dphi=0.1, dtheta=0.1
        ... )
        >>> print(f"Spherical surface RMSD: {rmsd:.3f} A")
    """
    if len(coords1) == 0 and len(coords2) == 0:
        raise ValueError("No coordinates provided for RMSD calculation")
    
    sum_squared_dev = 0.0
    total_coords = len(coords1) + len(coords2)
    
    # Process first coordinate set
    for coord in coords1:
        # Calculate grid indices (0-based)
        # Fortran: a = nint(store(i)%phi / dph) + 1
        # Python:  a = round(coord.phi / dphi)
        i = int(np.round(coord.phi / dphi))
        j = int(np.round(coord.theta / dtheta))
        
        # Validate indices
        if i < 0 or i >= grid1.shape[0] or j < 0 or j >= grid1.shape[1]:
            raise ValueError(
                f"Coordinate at (phi={coord.phi}, theta={coord.theta}) "
                f"falls outside grid bounds. Grid indices: ({i}, {j}), "
                f"Grid shape: {grid1.shape}"
            )
        
        # Calculate radial deviation
        delta_rho = coord.rho - grid1[i, j]
        sum_squared_dev += delta_rho * delta_rho
    
    # Process second coordinate set
    for coord in coords2:
        i = int(np.round(coord.phi / dphi))
        j = int(np.round(coord.theta / dtheta))
        
        # Validate indices
        if i < 0 or i >= grid2.shape[0] or j < 0 or j >= grid2.shape[1]:
            raise ValueError(
                f"Coordinate at (phi={coord.phi}, theta={coord.theta}) "
                f"falls outside grid bounds. Grid indices: ({i}, {j}), "
                f"Grid shape: {grid2.shape}"
            )
        
        delta_rho = coord.rho - grid2[i, j]
        sum_squared_dev += delta_rho * delta_rho
    
    # Calculate RMSD
    rmsd = np.sqrt(sum_squared_dev / total_coords)
    
    return float(rmsd)


def calculate_rmsd_inertia(
    coords: List[SphericalCoordinate],
    grid: npt.NDArray[np.float64],
    dz: float,
    dtheta: float
) -> float:
    """
    Calculate RMSD for inertia-based coordinate system.
    
    This is a specialized RMSD calculation for the s_inertia program,
    which uses a modified coordinate system based on principal axes.
    
    Mathematical formulation:
        For each coordinate at (rho, phi, theta):
            1. Calculate modified index: i = round((cos(phi) + 1) / dz + 0.5)
            2. Calculate theta index: j = round(theta / dtheta)
            3. Get grid rho-value: rho_grid = grid[i, j]
            4. Calculate deviation: delta_rho = rho - rho_grid
        
        RMSD = sqrt(sum(delta_rho^2) / n)
    
    Args:
        coords: Spherical coordinates in inertia frame
        grid: Fitted grid, shape (n_grid, n_grid)
              Contains rho values at each grid point
        dz: Grid spacing in z direction (modified coordinate)
        dtheta: Grid spacing in theta direction (radians)
    
    Returns:
        RMSD value in Angstroms
    
    Notes:
        - Uses modified indexing: i = round((cos(phi) + 1) / dz + 0.5)
        - This accounts for the principal axis transformation
        - Only used in s_inertia program
        - Original Fortran: calc_rmsd_inert function in funcproc.f90
    
    Example:
        >>> rmsd = calculate_rmsd_inertia(coords, grid, dz=0.1, dtheta=0.1)
        >>> print(f"Inertia frame RMSD: {rmsd:.3f} A")
    """
    if len(coords) == 0:
        raise ValueError("No coordinates provided for RMSD calculation")
    
    sum_squared_dev = 0.0
    
    for coord in coords:
        # Calculate modified grid index for inertia frame
        # Fortran: a = nint((cos(store(i)%phi) + 1) / dz + 1/2)
        # The cos(phi) + 1 maps [-1, 1] to [0, 2]
        # Adding 0.5 before rounding is equivalent to Fortran's nint
        i = int(np.round((np.cos(coord.phi) + 1.0) / dz + 0.5))
        j = int(np.round(coord.theta / dtheta))
        
        # Validate indices
        if i < 0 or i >= grid.shape[0] or j < 0 or j >= grid.shape[1]:
            raise ValueError(
                f"Coordinate at (phi={coord.phi}, theta={coord.theta}) "
                f"falls outside grid bounds. Grid indices: ({i}, {j}), "
                f"Grid shape: {grid.shape}"
            )
        
        # Calculate radial deviation
        delta_rho = coord.rho - grid[i, j]
        sum_squared_dev += delta_rho * delta_rho
    
    # Calculate RMSD
    # Note: Normalized by number of coordinates (not doubled like other functions)
    rmsd = np.sqrt(sum_squared_dev / len(coords))
    
    return float(rmsd)
