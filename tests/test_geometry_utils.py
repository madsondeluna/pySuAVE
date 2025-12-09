"""Tests for geometry utility functions."""

import numpy as np
import pytest

from pysuave.core.types import Coordinate3D
from pysuave.utils.geometry_utils import (
    calculate_solid_angle,
    calculate_cross_product,
    calculate_dot_product,
    calculate_vector_magnitude,
)


class TestVectorOperations:
    """Test basic vector operations."""
    
    def test_cross_product_orthogonal(self):
        """Test cross product of orthogonal vectors."""
        v1 = Coordinate3D(1.0, 0.0, 0.0)
        v2 = Coordinate3D(0.0, 1.0, 0.0)
        v3 = calculate_cross_product(v1, v2)
        
        # i x j = k
        assert v3.x == pytest.approx(0.0, abs=1e-10)
        assert v3.y == pytest.approx(0.0, abs=1e-10)
        assert v3.z == pytest.approx(1.0)
    
    def test_cross_product_anticommutative(self):
        """Test that cross product is anticommutative."""
        v1 = Coordinate3D(1.0, 2.0, 3.0)
        v2 = Coordinate3D(4.0, 5.0, 6.0)
        
        v3_12 = calculate_cross_product(v1, v2)
        v3_21 = calculate_cross_product(v2, v1)
        
        # v1 x v2 = -(v2 x v1)
        assert v3_12.x == pytest.approx(-v3_21.x)
        assert v3_12.y == pytest.approx(-v3_21.y)
        assert v3_12.z == pytest.approx(-v3_21.z)
    
    def test_dot_product_orthogonal(self):
        """Test dot product of orthogonal vectors."""
        v1 = Coordinate3D(1.0, 0.0, 0.0)
        v2 = Coordinate3D(0.0, 1.0, 0.0)
        
        dot = calculate_dot_product(v1, v2)
        assert dot == pytest.approx(0.0, abs=1e-10)
    
    def test_dot_product_parallel(self):
        """Test dot product of parallel vectors."""
        v1 = Coordinate3D(3.0, 4.0, 0.0)
        v2 = Coordinate3D(3.0, 4.0, 0.0)
        
        dot = calculate_dot_product(v1, v2)
        mag_sq = 3.0**2 + 4.0**2
        assert dot == pytest.approx(mag_sq)
    
    def test_vector_magnitude(self):
        """Test vector magnitude calculation."""
        v = Coordinate3D(3.0, 4.0, 0.0)
        mag = calculate_vector_magnitude(v)
        assert mag == pytest.approx(5.0)
    
    def test_vector_magnitude_3d(self):
        """Test vector magnitude in 3D."""
        v = Coordinate3D(1.0, 2.0, 2.0)
        mag = calculate_vector_magnitude(v)
        assert mag == pytest.approx(3.0)


class TestSolidAngle:
    """Test solid angle calculation."""
    
    def test_solid_angle_basic(self):
        """Test basic solid angle calculation."""
        p1 = Coordinate3D(1.0, 0.0, 0.0)
        p2 = Coordinate3D(0.0, 1.0, 0.0)
        p3 = Coordinate3D(0.0, 0.0, 1.0)
        
        # Angle at center of triangle
        phi = np.pi / 4
        theta = np.pi / 4
        
        angle = calculate_solid_angle(p1, p2, p3, phi, theta)
        
        # Should be between 0 and 1
        assert 0.0 <= angle <= 1.0
    
    def test_solid_angle_degenerate_triangle(self):
        """Test solid angle for degenerate triangle."""
        # Three collinear points
        p1 = Coordinate3D(1.0, 0.0, 0.0)
        p2 = Coordinate3D(2.0, 0.0, 0.0)
        p3 = Coordinate3D(3.0, 0.0, 0.0)
        
        phi = np.pi / 4
        theta = np.pi / 4
        
        angle = calculate_solid_angle(p1, p2, p3, phi, theta)
        
        # Should return 1.0 for degenerate triangle
        assert angle == pytest.approx(1.0)
    
    def test_solid_angle_zero_area(self):
        """Test solid angle for zero area triangle."""
        # Duplicate points
        p1 = Coordinate3D(1.0, 1.0, 1.0)
        p2 = Coordinate3D(1.0, 1.0, 1.0)
        p3 = Coordinate3D(2.0, 2.0, 2.0)
        
        phi = np.pi / 4
        theta = np.pi / 4
        
        angle = calculate_solid_angle(p1, p2, p3, phi, theta)
        
        # Should return 1.0 for zero area
        assert angle == pytest.approx(1.0)
    
    def test_solid_angle_range(self):
        """Test that solid angle is always in valid range."""
        # Random triangles
        np.random.seed(42)
        
        for _ in range(10):
            p1 = Coordinate3D(
                np.random.randn(),
                np.random.randn(),
                np.random.randn()
            )
            p2 = Coordinate3D(
                np.random.randn(),
                np.random.randn(),
                np.random.randn()
            )
            p3 = Coordinate3D(
                np.random.randn(),
                np.random.randn(),
                np.random.randn()
            )
            
            phi = np.random.uniform(0, np.pi)
            theta = np.random.uniform(0, 2*np.pi)
            
            angle = calculate_solid_angle(p1, p2, p3, phi, theta)
            
            # Should always be in [0, 1]
            assert 0.0 <= angle <= 1.0
    
    def test_solid_angle_symmetry(self):
        """Test solid angle for symmetric configuration."""
        # Equilateral triangle in xy-plane
        p1 = Coordinate3D(1.0, 0.0, 0.0)
        p2 = Coordinate3D(-0.5, np.sqrt(3)/2, 0.0)
        p3 = Coordinate3D(-0.5, -np.sqrt(3)/2, 0.0)
        
        # Angle perpendicular to plane
        phi = np.pi / 2
        theta = 0.0
        
        angle = calculate_solid_angle(p1, p2, p3, phi, theta)
        
        # Should be close to 1 (normal perpendicular to radial)
        assert 0.0 <= angle <= 1.0
