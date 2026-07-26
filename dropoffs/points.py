"""
dropoffs/points.py — the ONE place the eco-points formula lives.

Report §4.4 (RAPID "Responsible"): the eco-points calculation is implemented
once and reused everywhere points are calculated — the live preview and the
final award alike — so the same rule can never diverge across the codebase.

Formula (report §3.2.3.2): a fixed 10 points per kilogram of plastic.
"""

from decimal import Decimal

# Fixed award rate. Change it here and every calculation follows.
POINTS_PER_KG = 10


def calculate_points(weight_kg):
    """
    Return the whole eco-points earned for a given weight in kilograms.

    Accepts a Decimal, str, int, or float and computes exactly (via Decimal),
    then truncates to a whole number of points.
    """
    weight = Decimal(str(weight_kg))
    return int(weight * POINTS_PER_KG)
