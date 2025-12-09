"""Core constants used throughout pySuAVE."""

import numpy as np

# Mathematical constants
PI = np.pi
TWO_PI = 2.0 * np.pi
FOUR_PI = 4.0 * np.pi

# Version information
VERSION = "2.24.07"  # Matching Fortran version
PYTHON_VERSION = "0.1.0"

# Physical constants
ANGSTROM_TO_NM = 0.1
NM_TO_ANGSTROM = 10.0

# Numerical tolerances
EPSILON = 1e-10
FLOAT_TOLERANCE = 1e-6

# Default grid parameters
DEFAULT_GRID_SIZE = 1001
MAX_GRID_SIZE = 1001
DEFAULT_BIN_SIZE = 100

# Array size limits (from Fortran)
MAX_ATOMS = 1_000_000
MAX_INDEX = 500_000
MAX_STORE = 50_000
MAX_COARSE = 50_000
MAX_GRID_POINTS = 1001

# File extensions
PDB_EXT = ".pdb"
NDX_EXT = ".ndx"
XTC_EXT = ".xtc"
TRR_EXT = ".trr"
GRO_EXT = ".gro"
