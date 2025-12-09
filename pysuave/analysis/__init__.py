"""Analysis module initialization."""

from pysuave.analysis.density import (
    calculate_density_profile_spherical,
    calculate_density_profile_with_grid,
)
from pysuave.analysis.order import (
    calculate_order_parameter_cartesian,
    calculate_order_parameter_spherical,
)
from pysuave.analysis.thickness import (
    calculate_thickness_cartesian,
    calculate_thickness_spherical,
)
from pysuave.analysis.topography import (
    calculate_topography,
    calculate_moment_of_inertia,
)
from pysuave.analysis.statistics import (
    StatisticalSummary,
    calculate_basic_statistics,
    create_histogram,
    gaussian_model,
    calculate_percentiles,
    calculate_autocorrelation,
    comprehensive_statistics,
)

__all__ = [
    "calculate_density_profile_spherical",
    "calculate_density_profile_with_grid",
    "calculate_order_parameter_cartesian",
    "calculate_order_parameter_spherical",
    "calculate_thickness_cartesian",
    "calculate_thickness_spherical",
    "calculate_topography",
    "calculate_moment_of_inertia",
    "StatisticalSummary",
    "calculate_basic_statistics",
    "create_histogram",
    "gaussian_model",
    "calculate_percentiles",
    "calculate_autocorrelation",
    "comprehensive_statistics",
]
