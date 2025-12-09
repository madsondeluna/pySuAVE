"""Tests for geometry functions - area calculations."""

import numpy as np
import pytest

from pysuave.core.types import Coordinate3D
from pysuave.geometry.area import (
    calculate_triangle_area_heron,
    calculate_surface_area_cartesian,
)


class TestTriangleAreaHeron:
    """Test Heron's formula for triangle area."""
    
    def test_right_triangle(self):
        """Test area of a right triangle."""
        # Right triangle with legs 3 and 4
        p1 = Coordinate3D(0.0, 0.0, 0.0)
        p2 = Coordinate3D(3.0, 0.0, 0.0)
        p3 = Coordinate3D(0.0, 4.0, 0.0)
        
        area = calculate_triangle_area_heron(p1, p2, p3)
        
        # Area should be 0.5 * base * height = 0.5 * 3 * 4 = 6
        assert area == pytest.approx(6.0, rel=1e-6)
    
    def test_equilateral_triangle(self):
        """Test area of an equilateral triangle."""
        # Equilateral triangle with side length 2
        p1 = Coordinate3D(0.0, 0.0, 0.0)
        p2 = Coordinate3D(2.0, 0.0, 0.0)
        p3 = Coordinate3D(1.0, np.sqrt(3.0), 0.0)
        
        area = calculate_triangle_area_heron(p1, p2, p3)
        
        # Area of equilateral triangle = (sqrt(3) / 4) * side^2
        expected = (np.sqrt(3.0) / 4.0) * 4.0  # side = 2
        assert area == pytest.approx(expected, rel=1e-6)
    
    def test_3d_triangle(self):
        """Test triangle in 3D space."""
        p1 = Coordinate3D(0.0, 0.0, 0.0)
        p2 = Coordinate3D(1.0, 0.0, 0.0)
        p3 = Coordinate3D(0.0, 1.0, 1.0)
        
        area = calculate_triangle_area_heron(p1, p2, p3)
        
        # Area should be positive
        assert area > 0
        
        # Can verify using cross product method
        # v1 = p2 - p1 = (1, 0, 0)
        # v2 = p3 - p1 = (0, 1, 1)
        # cross = (0, -1, 1), magnitude = sqrt(2)
        # area = 0.5 * sqrt(2)
        expected = 0.5 * np.sqrt(2.0)
        assert area == pytest.approx(expected, rel=1e-6)
    
    def test_degenerate_triangle(self):
        """Test degenerate triangle (collinear points)."""
        # Three points on a line
        p1 = Coordinate3D(0.0, 0.0, 0.0)
        p2 = Coordinate3D(1.0, 0.0, 0.0)
        p3 = Coordinate3D(2.0, 0.0, 0.0)
        
        area = calculate_triangle_area_heron(p1, p2, p3)
        
        # Area should be approximately 0
        assert area == pytest.approx(0.0, abs=1e-10)
    
    def test_zero_area_triangle(self):
        """Test triangle with zero area (duplicate points)."""
        p1 = Coordinate3D(1.0, 2.0, 3.0)
        p2 = Coordinate3D(1.0, 2.0, 3.0)
        p3 = Coordinate3D(4.0, 5.0, 6.0)
        
        area = calculate_triangle_area_heron(p1, p2, p3)
        
        # Area should be 0
        assert area == pytest.approx(0.0, abs=1e-10)


