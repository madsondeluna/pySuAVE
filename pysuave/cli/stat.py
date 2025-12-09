"""
Statistical analysis command (s_stat equivalent).

This module implements the stat command for pySuAVE CLI.
"""

import click
import numpy as np
from pathlib import Path

from pysuave.analysis.statistics import (
    comprehensive_statistics,
    create_histogram,
    gaussian_model,
    calculate_autocorrelation,
)


@click.command(name='stat')
@click.option(
    '-in', '--input',
    'input_file',
    required=True,
    type=click.Path(exists=True),
    help='Input file with two columns: frame and value'
)
@click.option(
    '-o', '--output',
    'output_prefix',
    default='output',
    help='Output file prefix (default: output)'
)
@click.option(
    '--no-acf',
    is_flag=True,
    help='Skip autocorrelation function calculation'
)
def stat_command(input_file, output_prefix, no_acf):
    """
    Calculate statistical properties of time series data.
    
    This command reads a two-column file (frame, value) and calculates:
    - Mean, standard deviation
    - Skewness, kurtosis
    - Median, mode
    - Quartiles (Q1, Q3) and deciles (D1, D9)
    - Probability density function (PDF)
    - Gaussian model fit
    - Autocorrelation function (optional)
    
    Example:
        pysuave stat -in data.xvg -o results
    """
    click.echo(f"pySuAVE Statistical Analysis")
    click.echo(f"Input file: {input_file}")
    click.echo()
    
    # Read data
    click.echo("Reading data...")
    try:
        data = np.loadtxt(input_file, usecols=1)
    except Exception as e:
        click.echo(f"Error reading file: {e}", err=True)
        return 1
    
    if len(data) == 0:
        click.echo("Error: No data found in input file", err=True)
        return 1
    
    click.echo(f"Loaded {len(data)} data points")
    click.echo()
    
    # Calculate statistics
    click.echo("Calculating statistics...")
    stats = comprehensive_statistics(data)
    
    # Print summary
    click.echo()
    click.echo("=" * 50)
    click.echo("STATISTICAL SUMMARY")
    click.echo("=" * 50)
    click.echo(f"Number of points: {stats.n_points}")
    click.echo(f"Min value:        {stats.min_value:.6f}")
    click.echo(f"Max value:        {stats.max_value:.6f}")
    click.echo()
    click.echo(f"Mean:             {stats.mean:.6f}")
    click.echo(f"Std. deviation:   {stats.std_dev:.6f}")
    click.echo(f"Skewness:         {stats.skewness:.6f}")
    click.echo(f"Kurtosis:         {stats.kurtosis:.6f}")
    click.echo()
    click.echo(f"Median:           {stats.median:.6f}")
    click.echo(f"Mode:             {stats.mode:.6f}")
    click.echo()
    click.echo(f"1st Quartile (Q1): {stats.q1:.6f}")
    click.echo(f"3rd Quartile (Q3): {stats.q3:.6f}")
    click.echo(f"1st Decile (D1):   {stats.d1:.6f}")
    click.echo(f"9th Decile (D9):   {stats.d9:.6f}")
    click.echo("=" * 50)
    click.echo()
    
    # Create histogram and Gaussian model
    click.echo("Creating probability density function...")
    bin_centers, histogram, min_val, bin_width = create_histogram(data)
    gaussian = gaussian_model(bin_centers, stats.mean, stats.std_dev)
    
    # Write PDF output
    pdf_file = f"{output_prefix}_pdf.xvg"
    click.echo(f"Writing PDF to {pdf_file}...")
    
    with open(pdf_file, 'w') as f:
        # Write header
        f.write("# pySuAVE Statistical Analysis\n")
        f.write(f"# Input: {input_file}\n")
        f.write("# Probability Density Function\n")
        f.write("@    title \"Probability Density Function\"\n")
        f.write("@    xaxis  label \"x\"\n")
        f.write("@    yaxis  label \"PDF(x)\"\n")
        f.write("@    s0 legend  \"Original Data\"\n")
        f.write("@    s1 legend  \"Gaussian Model\"\n")
        f.write("@    s1 line linewidth 2.0\n")
        f.write("@    s2 legend  \"Q1\"\n")
        f.write("@    s3 legend  \"Q3\"\n")
        f.write("@    s4 legend  \"D1\"\n")
        f.write("@    s5 legend  \"D9\"\n")
        
        # Write histogram
        for x, y in zip(bin_centers, histogram):
            f.write(f"{x:.6f} {y:.6f}\n")
        
        f.write("&\n")
        
        # Write Gaussian model
        for x, y in zip(bin_centers, gaussian):
            f.write(f"{x:.6f} {y:.6f}\n")
        
        f.write("&\n")
        
        # Write quartile markers
        f.write(f"{stats.q1:.6f} 0.0\n")
        f.write("&\n")
        f.write(f"{stats.q3:.6f} 0.0\n")
        f.write("&\n")
        f.write(f"{stats.d1:.6f} 0.0\n")
        f.write("&\n")
        f.write(f"{stats.d9:.6f} 0.0\n")
    
    # Calculate and write autocorrelation
    if not no_acf:
        click.echo("Calculating autocorrelation function...")
        acf = calculate_autocorrelation(data)
        
        acf_file = f"{output_prefix}_acf.xvg"
        click.echo(f"Writing ACF to {acf_file}...")
        
        with open(acf_file, 'w') as f:
            f.write("# pySuAVE Statistical Analysis\n")
            f.write(f"# Input: {input_file}\n")
            f.write("# Autocorrelation Function\n")
            f.write("@    title \"Autocorrelation Function\"\n")
            f.write("@    xaxis  label \"Lag\"\n")
            f.write("@    yaxis  label \"ACF\"\n")
            
            for lag, value in enumerate(acf):
                f.write(f"{lag} {value:.6f}\n")
    
    click.echo()
    click.echo("Analysis complete!")
    return 0
