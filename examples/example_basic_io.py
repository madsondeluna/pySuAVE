"""
Example: Reading PDB and NDX files with pySuAVE

This demonstrates basic I/O operations equivalent to the Fortran code.
"""

from pathlib import Path
from pysuave.io import read_pdb, read_ndx, write_pdb
from pysuave.core.types import AtomData

def main():
    """Example usage of pySuAVE I/O functions."""
    
    # Example paths (adjust to your data)
    examples_dir = Path(__file__).parent.parent / "examples"
    pdb_file = examples_dir / "membrane.pdb"
    ndx_file = examples_dir / "mem1.ndx"
    
    print("=" * 60)
    print("pySuAVE - Example: Basic I/O Operations")
    print("=" * 60)
    
    # 1. Read index file
    print("\n1. Reading index file...")
    if ndx_file.exists():
        indices = read_ndx(ndx_file)
        print(f"   Loaded {len(indices)} atom indices")
        print(f"   First 10 indices: {indices[:10]}")
    else:
        print(f"   Warning: {ndx_file} not found")
        indices = None
    
    # 2. Read PDB file (all atoms)
    print("\n2. Reading PDB file (all atoms)...")
    if pdb_file.exists():
        all_atoms = read_pdb(pdb_file)
        print(f"   Loaded {len(all_atoms)} atoms")
        
        # Show first atom
        if all_atoms:
            atom = all_atoms[0]
            print(f"   First atom: {atom.atom} {atom.resid} {atom.n_resid}")
            print(f"   Coordinates: ({atom.x:.3f}, {atom.y:.3f}, {atom.z:.3f})")
    else:
        print(f"   Warning: {pdb_file} not found")
        all_atoms = []
    
    # 3. Read PDB file (selected atoms only)
    if pdb_file.exists() and indices is not None:
        print("\n3. Reading PDB file (selected atoms only)...")
        selected_atoms = read_pdb(pdb_file, atom_indices=indices)
        print(f"   Loaded {len(selected_atoms)} selected atoms")
    
    # 4. Calculate center of mass (simple example)
    if all_atoms:
        print("\n4. Calculating geometric center...")
        import numpy as np
        
        coords = np.array([atom.to_array() for atom in all_atoms])
        center = coords.mean(axis=0)
        print(f"   Geometric center: ({center[0]:.3f}, {center[1]:.3f}, {center[2]:.3f})")
    
    # 5. Write output PDB (example)
    print("\n5. Writing output PDB...")
    if all_atoms:
        output_file = Path("/tmp/pysuave_test_output.pdb")
        write_pdb(
            output_file,
            all_atoms[:100],  # Write first 100 atoms
            title="Test output from pySuAVE",
            box=(100.0, 100.0, 100.0)
        )
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