class TestSurfaceAreaCartesian:
    """Test Cartesian surface area calculation."""
    
    def test_flat_surface(self):
        """Test area of a flat horizontal surface."""
        # Create a 10x10 flat grid at z=0
        n = 10
        x = np.linspace(0, 10, n)
        y = np.linspace(0, 10, n)
        xx, yy = np.meshgrid(x, y, indexing='ij')
        zz = np.zeros_like(xx)
        
        grid = np.stack([xx, yy, zz], axis=-1)
        
        area = calculate_surface_area_cartesian(grid)
        
        # Area should be approximately 10 * 10 = 100
        # (slight deviation due to triangulation)
        assert area == pytest.approx(100.0, rel=0.01)
    
    def test_tilted_plane(self):
        """Test area of a tilted plane."""
        # Create a 10x10 grid tilted at 45 degrees
        n = 10
        x = np.linspace(0, 10, n)
        y = np.linspace(0, 10, n)
        xx, yy = np.meshgrid(x, y, indexing='ij')
        zz = xx  # z = x, creates 45-degree tilt
        
        grid = np.stack([xx, yy, zz], axis=-1)
        
        area = calculate_surface_area_cartesian(grid)
        
        # For a plane tilted at 45 degrees, area is sqrt(2) * base_area
        # Base area = 10 * 10 = 100
        expected = np.sqrt(2.0) * 100.0
        assert area == pytest.approx(expected, rel=0.01)
    
    def test_curved_surface(self):
        """Test area of a curved surface (paraboloid)."""
        # Create a paraboloid: z = x^2 + y^2
        n = 20
        x = np.linspace(-1, 1, n)
        y = np.linspace(-1, 1, n)
        xx, yy = np.meshgrid(x, y, indexing='ij')
        zz = xx**2 + yy**2
        
        grid = np.stack([xx, yy, zz], axis=-1)
        
        area = calculate_surface_area_cartesian(grid)
        
        # Area should be larger than the base (2x2 = 4)
        assert area > 4.0
        
        # For a paraboloid z = x^2 + y^2 over [-1,1]x[-1,1],
        # the area is approximately 7.2
        assert 6.0 < area < 9.0
    
    def test_minimum_grid_size(self):
        """Test with minimum valid grid size."""
        # 2x2 grid
        grid = np.array([
            [[0, 0, 0], [0, 1, 0]],
            [[1, 0, 0], [1, 1, 0]]
        ], dtype=np.float64)
        
        area = calculate_surface_area_cartesian(grid)
        
        # Should calculate area of 2 triangles forming a 1x1 square
        assert area == pytest.approx(1.0, rel=1e-6)
    
    def test_invalid_grid_shape(self):
        """Test validation of invalid grid shapes."""
        # Wrong number of dimensions
        with pytest.raises(ValueError):
            grid = np.zeros((10, 10))  # Missing 3rd dimension
            calculate_surface_area_cartesian(grid)
        
        # Wrong coordinate dimension
        with pytest.raises(ValueError):
            grid = np.zeros((10, 10, 2))  # Should be 3
            calculate_surface_area_cartesian(grid)
        
        # Too small grid
        with pytest.raises(ValueError):
            grid = np.zeros((1, 1, 3))  # Need at least 2x2
            calculate_surface_area_cartesian(grid)
    
    def test_unit_square(self):
        """Test area of a unit square."""
        # Create a simple 2x2 grid forming a unit square
        grid = np.array([
            [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]],
            [[1.0, 0.0, 0.0], [1.0, 1.0, 0.0]]
        ], dtype=np.float64)
        
        area = calculate_surface_area_cartesian(grid)
        
        # Area should be exactly 1.0
        assert area == pytest.approx(1.0, rel=1e-10)
    
    def test_area_scaling(self):
        """Test that area scales correctly with grid size."""
        # Create two grids: one 1x1, one 2x2
        n = 5
        
        # Grid 1: 1x1 square
        x1 = np.linspace(0, 1, n)
        y1 = np.linspace(0, 1, n)
        xx1, yy1 = np.meshgrid(x1, y1, indexing='ij')
        zz1 = np.zeros_like(xx1)
        grid1 = np.stack([xx1, yy1, zz1], axis=-1)
        area1 = calculate_surface_area_cartesian(grid1)
        
        # Grid 2: 2x2 square
        x2 = np.linspace(0, 2, n)
        y2 = np.linspace(0, 2, n)
        xx2, yy2 = np.meshgrid(x2, y2, indexing='ij')
        zz2 = np.zeros_like(xx2)
        grid2 = np.stack([xx2, yy2, zz2], axis=-1)
        area2 = calculate_surface_area_cartesian(grid2)
        
        # Area should scale as the square of linear dimensions
        # 2x2 square should have 4x the area of 1x1 square
        assert area2 == pytest.approx(4.0 * area1, rel=0.01)
