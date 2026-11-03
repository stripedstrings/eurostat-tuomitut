"""Vaihe 4: otos, sääntökoodaus, Krippendorff α. Ei ihmiskoodien keksintää."""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path

from src.fetch_media import TABLES
from src.krippendorff import pari_alpha

SIEMEN = 20261103
N_OTOS = 500
KOODIKIRJA = "koodaus-v1"
OTSIKOT = TABLES / "tietueet_otsikko.csv"

AIHE_JARJESTYS = (
    "putin",
    "zelenskyi",
    "presidentti",
    "maahanmuutto",
    "rikollisuus",
    "terveys",
)

AIHE_V1: dict[str, tuple[str, ...]] = {
    "putin": ("putin",),
    "zelenskyi": ("zelenskyi", "zelenskyy", "zelenskiy", "zelensky", "zelenski"),
    "presidentti": ("tasavallan presidentti", "suomen presidentti"),
    "maahanmuutto": ("maahanmuutto", "pakolais", "siirtolais"),
    "rikollisuus": ("rikollis", "rikos", "tuomittu", "tuomitut"),
    "terveys": ("terveysuhka", "epidemia", "pandemia"),
}

AIHE_V1B_LISAT: dict[str, tuple[str, ...]] = {
    "presidentti": ("presidentti niinistö", "presidentti stubb", "tasavallan pres."),
    "maahanmuutto": ("turvapaikka", "maahanmuuttaja", "pakolainen"),
    "rikollisuus": ("syytteeseen", "henkirikos", "rikosepäily"),
    "terveys": ("koronavirus", "covid"),
}

SAVY_JARJESTYS = ("uhka", "pelko", "viha")

SAVY_V1: dict[str, tuple[str, ...]] = {
    "uhka": ("uhka", "uhkail"),
    "pelko": ("pelko", "pelott"),
    "viha": ("viha", "vihain"),
}

SAVY_V1B_LISAT: dict[str, tuple[str, ...]] = {
    "uhka": ("hyökkäys", "terrori", "pommi-isku"),
    "pelko": ("kauhu", "paniikki"),
    "viha": ("raivo", "vihamiel"),
}


def _avaimet(pohja: dict[str, tuple[str, ...]], lisat: dict[str, tuple[str, ...]] | None) -> dict[str, tuple[str, ...]]:
    if not lisat:
        return pohja
    out: dict[str, tuple[str, ...]] = {}
    for luokka, av in pohja.items():
        out[luokka] = av + lisat.get(luokka, ())
    return out


def koodaa_aihe(otsikko: str, versio: str) -> str:
    lisat = AIHE_V1B_LISAT if versio == "v1b" else None
    avaimet = _avaimet(AIHE_V1, lisat)
    t = otsikko.lower()
    for luokka in AIHE_JARJESTYS:
        if any(a in t for a in avaimet[luokka]):
            return luokka
    return "muu"


def koodaa_savy(otsikko: str, versio: str) -> str:
    lisat = SAVY_V1B_LISAT if versio == "v1b" else None
    avaimet = _avaimet(SAVY_V1, lisat)
    t = otsikko.lower()
    for luokka in SAVY_JARJESTYS:
        if any(a in t for a in avaimet[luokka]):
            return luokka
    return ""


def arvo_otos(rivit: list[dict[str, str]], n: int = N_OTOS, siemen: int = SIEMEN) -> list[dict[str, str]]:
    kelvolliset = [r for r in rivit if (r.get("otsikko") or "").strip()]
    ryhmät: dict[str, list[dict[str, str]]] = defaultdict(list)
    for r in kelvolliset:
        ryhmät[r["media"]].append(r)
    mediat = sorted(ryhmät)
    if not mediat:
        return []
    n_kukin = n // len(mediat)
    rng = random.Random(siemen)
    otos: list[dict[str, str]] = []
    jaljella: list[dict[str, str]] = []
    for m in mediat:
        pool = list(ryhmät[m])
        rng.shuffle(pool)
        otos.extend(pool[:n_kukin])
        jaljella.extend(pool[n_kukin:])
    puute = n - len(otos)
    if puute > 0:
        rng.shuffle(jaljella)
        otos.extend(jaljella[:puute])
    return otos[:n]


