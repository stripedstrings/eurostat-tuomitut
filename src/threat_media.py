"""TUTKIVA: terveysuhka-aihe ja uhkakehys. Ei H4, ei täyttöä."""

from __future__ import annotations

import csv

from src.fetch_media import TABLES
from src.wilson import osuus, wilson_ci

D_MIN = 10
KOODIKIRJA = "uhkakehys-v1"
TERVEYS_AVAIMET = (
    "terveysuhka",
    "epidemia",
    "pandemia",
    "koronavirus",
    "korona",
    "covid",
    "influenssa",
    "tartunta",
    "rokote",
    "tehohoito",
    "kuolemaan johtav",
)
KEHYS_AVAIMET = (
    "tappaa",
    "tuhoaa",
    "tuhoisa",
    "katastrofi",
    "hengenvaara",
    "tunkeutu",
    "kaapata",
    "romahdus",
    "kaaos",
    "paniikki",
    "pelottel",
    "voi tappaa",
    "kaikki kuol",
)
RISTI = ("molemmat", "vain_terveys", "vain_kehys", "ei_kumpaakaan")


def _osuma(teksti: str, avaimet: tuple[str, ...]) -> bool:
    t = (teksti or "").lower()
    return any(a in t for a in avaimet)


def luokittele(otsikko: str) -> tuple[bool, bool, str]:
    ots = (otsikko or "").strip()
    if not ots:
        return False, False, ""
    terveys = _osuma(ots, TERVEYS_AVAIMET)
    kehys = _osuma(ots, KEHYS_AVAIMET)
    if terveys and kehys:
        risti = "molemmat"
    elif terveys:
        risti = "vain_terveys"
    elif kehys:
        risti = "vain_kehys"
    else:
        risti = "ei_kumpaakaan"
    return terveys, kehys, risti


def _f(v: float) -> str:
    return "" if v != v else f"{v:.6f}"


def _osuusrivi(x: int, n: int, **lisat: str) -> dict[str, str]:
    p = osuus(x, n)
    lo, hi = wilson_ci(x, n)
    merkitse = x < D_MIN or n < D_MIN
    out = {
        "n": str(n),
        "x": str(x),
        "osuus": _f(p),
        "wilson_ala": _f(lo),
        "wilson_yla": _f(hi),
        "d_lt_10": "1" if merkitse else "0",
        "huom": "TUTKIVA (ei esirekisteröity)",
        "koodakirja_versio": KOODIKIRJA,
    }
    out.update(lisat)
    return out


def aja() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    with (TABLES / "tietueet_otsikko.csv").open(encoding="utf-8", newline="") as f:
        rivit = [r for r in csv.DictReader(f) if (r.get("otsikko") or "").strip()]
    liput: list[dict[str, str]] = []
    for r in rivit:
        terveys, kehys, risti = luokittele(r["otsikko"])
        liput.append(
            {
                "media": r["media"],
                "paiva": r["paiva"],
                "jarjestys": r.get("jarjestys", ""),
                "otsikko": r["otsikko"],
                "terveysuhka": "1" if terveys else "0",
                "uhkakehys": "1" if kehys else "0",
                "risti": risti,
                "koodaaja": "saanto-uhkakehys-v1",
                "koodakirja_versio": KOODIKIRJA,
            }
        )
    with (TABLES / "uhkakehys_otsikko.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(liput[0].keys()))
        w.writeheader()
        w.writerows(liput)

    osuus_rivit: list[dict[str, str]] = []
    mediat = sorted({r["media"] for r in liput})
    for media in mediat:
        osat = [r for r in liput if r["media"] == media]
        jaksot: list[tuple[str, list[dict[str, str]]]] = [("havaittu", osat)]
        vuodet = sorted({r["paiva"][:4] for r in osat})
        for vuosi in vuodet:
            jaksot.append((vuosi, [r for r in osat if r["paiva"].startswith(vuosi)]))
        for jakso, joukko in jaksot:
            n = len(joukko)
            for luokka in RISTI:
                x = sum(1 for r in joukko if r["risti"] == luokka)
                osuus_rivit.append(
                    _osuusrivi(x, n, media=media, jakso=jakso, luokka=luokka)
                )
            osuus_rivit.append(
                _osuusrivi(
                    sum(1 for r in joukko if r["terveysuhka"] == "1"),
                    n,
                    media=media,
                    jakso=jakso,
                    luokka="terveysuhka",
                )
            )
            osuus_rivit.append(
                _osuusrivi(
                    sum(1 for r in joukko if r["uhkakehys"] == "1"),
                    n,
                    media=media,
                    jakso=jakso,
                    luokka="uhkakehys",
                )
            )
    with (TABLES / "uhkakehys_osuus.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(osuus_rivit[0].keys()))
        w.writeheader()
        w.writerows(osuus_rivit)
    print("kirjoitettu", TABLES / "uhkakehys_osuus.csv", flush=True)


if __name__ == "__main__":
    aja()
