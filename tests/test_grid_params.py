"""Tests for geometry functions - grid parameters."""

import numpy as np
import pytest

from pysuave.geometry.grid_params import (
    calculate_grid_parameters_cartesian,
    calculate_grid_parameters_spherical,
    calculate_bin_size_cartesian,
    calculate_bin_size_spherical,
)


class TestGridParametersCartesian:
    """Test Cartesian grid parameter calculations."""
    
    def test_basic_calculation(self):
        """Test basic grid parameter calculation."""
        r_fit, alpha = calculate_grid_parameters_cartesian(
            x_max=100.0, x_min=0.0,
            y_max=100.0, y_min=0.0,
            num_points=1000,
            roughness=1.0
        )
        
        # r_fit should be positive
        assert r_fit > 0
        
        # alpha should be positive
        assert alpha > 0
        
        # For a 100x100 box with 1000 points, r_fit should be reasonable
        assert 1.0 < r_fit < 50.0
    
    def test_roughness_effect(self):
        """Test that roughness parameter affects alpha."""
        r_fit1, alpha1 = calculate_grid_parameters_cartesian(
            x_max=100.0, x_min=0.0,
            y_max=100.0, y_min=0.0,
            num_points=1000,
            roughness=1.0
        )
        
        r_fit2, alpha2 = calculate_grid_parameters_cartesian(
            x_max=100.0, x_min=0.0,
            y_max=100.0, y_min=0.0,
            num_points=1000,
            roughness=0.5
        )
        
        # r_fit should be the same (doesn't depend on roughness)
        assert r_fit1 == pytest.approx(r_fit2)
        
        # alpha should be different
        assert alpha1 != alpha2
    
    def test_invalid_inputs(self):
        """Test validation of invalid inputs."""
        # num_points < 2
        with pytest.raises(ValueError):
            calculate_grid_parameters_cartesian(
                x_max=100.0, x_min=0.0,
                y_max=100.0, y_min=0.0,
                num_points=1,
                roughness=1.0
            )
        
        # Invalid dimensions
        with pytest.raises(ValueError):
            calculate_grid_parameters_cartesian(
                x_max=0.0, x_min=100.0,  # x_max < x_min
                y_max=100.0, y_min=0.0,
                num_points=1000,
                roughness=1.0
            )
        
        # Invalid roughness
        with pytest.raises(ValueError):
            calculate_grid_parameters_cartesian(
                x_max=100.0, x_min=0.0,
                y_max=100.0, y_min=0.0,
                num_points=1000,
                roughness=0.0  # Must be > 0
            )


class TestGridParametersSpherical:
    """Test spherical grid parameter calculations."""
    
    def test_basic_calculation(self):
        """Test basic spherical grid parameter calculation."""
        r_fit, alpha = calculate_grid_parameters_spherical(
            radius_mean=50.0,
            num_points=1000,
            roughness=1.0
        )
        
        # Both should be positive
        assert r_fit > 0
        assert alpha > 0
        
        # r_fit should scale with radius
        assert r_fit > 10.0
    
    def test_radius_scaling(self):
        """Test that r_fit scales with radius."""
        r_fit1, _ = calculate_grid_parameters_spherical(
            radius_mean=50.0,
            num_points=1000,
            roughness=1.0
        )
        
        r_fit2, _ = calculate_grid_parameters_spherical(
            radius_mean=100.0,
            num_points=1000,
            roughness=1.0
        )
        
        # r_fit should scale linearly with radius
        assert r_fit2 == pytest.approx(2.0 * r_fit1, rel=1e-6)
    
    def test_invalid_inputs(self):
        """Test validation of invalid inputs."""
        # Negative radius
        with pytest.raises(ValueError):
            calculate_grid_parameters_spherical(
                radius_mean=-10.0,
                num_points=1000,
                roughness=1.0
            )
        
        # num_points < 2
        with pytest.raises(ValueError):
            calculate_grid_parameters_spherical(
                radius_mean=50.0,
                num_points=1,
                roughness=1.0
            )


class TestBinSizeCalculations:
    """Test bin size calculation functions."""
    
    def test_cartesian_bin_size(self):
        """Test Cartesian bin size calculation."""
        bin_coarse, n_grid = calculate_bin_size_cartesian(n_index=1000)
        
        # Both should be positive integers
        assert bin_coarse > 0
        assert n_grid > 0
        
        # For 1000 points, bin size should be around sqrt(999) - 1
        expected = int(np.round(np.sqrt(999.0) - 1.0))
        assert bin_coarse == expected
        assert n_grid == expected
    
    def test_cartesian_user_bin(self):
        """Test Cartesian bin size with user-specified value."""
        bin_coarse, n_grid = calculate_bin_size_cartesian(
            n_index=1000,
            user_bin=50
        )
        
        # n_grid should match user input
        assert n_grid == 50
        
        # bin_coarse should still be calculated
        assert bin_coarse > 0
    
    def test_spherical_bin_size(self):
        """Test spherical bin size calculation."""
        bin_coarse, n_grid = calculate_bin_size_spherical(n_index=1000)
        
        # Both should be positive integers
        assert bin_coarse > 0
        assert n_grid > 0
        
        # For 1000 points, bin size should be around sqrt(2 * 999)
        expected = int(np.round(np.sqrt(2.0 * 999.0)))
        assert bin_coarse == expected
        assert n_grid == expected
    
    def test_spherical_user_bin(self):
        """Test spherical bin size with user-specified value."""
        bin_coarse, n_grid = calculate_bin_size_spherical(
            n_index=1000,
            user_bin=60
        )
        
        # n_grid should match user input
        assert n_grid == 60
        
        # bin_coarse should still be calculated
        assert bin_coarse > 0
    
    def test_invalid_n_index(self):
        """Test validation of invalid n_index."""
        with pytest.raises(ValueError):
            calculate_bin_size_cartesian(n_index=1)
        
        with pytest.raises(ValueError):
            calculate_bin_size_spherical(n_index=1)
