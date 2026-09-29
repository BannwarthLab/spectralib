# =============================================================================
# test_plotting.py  –  smoke test (headless)
# =============================================================================
import numpy as np

from cpl50 import read_spectrum
from cpl50.broadening import emission_spectrum
from cpl50.plotting import add_wavelength_axis, plot_comparison, plot_sticks


def test_comparison_plot(tmp_path):
    ref = read_spectrum("data/spectra/12/12_CPL.csv").convert_x("ev", jacobian=True)
    grid = np.linspace(1.5, 5.0, 1000)
    calc = emission_spectrum([3.1], [-4.0], grid, 0.35)
    ax = plot_comparison(ref, calc, shift=-0.2)
    plot_sticks([2.9], [-1.0], ax)
    add_wavelength_axis(ax)
    ax.figure.savefig(tmp_path / "cmp.png")
    assert (tmp_path / "cmp.png").stat().st_size > 0
