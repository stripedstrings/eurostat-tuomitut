"""Krippendorffin nominaali-α. Puuttuva arvo jätetään pois."""

from __future__ import annotations

import math
from collections import defaultdict


def _puuttuu(x: object) -> bool:
    if x is None:
        return True
    if isinstance(x, float) and math.isnan(x):
        return True
    return str(x).strip() == ""


def krippendorff_alpha_nominal(yksikot: list[list[object]]) -> float:
    """`yksikot`: lista havaintoja; kussakin koodaajien arvot.

    α = 1 − D_o / D_e. Alle kaksi kelvollista paria → NaN.
    """
    o: dict[tuple[object, object], float] = defaultdict(float)
    n_tahti = 0.0
    for u in yksikot:
        r = [x for x in u if not _puuttuu(x)]
        m = len(r)
        if m < 2:
            continue
        n_tahti += m
        for i, ci in enumerate(r):
            for j, cj in enumerate(r):
                if i == j:
                    continue
                o[(ci, cj)] += 1.0 / (m - 1)
    if n_tahti < 2:
        return float("nan")
    n_c: dict[object, float] = defaultdict(float)
    for (c, _k), val in o.items():
        n_c[c] += val
    d_o = sum(val for (c, k), val in o.items() if c != k) / n_tahti
    avaimet = list(n_c)
    d_e = 0.0
    for c in avaimet:
        for k in avaimet:
            if c != k:
                d_e += n_c[c] * n_c[k]
    d_e /= n_tahti * (n_tahti - 1)
    if d_e == 0:
        return 1.0 if d_o == 0 else float("nan")
    return 1.0 - d_o / d_e


def pari_alpha(a: list[object], b: list[object]) -> float:
    if len(a) != len(b):
        raise ValueError("parien pituudet eroavat")
    return krippendorff_alpha_nominal([[x, y] for x, y in zip(a, b)])
