"""Wilson-osuusväli. n<=0 → NaN, ei täyttöä."""

from __future__ import annotations

import math

from src.rates import Z_95


def wilson_ci(x: int | float, n: int | float, z: float = Z_95) -> tuple[float, float]:
    if n is None or x is None:
        return float("nan"), float("nan")
    nn = float(n)
    xx = float(x)
    if not math.isfinite(nn) or not math.isfinite(xx) or nn <= 0 or xx < 0 or xx > nn:
        return float("nan"), float("nan")
    p = xx / nn
    z2 = z * z
    den = 1.0 + z2 / nn
    keski = (p + z2 / (2.0 * nn)) / den
    puoli = z * math.sqrt(p * (1.0 - p) / nn + z2 / (4.0 * nn * nn)) / den
    return keski - puoli, keski + puoli


def osuus(x: int | float, n: int | float) -> float:
    nn = float(n) if n is not None else float("nan")
    xx = float(x) if x is not None else float("nan")
    if not math.isfinite(nn) or not math.isfinite(xx) or nn <= 0:
        return float("nan")
    return xx / nn
