"""Kansalliset tapaustutkimukset. Ei yhdistetä src.rates / EU-aggregaattiin."""

from src.national import dk, fi, se


def aja() -> None:
    dk.aja()
    fi.aja()
    se.aja()


if __name__ == "__main__":
    aja()
