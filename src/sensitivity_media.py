"""Vaihe 6: S1–S7 vs. P1-pää (otsikko, havaittu). Ei täyttöä, ei M4."""

from __future__ import annotations

import csv

from src.analyze_media import (
    RYHMA_JARJESTYS,
    _avaimet,
    _lue,
    _osuma,
    _rivi_osuus,
)
from src.fetch_media import TABLES
from src.wilson import clopper_pearson_ci, osuus, wilson_ci


def _f(v: float) -> str:
    return "" if v != v else f"{v:.6f}"


def _hae(p1: list[dict[str, str]], **ehdot: str) -> dict[str, str] | None:
    return next(
        (r for r in p1 if all(r.get(k) == v for k, v in ehdot.items())),
        None,
    )


def _vertailu(
    s: str,
    kuvaus: str,
    media: str,
    ryhma: str,
    paa: dict[str, str] | None,
    alt_x: int | None,
    alt_n: int | None,
    huom: str,
    s_ala: str = "",
    s_yla: str = "",
) -> dict[str, str]:
    if paa is None:
        p_s = (
            osuus(alt_x, alt_n)
            if alt_x is not None and alt_n is not None
            else float("nan")
        )
        if not s_ala and alt_x is not None and alt_n:
            lo, hi = wilson_ci(alt_x, alt_n)
            s_ala, s_yla = _f(lo), _f(hi)
        return {
            "s": s,
            "kuvaus": kuvaus,
            "media": media,
            "ryhma": ryhma,
            "n_paa": "",
            "osuus_paa": "",
            "n_s": "" if alt_n is None else str(alt_n),
            "osuus_s": _f(p_s),
            "ero": "",
            "paa_ala": "",
            "paa_yla": "",
            "s_ala": s_ala,
            "s_yla": s_yla,
            "huom": huom,
        }
    n_s = "" if alt_n is None else str(alt_n)
    if alt_x is None or alt_n is None:
        p_s = float("nan")
    else:
        p_s = osuus(alt_x, alt_n)
        if not s_ala and alt_n > 0:
            lo, hi = wilson_ci(alt_x, alt_n)
            s_ala, s_yla = _f(lo), _f(hi)
    p_paa = float(paa["osuus"]) if paa.get("osuus") else float("nan")
    ero = p_s - p_paa if p_s == p_s and p_paa == p_paa else float("nan")
    return {
        "s": s,
        "kuvaus": kuvaus,
        "media": media,
        "ryhma": ryhma,
        "n_paa": paa.get("n", ""),
        "osuus_paa": paa.get("osuus", ""),
        "n_s": n_s if alt_x is None else str(alt_n),
        "osuus_s": _f(p_s),
        "ero": _f(ero),
        "paa_ala": paa.get("wilson_ala", ""),
        "paa_yla": paa.get("wilson_yla", ""),
        "s_ala": s_ala,
        "s_yla": s_yla,
        "huom": huom,
    }


