"""
Statistical analysis functions for pySuAVE.

This module provides comprehensive statistical analysis including descriptive
statistics, histograms, autocorrelation, and distribution fitting.

Fortran equivalent: calc_stat_aver, do_histogram, calc_stat_all, calc_acf in funcproc.f90
"""

import numpy as np
import numpy.typing as npt
from typing import Tuple, Dict
from dataclasses import dataclass


@dataclass
class StatisticalSummary:
    """Container for statistical summary results."""
    mean: float
    std_dev: float
    skewness: float
    kurtosis: float
    median: float
    mode: float
    q1: float  # First quartile (25th percentile)
    q3: float  # Third quartile (75th percentile)
    d1: float  # First decile (10th percentile)
    d9: float  # Ninth decile (90th percentile)
    min_value: float
    max_value: float
    n_points: int


def calculate_basic_statistics(
    data: npt.NDArray[np.float64]
) -> Tuple[float, float, float, float]:
    """
    Calculate basic statistical moments (mean, std dev, skewness, kurtosis).
    
    Args:
        data: Input data array
    
    Returns:
        Tuple of (mean, std_dev, skewness, kurtosis)
    
    Notes:
        - Original Fortran: calc_stat_aver subroutine in funcproc.f90
    
    Example:
        >>> data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        >>> mean, std, skew, kurt = calculate_basic_statistics(data)
    """
    n = len(data)
    
    if n == 0:
        return 0.0, 0.0, 0.0, 0.0
    
    # Calculate mean
    # Fortran: aver = aver + func(i) / n_index
    mean = np.mean(data)
    
    # Calculate variance and std dev
    # Fortran: aver2 = aver2 + func(i)*func(i) / n_index
    #          desv = sqrt(aver2 - aver*aver)
    variance = np.var(data, ddof=0)  # Population variance
    std_dev = np.sqrt(variance)
    
    if std_dev == 0:
        return mean, 0.0, 0.0, 0.0
    
    # Calculate standardized moments
    # Fortran: st_mom = (func(i) - aver) / desv
    standardized = (data - mean) / std_dev
    
    # Calculate skewness (3rd moment)
    # Fortran: skew = skew + st_mom*st_mom*st_mom / n_index
    skewness = np.mean(standardized**3)
    
    # Calculate kurtosis (4th moment)
    # Fortran: kurt = kurt + st_mom*st_mom*st_mom*st_mom / n_index
    kurtosis = np.mean(standardized**4)
    
    return float(mean), float(std_dev), float(skewness), float(kurtosis)


def create_histogram(
    data: npt.NDArray[np.float64],
    n_bins: int = 1000,
    bin_offset: int = 100
) -> Tuple[npt.NDArray[np.float64], npt.NDArray[np.float64], float, float]:
    """
    Create histogram from data with Gaussian model overlay.
    
    Args:
        data: Input data array
        n_bins: Number of histogram bins (default: 1000)
        bin_offset: Offset for bin indexing (default: 100)
    
    Returns:
        Tuple of:
            - bin_centers: Center values of bins
            - histogram: Normalized histogram values (PDF)
            - min_value: Minimum data value
            - bin_width: Width of each bin
    
    Notes:
        - Histogram is normalized to form a probability density function
        - Original Fortran: do_histogram subroutine in funcproc.f90
    
    Example:
        >>> bins, hist, min_val, width = create_histogram(data)
    """
    if len(data) == 0:
        return np.array([]), np.array([]), 0.0, 0.0
    
    min_value = float(np.min(data))
    max_value = float(np.max(data))
    
    # Calculate bin width
    # Fortran: del = (maxf - minf) / 800
    # We use n_bins - 2*bin_offset to match Fortran behavior
    bin_width = (max_value - min_value) / (n_bins - 2 * bin_offset)
    
    if bin_width == 0:
        bin_width = 1.0
    
    # Initialize histogram
    histogram = np.zeros(n_bins, dtype=np.float64)
    
    # Fill histogram
    # Fortran: bini = nint((func(i) - minf) / del) + 100
    #          hist(bini) = hist(bini) + 1 / (n_index * del)
    for value in data:
        bin_index = int(np.round((value - min_value) / bin_width)) + bin_offset
        if 0 <= bin_index < n_bins:
            histogram[bin_index] += 1.0 / (len(data) * bin_width)
    
    # Create bin centers
    # Fortran: (i - 100) * del + minf
    bin_centers = np.array([(i - bin_offset) * bin_width + min_value 
                            for i in range(n_bins)])
    
    return bin_centers, histogram, min_value, bin_width


def gaussian_model(
    bin_centers: npt.NDArray[np.float64],
    mean: float,
    std_dev: float
) -> npt.NDArray[np.float64]:
    """
    Calculate Gaussian (normal) distribution model.
    
    Args:
        bin_centers: X values for evaluation
        mean: Mean of distribution
        std_dev: Standard deviation
    
    Returns:
        Gaussian PDF values at bin_centers
    
    Notes:
        - Formula: PDF(x) = exp(-(x-mean)^2 / (2*std^2)) / (std*sqrt(2*pi))
        - Original Fortran: Gaussian model in do_histogram
    """
    if std_dev == 0:
        return np.zeros_like(bin_centers)
    
    # Fortran: aux = exp(-(aux - aver)*(aux - aver) / (2*desv*desv))
    #          aux = aux / (desv * sqrt(2*pi))
    gaussian = np.exp(-(bin_centers - mean)**2 / (2 * std_dev**2))
    gaussian = gaussian / (std_dev * np.sqrt(2 * np.pi))
    
    return gaussian


