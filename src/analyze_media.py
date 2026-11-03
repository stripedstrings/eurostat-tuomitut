"""Vaihe 5: P1–P5 ja H1–H7. Ei täyttöä, ei M4, ei validoimatonta sävyä."""

from __future__ import annotations

import csv
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

from src.fetch_media import TABLES
from src.parse_media import ENTITEETTI_AVAIMET
from src.wilson import osuus, wilson_ci

D_MIN = 10
RYHMAT: dict[str, tuple[str, ...]] = {
    "putin": ("putin",),
    "zelenskyi": ("zelenskyi", "zelenskyy", "zelenskiy", "zelensky", "zelenski"),
    "presidentti": ("tasavallan presidentti", "suomen presidentti"),
    "maahanmuutto": ("maahanmuutto", "pakolais", "siirtolais"),
    "rikollisuus": ("rikollis", "rikos", "tuomittu", "tuomitut"),
    "terveys": ("terveysuhka", "epidemia", "pandemia"),
}
RYHMA_JARJESTYS = tuple(RYHMAT.keys())


def _avaimet(kentta: str) -> set[str]:
    return {p.strip() for p in (kentta or "").split(";") if p.strip()}


def _osuma(avaimet: set[str], ryhma: str) -> bool:
    return any(a in avaimet for a in RYHMAT[ryhma])


def _ensimmainen(avaimet: set[str]) -> str:
    for ryhma in RYHMA_JARJESTYS:
        if _osuma(avaimet, ryhma):
            return ryhma
    return "muu"


def _lue(nimi: str) -> list[dict[str, str]]:
    with (TABLES / nimi).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def _kelpaa_etusivu(r: dict[str, str]) -> bool:
    if not (r.get("http_tiedosto") or "").strip():
        return False
    try:
        return int(r.get("n_otsikkoa") or "0") > 0
    except ValueError:
        return False


def _rivi_osuus(x: int, n: int, **lisat: str) -> dict[str, str]:
    p = osuus(x, n)
    lo, hi = wilson_ci(x, n)
    merkitse = x < D_MIN or n < D_MIN

    def f(v: float) -> str:
        return "" if v != v else f"{v:.6f}"

    out = {
        "n": str(n),
        "x": str(x),
        "osuus": f(p),
        "wilson_ala": f(lo),
        "wilson_yla": f(hi),
        "d_lt_10": "1" if merkitse else "0",
    }
    out.update(lisat)
    return out


def p1_osuudet(
    etusivut: list[dict[str, str]], otsikot: list[dict[str, str]]
) -> list[dict[str, str]]:
    rivit: list[dict[str, str]] = []
    etu_ok = [r for r in etusivut if _kelpaa_etusivu(r)]
    ots_ok = [r for r in otsikot if (r.get("otsikko") or "").strip()]
    for yksikko, aine in (("etusivu", etu_ok), ("otsikko", ots_ok)):
        mediat = sorted({r["media"] for r in aine})
        for media in mediat:
            osat = [r for r in aine if r["media"] == media]
            n = len(osat)
            for ryhma in RYHMA_JARJESTYS:
                x = sum(1 for r in osat if _osuma(_avaimet(r.get("entiteetti", "")), ryhma))
                rivit.append(
                    _rivi_osuus(
                        x,
                        n,
                        analyysi="P1",
                        yksikko=yksikko,
                        media=media,
                        ryhma=ryhma,
                        jakso="havaittu",
                    )
                )
            vuodet = sorted({r["paiva"][:4] for r in osat})
            for vuosi in vuodet:
                v_osat = [r for r in osat if r["paiva"].startswith(vuosi)]
                nv = len(v_osat)
                for ryhma in RYHMA_JARJESTYS:
                    x = sum(
                        1
                        for r in v_osat
                        if _osuma(_avaimet(r.get("entiteetti", "")), ryhma)
                    )
                    rivit.append(
                        _rivi_osuus(
                            x,
                            nv,
                            analyysi="P1",
                            yksikko=yksikko,
                            media=media,
                            ryhma=ryhma,
                            jakso=vuosi,
                        )
                    )
    return rivit