def aja() -> None:
    p1 = _lue("p1_entiteetti_osuus.csv")
    otsikot = _lue("tietueet_otsikko.csv")
    otos = _lue("koodaus_otos.csv")
    rivit: list[dict[str, str]] = []

    for media in ("iltalehti_etusivu", "yle_uutiset"):
        for ryhma in RYHMA_JARJESTYS:
            paa = _hae(
                p1,
                analyysi="P1",
                yksikko="otsikko",
                media=media,
                ryhma=ryhma,
                jakso="havaittu",
            )
            etu = _hae(
                p1,
                analyysi="P1",
                yksikko="etusivu",
                media=media,
                ryhma=ryhma,
                jakso="havaittu",
            )
            rivit.append(
                _vertailu(
                    "S1",
                    "etusivupäivä vs. otsikko (pää)",
                    media,
                    ryhma,
                    paa,
                    int(etu["x"]) if etu else None,
                    int(etu["n"]) if etu else None,
                    "pää = otsikko; S = etusivu (≥1 otsikko)",
                    s_ala=etu["wilson_ala"] if etu else "",
                    s_yla=etu["wilson_yla"] if etu else "",
                )
            )

    for ryhma in RYHMA_JARJESTYS:
        il = _hae(
            p1,
            analyysi="P1",
            yksikko="otsikko",
            media="iltalehti_etusivu",
            ryhma=ryhma,
            jakso="havaittu",
        )
        yle = _hae(
            p1,
            analyysi="P1",
            yksikko="otsikko",
            media="yle_uutiset",
            ryhma=ryhma,
            jakso="havaittu",
        )
        rivit.append(
            _vertailu(
                "S2",
                "Yle vs. IL (pää pitää molemmat)",
                "molemmat",
                ryhma,
                il,
                int(yle["x"]) if yle else None,
                int(yle["n"]) if yle else None,
                "osuus_paa=IL, osuus_s=Yle; kumpaakaan ei pudoteta päästä",
                s_ala=yle["wilson_ala"] if yle else "",
                s_yla=yle["wilson_yla"] if yle else "",
            )
        )

    for media in ("iltalehti_etusivu", "yle_uutiset"):
        for ryhma in RYHMA_JARJESTYS:
            paa = _hae(
                p1,
                analyysi="P1",
                yksikko="otsikko",
                media=media,
                ryhma=ryhma,
                jakso="havaittu",
            )
            v23 = _hae(
                p1,
                analyysi="P1",
                yksikko="otsikko",
                media=media,
                ryhma=ryhma,
                jakso="2023",
            )
            rivit.append(
                _vertailu(
                    "S3",
                    "vain 2023 vs. havaittu jakso (pää)",
                    media,
                    ryhma,
                    paa,
                    int(v23["x"]) if v23 else None,
                    int(v23["n"]) if v23 else None,
                    "ei HTML-vuotta ei täytetä",
                    s_ala=v23["wilson_ala"] if v23 else "",
                    s_yla=v23["wilson_yla"] if v23 else "",
                )
            )

    n_otos = len(otos)
    for ryhma in RYHMA_JARJESTYS:
        x_ent = sum(1 for r in otos if _osuma_otsikosta(r.get("otsikko", ""), ryhma))
        x_aihe = sum(1 for r in otos if (r.get("aihe_saanto_v1") or "") == ryhma)
        paa_r = _rivi_osuus(x_ent, n_otos)
        rivit.append(
            _vertailu(
                "S4",
                "sääntöaihe vs. entiteettiosuma, otos 500",
                "otos",
                ryhma,
                paa_r,
                x_aihe,
                n_otos,
                "TUTKIVA; ihmisaihe tyhjä; koko ruudukkoa ei koodattu",
            )
        )

    savy_merkityt = [r for r in otos if (r.get("savy_saanto_v1") or "").strip()]
    n_merk = len(savy_merkityt)
    for luokka in ("uhka", "pelko", "viha"):
        x_m = sum(1 for r in savy_merkityt if r.get("savy_saanto_v1") == luokka)
        x_t = sum(1 for r in otos if r.get("savy_saanto_v1") == luokka)
        paa_s = _rivi_osuus(x_m, n_merk) if n_merk else None
        rivit.append(
            _vertailu(
                "S5",
                "tyhjä→neutraali (tutkiva) vs. vain merkitty (pää)",
                "otos",
                f"savy:{luokka}",
                paa_s,
                x_t,
                n_otos,
                "täyttö ei pääanalyysi; tyhjä ei ole neutraali päässä",
            )
        )
    x_neu = sum(1 for r in otos if not (r.get("savy_saanto_v1") or "").strip())
    rivit.append(
        _vertailu(
            "S5",
            "tyhjä→neutraali (tutkiva) vs. vain merkitty (pää)",
            "otos",
            "savy:neutraali",
            None,
            x_neu,
            n_otos,
            "TUTKIVA täyttö; päässä ei neutraali-luokkaa",
        )
    )

    ots_ok = [r for r in otsikot if (r.get("otsikko") or "").strip()]
    ots_40 = [r for r in ots_ok if len(r["otsikko"]) >= 40]
    for media in ("iltalehti_etusivu", "yle_uutiset"):
        osat = [r for r in ots_40 if r["media"] == media]
        n40 = len(osat)
        for ryhma in RYHMA_JARJESTYS:
            paa = _hae(
                p1,
                analyysi="P1",
                yksikko="otsikko",
                media=media,
                ryhma=ryhma,
                jakso="havaittu",
            )
            x = sum(1 for r in osat if _osuma(_avaimet(r.get("entiteetti", "")), ryhma))
            rivit.append(
                _vertailu(
                    "S6",
                    "pituus ≥40 vs. ≥18 (pää, poiminta)",
                    media,
                    ryhma,
                    paa,
                    x,
                    n40,
                    "puuttuvaa otsikkoa ei keksitä",
                )
            )

    for media in ("iltalehti_etusivu", "yle_uutiset"):
        for ryhma in RYHMA_JARJESTYS:
            paa = _hae(
                p1,
                analyysi="P1",
                yksikko="otsikko",
                media=media,
                ryhma=ryhma,
                jakso="havaittu",
            )
            if paa is None:
                continue
            x, n = int(paa["x"]), int(paa["n"])
            lo, hi = clopper_pearson_ci(x, n)
            rivit.append(
                _vertailu(
                    "S7",
                    "Clopper–Pearson 95 % vs. Wilson 95 % (pää)",
                    media,
                    ryhma,
                    paa,
                    x,
                    n,
                    "osuus sama; vaihtuu väli",
                    s_ala=_f(lo),
                    s_yla=_f(hi),
                )
            )

    kentat = [
        "s",
        "kuvaus",
        "media",
        "ryhma",
        "n_paa",
        "osuus_paa",
        "n_s",
        "osuus_s",
        "ero",
        "paa_ala",
        "paa_yla",
        "s_ala",
        "s_yla",
        "huom",
    ]
    polku = TABLES / "herkkyys_media_S1_S7.csv"
    with polku.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kentat)
        w.writeheader()
        w.writerows(rivit)

    yht = []
    for koodi in ("S1", "S2", "S3", "S4", "S5", "S6", "S7"):
        osat = [r for r in rivit if r["s"] == koodi]
        erot = [float(r["ero"]) for r in osat if r["ero"]]
        yht.append(
            {
                "s": koodi,
                "n_rivia": str(len(osat)),
                "ero_min": _f(min(erot) if erot else float("nan")),
                "ero_max": _f(max(erot) if erot else float("nan")),
                "kuvaus": osat[0]["kuvaus"] if osat else "",
            }
        )
    with (TABLES / "herkkyys_media_yhteenveto.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["s", "n_rivia", "ero_min", "ero_max", "kuvaus"])
        w.writeheader()
        w.writerows(yht)
    print("kirjoitettu", polku, flush=True)


def _osuma_otsikosta(otsikko: str, ryhma: str) -> bool:
    from src.analyze_media import RYHMAT

    t = otsikko.lower()
    return any(a in t for a in RYHMAT[ryhma])


if __name__ == "__main__":
    aja()
