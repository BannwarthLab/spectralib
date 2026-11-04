"""Render a coverage badge SVG from a Cobertura report.

``gitlab.git.nrw`` requires a login for ``/-/badges/*.svg``. This writes an
equivalent badge into the documentation that should be readable without login credentials.

Usage: ``python3 coverage_badge.py coverage.xml public/coverage.svg``
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

USAGE = "usage: coverage_badge.py <cobertura-report> <output.svg>\n"
EXPECTED_ARGS = 2

LABEL = "coverage"
PADDING = 9.0

# (minimum percentage, fill) -- first match wins, so keep this ordered high to low.
COLOURS = (
    (95.0, "#4c1"),
    (90.0, "#97ca00"),
    (75.0, "#dfb317"),
    (60.0, "#fe7d37"),
    (0.0, "#e05d44"),
)

# Approximate advance widths at 11px Verdana. Only used to size the two boxes;
# the text itself is centred and never stretched, so an estimate a little on the
# generous side costs a pixel of padding rather than distorted glyphs.
ADVANCE = {"%": 8.4, "digit": 7.0, "other": 6.6}

# Read straight off the Cobertura root element rather than through an XML parser:
# the input is this pipeline's own artifact, and a one-attribute lookup is not
# worth a defusedxml dependency in the CI image.
LINE_RATE = re.compile(r"<coverage[^>]*\sline-rate=\"([0-9.]+)\"")


def text_width(text: str) -> float:
    """Approximate rendered width of ``text`` in pixels."""
    return sum(ADVANCE["%"] if c == "%" else ADVANCE["digit"] if c.isdigit() else ADVANCE["other"] for c in text)


def line_rate(report: Path) -> float:
    """Overall line coverage of a Cobertura report, in percent."""
    match = LINE_RATE.search(report.read_text())
    if match is None:
        msg = f"{report} has no line-rate on its <coverage> element, so it is not a Cobertura report."
        raise ValueError(msg)
    return float(match.group(1)) * 100.0


def colour(percent: float) -> str:
    """Fill colour for a coverage percentage."""
    return next(fill for minimum, fill in COLOURS if percent >= minimum)


def badge(percent: float) -> str:
    """Build a flat SVG badge reading ``coverage <percent>%``."""
    value = f"{percent:.0f}%"
    label_width = round(text_width(LABEL) + 2 * PADDING)
    value_width = round(text_width(value) + 2 * PADDING)
    total = label_width + value_width
    # Text sits at the centre of its half, in tenths of a pixel so the shifted
    # shadow copy below it can be offset by exactly one pixel.
    label_mid = label_width * 5
    value_mid = (label_width + value_width / 2) * 10
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total}" height="20" \
role="img" aria-label="{LABEL}: {value}">
  <title>{LABEL}: {value}</title>
  <linearGradient id="s" x2="0" y2="100%">
    <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
    <stop offset="1" stop-opacity=".1"/>
  </linearGradient>
  <clipPath id="r"><rect width="{total}" height="20" rx="3" fill="#fff"/></clipPath>
  <g clip-path="url(#r)">
    <rect width="{label_width}" height="20" fill="#555"/>
    <rect x="{label_width}" width="{value_width}" height="20" fill="{colour(percent)}"/>
    <rect width="{total}" height="20" fill="url(#s)"/>
  </g>
  <g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="110">
    <text x="{label_mid}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{LABEL}</text>
    <text x="{label_mid}" y="140" transform="scale(.1)">{LABEL}</text>
    <text x="{value_mid:.0f}" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)">{value}</text>
    <text x="{value_mid:.0f}" y="140" transform="scale(.1)">{value}</text>
  </g>
</svg>
"""


def main(argv: list[str]) -> int:
    """Write the badge for ``argv[0]`` to ``argv[1]``."""
    if len(argv) != EXPECTED_ARGS:
        sys.stderr.write(USAGE)
        return 2
    report, target = Path(argv[0]), Path(argv[1])
    percent = line_rate(report)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(badge(percent))
    sys.stdout.write(f"{target}: {percent:.2f}% coverage\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