def _f1(viite: list[str], ennuste: list[str], luokka: str) -> dict[str, str]:
    tp = fp = fn = 0
    for v, e in zip(viite, ennuste):
        if v == luokka and e == luokka:
            tp += 1
        elif e == luokka and v != luokka:
            fp += 1
        elif v == luokka and e != luokka:
            fn += 1
    tark = tp / (tp + fp) if (tp + fp) else float("nan")
    saanti = tp / (tp + fn) if (tp + fn) else float("nan")
    if tark != tark or saanti != saanti or (tark + saanti) == 0:
        f1 = float("nan")
    else:
        f1 = 2 * tark * saanti / (tark + saanti)
    return {
        "luokka": luokka,
        "n_viite": str(tp + fn),
        "n_ennuste": str(tp + fp),
        "tp": str(tp),
        "tarkkuus": "" if tark != tark else f"{tark:.6f}",
        "saanti": "" if saanti != saanti else f"{saanti:.6f}",
        "f1": "" if f1 != f1 else f"{f1:.6f}",
        "viite": "saanto-v1",
        "ennuste": "saanto-v1b",
        "huom": "TUTKIVA (ei esirekisteröity); ei ihmisvalidointia",
    }


def aja() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    with OTSIKOT.open(encoding="utf-8", newline="") as f:
        rivit = list(csv.DictReader(f))
    otos = arvo_otos(rivit)
    kentat = [
        "media",
        "paiva",
        "jarjestys",
        "otsikko",
        "snapshot_url",
        "aihe_saanto_v1",
        "savy_saanto_v1",
        "aihe_saanto_v1b",
        "savy_saanto_v1b",
        "aihe_ihminen_a",
        "savy_ihminen_a",
        "koodaaja_ihminen_a",
        "aihe_ihminen_b",
        "savy_ihminen_b",
        "koodaaja_ihminen_b",
        "koodakirja_versio",
    ]
    koodatut: list[dict[str, str]] = []
    for r in otos:
        ots = r["otsikko"]
        koodatut.append(
            {
                "media": r["media"],
                "paiva": r["paiva"],
                "jarjestys": r.get("jarjestys", ""),
                "otsikko": ots,
                "snapshot_url": r.get("snapshot_url", ""),
                "aihe_saanto_v1": koodaa_aihe(ots, "v1"),
                "savy_saanto_v1": koodaa_savy(ots, "v1"),
                "aihe_saanto_v1b": koodaa_aihe(ots, "v1b"),
                "savy_saanto_v1b": koodaa_savy(ots, "v1b"),
                "aihe_ihminen_a": "",
                "savy_ihminen_a": "",
                "koodaaja_ihminen_a": "",
                "aihe_ihminen_b": "",
                "savy_ihminen_b": "",
                "koodaaja_ihminen_b": "",
                "koodakirja_versio": KOODIKIRJA,
            }
        )
    polku = TABLES / "koodaus_otos.csv"
    with polku.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kentat)
        w.writeheader()
        w.writerows(koodatut)

    aihe_a = [r["aihe_saanto_v1"] for r in koodatut]
    aihe_b = [r["aihe_saanto_v1b"] for r in koodatut]
    savy_a = [r["savy_saanto_v1"] for r in koodatut]
    savy_b = [r["savy_saanto_v1b"] for r in koodatut]
    alpha_aihe = pari_alpha(aihe_a, aihe_b)
    alpha_savy = pari_alpha(savy_a, savy_b)

    n_media: dict[str, int] = defaultdict(int)
    n_aihe: dict[str, int] = defaultdict(int)
    n_savy: dict[str, int] = defaultdict(int)
    for r in koodatut:
        n_media[r["media"]] += 1
        n_aihe[r["aihe_saanto_v1"]] += 1
        if r["savy_saanto_v1"]:
            n_savy[r["savy_saanto_v1"]] += 1

    def _fmt(x: float) -> str:
        return "" if x != x else f"{x:.6f}"

    yht_kentat = ["tunnus", "arvo", "huom"]
    yht = [
        {"tunnus": "siemen", "arvo": str(SIEMEN), "huom": ""},
        {"tunnus": "n_otos", "arvo": str(len(koodatut)), "huom": "tasakiintiö medioittain"},
        {"tunnus": "n_kaksoiskoodattu_saanto", "arvo": str(len(koodatut)), "huom": "saanto-v1 vs saanto-v1b"},
        {"tunnus": "n_ihminen", "arvo": "0", "huom": "ihmiskentät tyhjiä"},
        {"tunnus": "alpha_aihe_saanto", "arvo": _fmt(alpha_aihe), "huom": "TUTKIVA; ei ihmis-α"},
        {
            "tunnus": "alpha_savy_saanto",
            "arvo": _fmt(alpha_savy),
            "huom": "vain parit joissa molemmilla luokka; tyhjä pois",
        },
        {
            "tunnus": "n_savy_paria_molemmat",
            "arvo": str(sum(1 for a, b in zip(savy_a, savy_b) if a and b)),
            "huom": "α-sävyn otos",
        },
        {
            "tunnus": "n_savy_vain_v1b",
            "arvo": str(sum(1 for a, b in zip(savy_a, savy_b) if not a and b)),
            "huom": "v1 tyhjä, v1b luokka; ei α-parissa",
        },
        {"tunnus": "alpha_aihe_ihminen", "arvo": "", "huom": "ei kahta ihmiskoodaajaa"},
        {"tunnus": "alpha_savy_ihminen", "arvo": "", "huom": "ei kahta ihmiskoodaajaa"},
        {"tunnus": "koodakirja_versio", "arvo": KOODIKIRJA, "huom": ""},
    ]
    for m, n in sorted(n_media.items()):
        yht.append({"tunnus": f"n_{m}", "arvo": str(n), "huom": ""})
    for luokka in list(AIHE_JARJESTYS) + ["muu"]:
        yht.append({"tunnus": f"n_aihe_v1_{luokka}", "arvo": str(n_aihe.get(luokka, 0)), "huom": "saanto-v1"})
    for luokka in SAVY_JARJESTYS:
        yht.append({"tunnus": f"n_savy_v1_{luokka}", "arvo": str(n_savy.get(luokka, 0)), "huom": "saanto-v1; tyhjä ei neutraali"})
    yht.append(
        {
            "tunnus": "n_savy_v1_tyhja",
            "arvo": str(sum(1 for r in koodatut if not r["savy_saanto_v1"])),
            "huom": "ei merkkiosumaa",
        }
    )
    with (TABLES / "koodaus_yhteenveto.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=yht_kentat)
        w.writeheader()
        w.writerows(yht)

    f1_rivit = [_f1(aihe_a, aihe_b, luokka) for luokka in list(AIHE_JARJESTYS) + ["muu"]]
    savy_parit_a: list[str] = []
    savy_parit_b: list[str] = []
    for a, b in zip(savy_a, savy_b):
        if a or b:
            savy_parit_a.append(a)
            savy_parit_b.append(b)
    for luokka in SAVY_JARJESTYS:
        rivi = _f1(savy_parit_a, savy_parit_b, luokka)
        rivi["luokka"] = f"savy:{luokka}"
        f1_rivit.append(rivi)
    with (TABLES / "koodaus_f1.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(f1_rivit[0].keys()))
        w.writeheader()
        w.writerows(f1_rivit)
    print("kirjoitettu", polku, flush=True)


if __name__ == "__main__":
    aja()
