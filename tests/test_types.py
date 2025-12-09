"""Tests for core data types."""

import numpy as np
import pytest

from pysuave.core.types import AtomData, Coordinate3D, SphericalCoordinate


class TestAtomData:
    """Test AtomData dataclass."""
    
    def test_creation(self):
        """Test basic AtomData creation."""
        atom = AtomData(
            x=1.0, y=2.0, z=3.0,
            n_atom=1, n_resid=1,
            atom="CA", resid="ALA"
        )
        assert atom.x == 1.0
        assert atom.y == 2.0
        assert atom.z == 3.0
        assert atom.atom == "CA"
    
    def test_to_array(self):
        """Test conversion to numpy array."""
        atom = AtomData(x=1.0, y=2.0, z=3.0, n_atom=1, n_resid=1)
        arr = atom.to_array()
        np.testing.assert_array_equal(arr, [1.0, 2.0, 3.0])
    
    def test_from_array(self):
        """Test creation from numpy array."""
        coords = np.array([1.0, 2.0, 3.0])
        atom = AtomData.from_array(coords, n_atom=1, n_resid=1, atom="CA")
        assert atom.x == 1.0
        assert atom.y == 2.0
        assert atom.z == 3.0
        assert atom.atom == "CA"


class TestCoordinate3D:
    """Test Coordinate3D dataclass."""
    
    def test_creation(self):
        """Test basic Coordinate3D creation."""
        coord = Coordinate3D(x=1.0, y=2.0, z=3.0)
        assert coord.x == 1.0
        assert coord.y == 2.0
        assert coord.z == 3.0
    
    def test_distance(self):
        """Test distance calculation."""
        c1 = Coordinate3D(x=0.0, y=0.0, z=0.0)
        c2 = Coordinate3D(x=3.0, y=4.0, z=0.0)
        dist = c1.distance_to(c2)
        assert dist == pytest.approx(5.0)
    
    def test_addition(self):
        """Test vector addition."""
        c1 = Coordinate3D(x=1.0, y=2.0, z=3.0)
        c2 = Coordinate3D(x=4.0, y=5.0, z=6.0)
        c3 = c1 + c2
        assert c3.x == 5.0
        assert c3.y == 7.0
        assert c3.z == 9.0
    
    def test_subtraction(self):
        """Test vector subtraction."""
        c1 = Coordinate3D(x=5.0, y=7.0, z=9.0)
        c2 = Coordinate3D(x=1.0, y=2.0, z=3.0)
        c3 = c1 - c2
        assert c3.x == 4.0
        assert c3.y == 5.0
        assert c3.z == 6.0
    
    def test_scalar_multiplication(self):
        """Test scalar multiplication."""
        c1 = Coordinate3D(x=1.0, y=2.0, z=3.0)
        c2 = c1 * 2.0
        assert c2.x == 2.0
        assert c2.y == 4.0
        assert c2.z == 6.0


class TestSphericalCoordinate:
    """Test SphericalCoordinate dataclass."""
    
    def test_creation(self):
        """Test basic SphericalCoordinate creation."""
        coord = SphericalCoordinate(rho=1.0, phi=0.0, theta=0.0)
        assert coord.rho == 1.0
        assert coord.phi == 0.0
        assert coord.theta == 0.0
    
    def test_to_cartesian_simple(self):
        """Test conversion to Cartesian (simple case)."""
        # Point on z-axis
        sph = SphericalCoordinate(rho=5.0, phi=0.0, theta=0.0)
        cart = sph.to_cartesian()
        assert cart.x == pytest.approx(0.0, abs=1e-10)
        assert cart.y == pytest.approx(0.0, abs=1e-10)
        assert cart.z == pytest.approx(5.0)
    
    def test_from_cartesian_simple(self):
        """Test conversion from Cartesian (simple case)."""
        # Point on z-axis
        cart = Coordinate3D(x=0.0, y=0.0, z=5.0)
        sph = SphericalCoordinate.from_cartesian(cart)
        assert sph.rho == pytest.approx(5.0)
        assert sph.theta == pytest.approx(0.0, abs=1e-10)
    
    def test_roundtrip_conversion(self):
        """Test Cartesian -> Spherical -> Cartesian roundtrip."""
        original = Coordinate3D(x=3.0, y=4.0, z=5.0)
        sph = SphericalCoordinate.from_cartesian(original)
        back = sph.to_cartesian()
        
        assert back.x == pytest.approx(original.x)
        assert back.y == pytest.approx(original.y)
        assert back.z == pytest.approx(original.z)
    
    def test_origin_handling(self):
        """Test handling of origin (0, 0, 0)."""
        cart = Coordinate3D(x=0.0, y=0.0, z=0.0)
        sph = SphericalCoordinate.from_cartesian(cart)
        assert sph.rho == 0.0
        assert sph.phi == 0.0
        assert sph.theta == 0.0
