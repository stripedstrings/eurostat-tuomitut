"""Vaihe 7 M4: rikosotsikon kansalaisuusmaininta vs. K1 Suomi. Ei syytä."""

from __future__ import annotations

import csv

import pandas as pd

from src.analyze_media import RYHMAT, _avaimet, _lue, _osuma
from src.config import ASTEET_PATH
from src.fetch_media import TABLES
from src.wilson import osuus, wilson_ci

D_MIN = 10
NAT_AVAIMET = ("suomalais", "suomen kansal")
FOR_AVAIMET = ("ulkomaalais", "vierasmaalais")


def _f(v: float) -> str:
    return "" if v != v else f"{v:.6f}"


def kansalaisuus_luokka(otsikko: str) -> str:
    t = (otsikko or "").lower()
    nat = any(a in t for a in NAT_AVAIMET)
    foreign = any(a in t for a in FOR_AVAIMET)
    if nat and foreign:
        return "molemmat"
    if nat:
        return "NAT"
    if foreign:
        return "FOR"
    return ""


def on_rikosotsikko(rivi: dict[str, str]) -> bool:
    if _osuma(_avaimet(rivi.get("entiteetti", "")), "rikollisuus"):
        return True
    t = (rivi.get("otsikko") or "").lower()
    return any(a in t for a in RYHMAT["rikollisuus"])


def k1_fi_osuus(vuodet: set[int]) -> dict[str, str]:
    df = pd.read_csv(ASTEET_PATH)
    fi = df[(df["geo"] == "FI") & (df["vuosi"].isin(vuodet))].copy()
    fi = fi[fi["kelpoinen_aste"].astype(str).str.lower().isin(["true", "1"])]
    nat = pd.to_numeric(fi["tuomitut_NAT"], errors="coerce")
    foreign = pd.to_numeric(fi["tuomitut_FOR"], errors="coerce")
    ok = nat.notna() & foreign.notna()
    n_nat = float(nat[ok].sum())
    n_for = float(foreign[ok].sum())
    n = n_nat + n_for
    p = osuus(n_for, n)
    vuosi_lista = sorted(int(v) for v in fi.loc[ok, "vuosi"].tolist())
    return {
        "lahde": "K1_FI",
        "yksikko": "tuomitut",
        "vuodet": ",".join(str(v) for v in vuosi_lista),
        "n_NAT": str(int(n_nat)) if n_nat == n_nat else "",
        "n_FOR": str(int(n_for)) if n_for == n_for else "",
        "n": str(int(n)) if n == n else "",
        "osuus_FOR": _f(p),
        "wilson_ala": "",
        "wilson_yla": "",
        "d_lt_10": "0" if n >= D_MIN else "1",
        "huom": "ilmoitetut lukumäärät, ei otanta-CI; ei EU-aggregaatti",
    }


def uutis_osuus(
    rivit: list[dict[str, str]], ehdollinen: bool, media: str, vuodet: set[int]
) -> dict[str, str]:
    osat = [
        r
        for r in rivit
        if on_rikosotsikko(r)
        and (media == "molemmat" or r.get("media") == media)
        and (not vuodet or int(r["paiva"][:4]) in vuodet)
    ]
    if ehdollinen:
        osat = [r for r in osat if kansalaisuus_luokka(r.get("otsikko", ""))]
    n = len(osat)
    x_for = sum(1 for r in osat if kansalaisuus_luokka(r.get("otsikko", "")) in {"FOR", "molemmat"})
    x_nat = sum(1 for r in osat if kansalaisuus_luokka(r.get("otsikko", "")) in {"NAT", "molemmat"})
    p = osuus(x_for, n)
    lo, hi = wilson_ci(x_for, n)
    return {
        "lahde": "media",
        "yksikko": "rikosotsikko_ehdollinen" if ehdollinen else "rikosotsikko",
        "media": media,
        "vuodet": ",".join(str(v) for v in sorted(vuodet)) if vuodet else "havaittu",
        "n_NAT": str(x_nat),
        "n_FOR": str(x_for),
        "n": str(n),
        "osuus_FOR": _f(p),
        "wilson_ala": _f(lo),
        "wilson_yla": _f(hi),
        "d_lt_10": "1" if x_for < D_MIN or n < D_MIN else "0",
        "huom": "uutiskynnys; avain ≠ oikeudellinen kansalaisuus",
    }


def aja() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    otsikot = [r for r in _lue("tietueet_otsikko.csv") if (r.get("otsikko") or "").strip()]
    media_vuodet = {int(r["paiva"][:4]) for r in otsikot if on_rikosotsikko(r)}
    k1_kaikki = pd.read_csv(ASTEET_PATH)
    fi_ok = k1_kaikki[
        (k1_kaikki["geo"] == "FI")
        & (k1_kaikki["kelpoinen_aste"].astype(str).str.lower().isin(["true", "1"]))
        & pd.to_numeric(k1_kaikki["tuomitut_NAT"], errors="coerce").notna()
        & pd.to_numeric(k1_kaikki["tuomitut_FOR"], errors="coerce").notna()
    ]
    k1_vuodet = {int(v) for v in fi_ok["vuosi"].tolist()}
    yhteiset = media_vuodet & k1_vuodet

    rivit = [
        k1_fi_osuus(yhteiset),
        uutis_osuus(otsikot, False, "molemmat", yhteiset),
        uutis_osuus(otsikot, True, "molemmat", yhteiset),
        uutis_osuus(otsikot, False, "iltalehti_etusivu", yhteiset),
        uutis_osuus(otsikot, False, "yle_uutiset", yhteiset),
        uutis_osuus(otsikot, True, "iltalehti_etusivu", yhteiset),
        uutis_osuus(otsikot, True, "yle_uutiset", yhteiset),
    ]
    kentat = [
        "lahde",
        "yksikko",
        "media",
        "vuodet",
        "n_NAT",
        "n_FOR",
        "n",
        "osuus_FOR",
        "wilson_ala",
        "wilson_yla",
        "d_lt_10",
        "huom",
    ]
    with (TABLES / "m4_media_vs_k1.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kentat, extrasaction="ignore")
        w.writeheader()
        w.writerows(rivit)

    varo = [
        {
            "varoitus": "uutiskynnys",
            "teksti": "Etusivuotsikko ei ole otos kaikista rikoksista eikä tuomioista.",
        },
        {
            "varoitus": "laskentayksikko",
            "teksti": "K1 FI tuomitut (NAT/FOR). Media = otsikko. Yksiköt eivät täsmää.",
        },
        {
            "varoitus": "otoskoko",
            "teksti": "HTML-peitto on katkonainen; D<10 merkitty. Ei täyttöä.",
        },
        {
            "varoitus": "kasite",
            "teksti": "Kansalaisuusmaininta ≠ maahanmuuttotausta. Ei demonyymejä.",
        },
        {
            "varoitus": "syy",
            "teksti": "Ei syy-yhteyttä, ei motiivia, ei politiikkajohtopäätöstä.",
        },
        {
            "varoitus": "eu",
            "teksti": "EU-aggregaattia ei yhdistetty Suomen mediaan.",
        },
    ]
    with (TABLES / "m4_varoitukset.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["varoitus", "teksti"])
        w.writeheader()
        w.writerows(varo)
    print("kirjoitettu", TABLES / "m4_media_vs_k1.csv", flush=True)


if __name__ == "__main__":
    aja()