def p2_otos_aihe(otos: list[dict[str, str]]) -> list[dict[str, str]]:
    rivit: list[dict[str, str]] = []
    luokat = sorted({r.get("aihe_saanto_v1") or "muu" for r in otos})
    for media in sorted({r["media"] for r in otos}):
        osat = [r for r in otos if r["media"] == media]
        n = len(osat)
        for luokka in luokat:
            x = sum(1 for r in osat if (r.get("aihe_saanto_v1") or "muu") == luokka)
            rivit.append(
                _rivi_osuus(
                    x,
                    n,
                    analyysi="P2",
                    yksikko="otsikko_otos",
                    media=media,
                    ryhma=luokka,
                    jakso="otos_500",
                    huom="TUTKIVA (ei esirekisteröity); ei ihmisaihetta",
                )
            )
    return rivit


def p4_pearson(p1: list[dict[str, str]]) -> list[dict[str, str]]:
    rivit: list[dict[str, str]] = []
    for yksikko in ("etusivu", "otsikko"):
        vek: dict[str, list[float]] = {}
        for media in ("iltalehti_etusivu", "yle_uutiset"):
            osuudet: list[float] = []
            for ryhma in RYHMA_JARJESTYS:
                osuma = next(
                    (
                        r
                        for r in p1
                        if r["analyysi"] == "P1"
                        and r["yksikko"] == yksikko
                        and r["media"] == media
                        and r["ryhma"] == ryhma
                        and r["jakso"] == "havaittu"
                    ),
                    None,
                )
                osuudet.append(float(osuma["osuus"]) if osuma and osuma["osuus"] else float("nan"))
            vek[media] = osuudet
        a = np.array(vek["iltalehti_etusivu"], dtype=float)
        b = np.array(vek["yle_uutiset"], dtype=float)
        ok = np.isfinite(a) & np.isfinite(b)
        r = float("nan")
        if ok.sum() >= 2 and np.nanstd(a[ok]) > 0 and np.nanstd(b[ok]) > 0:
            r = float(np.corrcoef(a[ok], b[ok])[0, 1])
        rivit.append(
            {
                "analyysi": "P4",
                "yksikko": yksikko,
                "pearson_r": "" if r != r else f"{r:.6f}",
                "n_ryhmaa": str(int(ok.sum())),
                "huom": "kaksi mediaa; ei maiden vertailua",
            }
        )
    return rivit


def h_taulu(p1: list[dict[str, str]], p4: list[dict[str, str]]) -> list[dict[str, str]]:
    def hae(media: str, yksikko: str, ryhma: str, jakso: str) -> dict[str, str] | None:
        return next(
            (
                r
                for r in p1
                if r["media"] == media
                and r["yksikko"] == yksikko
                and r["ryhma"] == ryhma
                and r["jakso"] == jakso
            ),
            None,
        )

    def _h(hid: str, tila: str, **k: str) -> dict[str, str]:
        pohja = {
            "h": hid,
            "tila": tila,
            "media": "",
            "yksikko": "",
            "ryhma": "",
            "jakso": "",
            "n": "",
            "x": "",
            "osuus": "",
            "wilson_ala": "",
            "wilson_yla": "",
            "d_lt_10": "",
            "huom": "",
        }
        pohja.update(k)
        return pohja

    out: list[dict[str, str]] = []
    for yksikko in ("etusivu", "otsikko"):
        r = hae("iltalehti_etusivu", yksikko, "putin", "2023")
        if r:
            out.append(_h("H1", "laskettu", **{k: r[k] for k in r if k != "analyysi"}))
        else:
            out.append(
                _h(
                    "H1",
                    "ei_nimittajaa",
                    media="iltalehti_etusivu",
                    yksikko=yksikko,
                    ryhma="putin",
                    jakso="2023",
                    huom="ei HTML-otsikoita 2023",
                )
            )
        for ryhma in ("presidentti", "putin", "zelenskyi"):
            r2 = hae("iltalehti_etusivu", yksikko, ryhma, "havaittu")
            r3 = hae("yle_uutiset", yksikko, ryhma, "havaittu")
            for rr in (r2, r3):
                if rr:
                    out.append(_h("H2", "laskettu", **{k: rr[k] for k in rr if k != "analyysi"}))
    out.append(_h("H3", "ei_testattavissa", huom="ei julkaisijan analytiikkaa"))
    out.append(_h("H4", "ei_testattavissa", huom="ei ihmis-sävyn aikasarjaa"))
    for r in p4:
        out.append(
            _h(
                "H5",
                "laskettu",
                yksikko=r["yksikko"],
                osuus=r["pearson_r"],
                n=r["n_ryhmaa"],
                huom="Pearson-r entiteettiosuuksista; " + r["huom"],
            )
        )
    out.append(_h("H6", "ei_testattavissa", huom="ei tuho/tuhoutuminen-luokkia"))
    out.append(
        _h(
            "H7",
            "ei_testattavissa",
            huom="ei aihekoodia 2015–2025; entropia tutkiva erillistaulussa",
        )
    )
    return out