def calculate_percentiles(
    data: npt.NDArray[np.float64],
    histogram: npt.NDArray[np.float64],
    bin_centers: npt.NDArray[np.float64],
    bin_width: float
) -> Dict[str, float]:
    """
    Calculate median, mode, quartiles, and deciles from histogram.
    
    Args:
        data: Original data
        histogram: Histogram values
        bin_centers: Bin center values
        bin_width: Width of bins
    
    Returns:
        Dictionary with keys: median, mode, q1, q3, d1, d9
    
    Notes:
        - Uses cumulative distribution from histogram
        - Original Fortran: calc_stat_all subroutine in funcproc.f90
    """
    n = len(data)
    
    # Find mode (bin with highest frequency)
    # Fortran: if (hist(i) > hist(class_modal)) class_modal = i
    mode_index = int(np.argmax(histogram))
    mode = float(bin_centers[mode_index])
    
    # Calculate cumulative distribution
    cumsum = 0.0
    median = 0.0
    q1 = 0.0  # 25th percentile
    q3 = 0.0  # 75th percentile
    d1 = 0.0  # 10th percentile
    d9 = 0.0  # 90th percentile
    
    median_found = False
    q1_found = False
    q3_found = False
    d1_found = False
    d9_found = False
    
    for i in range(len(histogram)):
        cumsum += histogram[i] * bin_width * n
        
        # Median (50th percentile)
        if not median_found and cumsum >= n / 2:
            median = bin_centers[i]
            median_found = True
        
        # First quartile (25th percentile)
        if not q1_found and cumsum >= n / 4:
            q1 = bin_centers[i]
            q1_found = True
        
        # Third quartile (75th percentile)
        if not q3_found and cumsum >= 3 * n / 4:
            q3 = bin_centers[i]
            q3_found = True
        
        # First decile (10th percentile)
        if not d1_found and cumsum >= n / 10:
            d1 = bin_centers[i]
            d1_found = True
        
        # Ninth decile (90th percentile)
        if not d9_found and cumsum >= 9 * n / 10:
            d9 = bin_centers[i]
            d9_found = True
    
    return {
        'median': median,
        'mode': mode,
        'q1': q1,
        'q3': q3,
        'd1': d1,
        'd9': d9
    }


def calculate_autocorrelation(
    data: npt.NDArray[np.float64],
    max_lag: Optional[int] = None
) -> npt.NDArray[np.float64]:
    """
    Calculate autocorrelation function.
    
    Args:
        data: Input time series data
        max_lag: Maximum lag to calculate (default: len(data)//2)
    
    Returns:
        Autocorrelation values for each lag
    
    Notes:
        - ACF(lag) = sum((x_i - mean) * (x_{i+lag} - mean)) / (n/2 * var)
        - Original Fortran: calc_acf subroutine in funcproc.f90
    
    Example:
        >>> acf = calculate_autocorrelation(data)
    """
    n = len(data)
    
    if n == 0:
        return np.array([])
    
    if max_lag is None:
        max_lag = n // 2
    
    mean = np.mean(data)
    variance = np.var(data, ddof=0)
    
    if variance == 0:
        return np.zeros(max_lag)
    
    acf = np.zeros(max_lag)
    
    # Fortran: do j=1, int(n_index/2)
    #            acf = 0
    #            do i=1, int(n_index/2)
    #              acf = acf + (func(i) - aver) * (func(i+j) - aver) / (int(n_index/2) * desv * desv)
    for lag in range(max_lag):
        correlation = 0.0
        for i in range(n // 2):
            if i + lag < n:
                correlation += (data[i] - mean) * (data[i + lag] - mean)
        
        acf[lag] = correlation / ((n // 2) * variance)
    
    return acf


def comprehensive_statistics(
    data: npt.NDArray[np.float64]
) -> StatisticalSummary:
    """
    Calculate comprehensive statistical summary.
    
    Args:
        data: Input data array
    
    Returns:
        StatisticalSummary object with all statistics
    
    Example:
        >>> stats = comprehensive_statistics(data)
        >>> print(f"Mean: {stats.mean:.3f} +/- {stats.std_dev:.3f}")
        >>> print(f"Median: {stats.median:.3f}")
    """
    if len(data) == 0:
        return StatisticalSummary(
            mean=0.0, std_dev=0.0, skewness=0.0, kurtosis=0.0,
            median=0.0, mode=0.0, q1=0.0, q3=0.0, d1=0.0, d9=0.0,
            min_value=0.0, max_value=0.0, n_points=0
        )
    
    # Basic statistics
    mean, std_dev, skewness, kurtosis = calculate_basic_statistics(data)
    
    # Histogram and percentiles
    bin_centers, histogram, min_value, bin_width = create_histogram(data)
    percentiles = calculate_percentiles(data, histogram, bin_centers, bin_width)
    
    return StatisticalSummary(
        mean=mean,
        std_dev=std_dev,
        skewness=skewness,
        kurtosis=kurtosis,
        median=percentiles['median'],
        mode=percentiles['mode'],
        q1=percentiles['q1'],
        q3=percentiles['q3'],
        d1=percentiles['d1'],
        d9=percentiles['d9'],
        min_value=float(np.min(data)),
        max_value=float(np.max(data)),
        n_points=len(data)
    )