def h7_entropia_tutkiva(otsikot: list[dict[str, str]]) -> list[dict[str, str]]:
    rivit: list[dict[str, str]] = []
    ots_ok = [r for r in otsikot if (r.get("otsikko") or "").strip()]
    for media in sorted({r["media"] for r in ots_ok}):
        osat = [r for r in ots_ok if r["media"] == media]
        vuodet = sorted({r["paiva"][:4] for r in osat})
        for vuosi in vuodet:
            v = [r for r in osat if r["paiva"].startswith(vuosi)]
            n = len(v)
            laskuri: dict[str, int] = defaultdict(int)
            for r in v:
                laskuri[_ensimmainen(_avaimet(r.get("entiteetti", "")))] += 1
            if n <= 0:
                h = float("nan")
            else:
                h = 0.0
                for c in laskuri.values():
                    p = c / n
                    if p > 0:
                        h -= p * math.log2(p)
            rivit.append(
                {
                    "media": media,
                    "vuosi": vuosi,
                    "n": str(n),
                    "entropia_bitti": "" if h != h else f"{h:.6f}",
                    "n_luokkaa": str(sum(1 for c in laskuri.values() if c > 0)),
                    "huom": "TUTKIVA (ei esirekisteröity); ensisijainen entiteetti tai muu",
                }
            )
    return rivit


def p5_ja_p3() -> list[dict[str, str]]:
    return [
        {
            "analyysi": "P3",
            "tila": "ei_testattavissa",
            "huom": "ihmissävy tyhjä; sääntösävyä ei aikasarjana",
        },
        {
            "analyysi": "P5",
            "tila": "ei_testattavissa",
            "huom": "ulkoisia indikaattoreita ei haettu; M4 vaiheessa 7",
        },
        {
            "analyysi": "P2_paa",
            "tila": "ei_testattavissa",
            "huom": "ihmisaihe tyhjä; otos TUTKIVA p2_aihe_otos.csv",
        },
    ]


def aja() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    etusivut = _lue("tietueet_etusivu.csv")
    otsikot = _lue("tietueet_otsikko.csv")
    otos = _lue("koodaus_otos.csv")
    p1 = p1_osuudet(etusivut, otsikot)
    p2 = p2_otos_aihe(otos)
    p4 = p4_pearson(p1)
    h = h_taulu(p1, p4)
    ent = h7_entropia_tutkiva(otsikot)
    p35 = p5_ja_p3()

    def _kirj(nimi: str, rivit: list[dict[str, str]]) -> None:
        if not rivit:
            return
        kentat: list[str] = []
        for r in rivit:
            for k in r:
                if k not in kentat:
                    kentat.append(k)
        with (TABLES / nimi).open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=kentat, extrasaction="ignore")
            w.writeheader()
            w.writerows(rivit)

    _kirj("p1_entiteetti_osuus.csv", p1)
    _kirj("p1_entiteetti_osuus_havaittu.csv", [r for r in p1 if r["jakso"] == "havaittu"])
    _kirj("p2_aihe_otos.csv", p2)
    _kirj("p4_mediavertailu.csv", p4)
    _kirj("h1_h7.csv", h)
    _kirj("h7_entropia_tutkiva.csv", ent)
    _kirj("p3_p5_tila.csv", p35)
    puuttuvat = [a for a in ENTITEETTI_AVAIMET if not any(a in v for v in RYHMAT.values())]
    if puuttuvat:
        raise RuntimeError(f"entiteettiavain ilman ryhmää: {puuttuvat}")
    print("kirjoitettu", TABLES / "p1_entiteetti_osuus.csv", flush=True)


if __name__ == "__main__":
    aja()
