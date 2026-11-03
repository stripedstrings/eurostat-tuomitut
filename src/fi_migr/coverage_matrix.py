"""FI-paneeli: peittomatriisi indikaattori × vuosi. Ei täyttöä, ei välittäjiä."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.fi_migr.paths import DOCS, HAETTU, TABLES

VUOSI_MIN = 1990
VUOSI_MAX = 2025

# Kaikki indikaattorit, myös tyhjät (näytetään matriisissa).
INDIKAATTORIT: list[tuple[str, str, str, Path | None]] = [
    ("tulot_maahanmuutto", "StatFin", "11a8.px", TABLES / "fi_migr_tulot_vuosi.csv"),
    ("vaesto_osuudet", "StatFin", "159t.px", TABLES / "fi_migr_vaesto_osuudet.csv"),
    ("ika_sukupuoli_syntypera", "StatFin", "11rt.px", TABLES / "fi_migr_ika_sukupuoli.csv"),
    ("tyollisyys", "Eurostat", "lfsa_ergan/urgan FI", TABLES / "fi_migr_tyollisyys.csv"),
    ("koulutus", "Eurostat", "edat_lfs_9911 FI", TABLES / "fi_migr_koulutus.csv"),
    ("oleskeluluvat", "Eurostat", "migr_res* FI", TABLES / "fi_migr_luvat.csv"),
    ("kiintiopakolaiset_saapuneet", "Migri", "kiintiopakolaistilastot", TABLES / "fi_migr_kiintio.csv"),
    ("kiintiopakolaiset_paatetty", "Migri", "meta / Yhteensä", TABLES / "fi_migr_kiintio_meta.csv"),
    ("kielitaito_taso", "Kotoutuminen", "PxWeb (ei vastannut)", None),
    ("kieli_oppimisaika_kk", "—", "ei avointa aikasarjaa", None),
    ("eurostat_migr_imm1ctz", "Eurostat", "HTTP 413 / ei FI-aikasarjaa", None),
    ("eurostat_migr_asy", "Eurostat", "HTTP 413 / ei FI-aikasarjaa", None),
]

MONIVERTAILU = (
    "Monivertailuvaroitus: indikaattoreita ei pidä tulkita samanaikaisesti "
    "ikään kuin ne olisivat yhteismitallisia. StatFin-syntyperä ≠ "
    "Eurostat-kansalaisuus ≠ Migri-kiintiö/pakolaisuus. Usean testin / "
    "usean indikaattorin rinnakkain asettelu ei ole yhteisjohtopäätös."
)


def _vuodet_tiedostosta(polku: Path | None) -> set[int]:
    if polku is None or not polku.exists():
        return set()
    df = pd.read_csv(polku)
    if "vuosi" not in df.columns:
        return set()
    v = pd.to_numeric(df["vuosi"], errors="coerce").dropna()
    # meta: tyhjä vuosi-rivi (yleinen asettaja) ei lasketa peitoksi
    return {int(x) for x in v if VUOSI_MIN <= int(x) <= VUOSI_MAX}


def matriisi() -> pd.DataFrame:
    vuodet = list(range(VUOSI_MIN, VUOSI_MAX + 1))
    rivit = []
    for ind, lahde, koodi, polku in INDIKAATTORIT:
        years = _vuodet_tiedostosta(polku)
        row: dict[str, object] = {
            "indikaattori": ind,
            "lahde": lahde,
            "koodi": koodi,
            "n_vuotta_peitto": len(years),
            "saatavuus": "kylla" if years else "ei",
        }
        for y in vuodet:
            # 1 = havainto vuodelle; tyhjä = puuttuu (ei nolla-imputointia)
            row[str(y)] = 1 if y in years else ""
        rivit.append(row)
    return pd.DataFrame(rivit)


def peitto_yhteenveto(m: pd.DataFrame) -> pd.DataFrame:
    vuosi_cols = [c for c in m.columns if c.isdigit()]
    out = []
    for _, r in m.iterrows():
        peitot = [int(c) for c in vuosi_cols if r[c] == 1]
        out.append(
            {
                "indikaattori": r["indikaattori"],
                "lahde": r["lahde"],
                "koodi": r["koodi"],
                "saatavuus": r["saatavuus"],
                "vuosi_min": min(peitot) if peitot else "",
                "vuosi_max": max(peitot) if peitot else "",
                "n_vuotta_peitto": r["n_vuotta_peitto"],
                "huom": "" if peitot else "ei aikasarjaa; ei välittäjämuuttujaa",
            }
        )
    return pd.DataFrame(out)


def vahvista_kiintio_meta() -> pd.DataFrame:
    """Asettaja + hakupäivä; päätöspäivämäärä vain jos lähteessä (muuten tyhjä)."""
    p = TABLES / "fi_migr_kiintio_meta.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p)
    if "asettaja" not in df.columns:
        df["asettaja"] = (
            "Suomen valtioneuvosto (esitys) / eduskunta (päätös); "
            "UNHCR ei aseta Suomen vuosikiintiötä"
        )
    if "haettu" not in df.columns:
        df["haettu"] = HAETTU
    # Älä keksi päätöspäivää
    if "paatos_pvm" not in df.columns:
        df["paatos_pvm"] = pd.NA
    df["paatos_pvm_huom"] = (
        "tyhjä = Migri-sivulta ei poimittu päätöksen päivämäärää; ei arvioida"
    )
    df.to_csv(p, index=False, encoding="utf-8")
    return df


def kirjoita_md(yht: pd.DataFrame) -> Path:
    rivit = [
        "# FI peittomatriisi (indikaattori × vuosi)",
        "",
        f"Haettu/rakennettu: {HAETTU}. TUTKIVA. Puuttuva solussa = tyhjä, ei nolla.",
        "",
        MONIVERTAILU,
        "",
        "## Yhteenveto",
        "",
        "| indikaattori | lähde | saatavuus | vuodet | n |",
        "|---|---|---|---|---:|",
    ]
    for r in yht.itertuples(index=False):
        jakso = (
            f"{r.vuosi_min}–{r.vuosi_max}" if r.vuosi_min != "" else "—"
        )
        rivit.append(
            f"| {r.indikaattori} | {r.lahde} {r.koodi} | {r.saatavuus} | {jakso} | {r.n_vuotta_peitto} |"
        )
    rivit.extend(
        [
            "",
            "## Kiintiöt",
            "",
            "Asettaja: Suomen valtioneuvosto / eduskunta. UNHCR ehdottaa henkilöitä.",
            f"Hakupäivä (Migri-sivu): `{HAETTU}`. `paatos_pvm` tyhjä, jos ei lähteessä.",
            "Taulu: `fi_migr_kiintio_meta.csv`.",
            "",
            "Laaja matriisi: `fi_migr_peitto_matriisi.csv` (1 = peitto, tyhjä = aukko).",
            "",
        ]
    )
    out = TABLES / "FI_MIGR_PEITTO.md"
    out.write_text("\n".join(rivit), encoding="utf-8")
    return out


def aja() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    vahvista_kiintio_meta()
    m = matriisi()
    yht = peitto_yhteenveto(m)
    m.to_csv(TABLES / "fi_migr_peitto_matriisi.csv", index=False, encoding="utf-8")
    yht.to_csv(TABLES / "fi_migr_peitto.csv", index=False, encoding="utf-8")
    md = kirjoita_md(yht)
    DOCS.mkdir(parents=True, exist_ok=True)
    for nimi in (
        "fi_migr_peitto_matriisi.csv",
        "fi_migr_peitto.csv",
        "fi_migr_kiintio_meta.csv",
        "FI_MIGR_PEITTO.md",
    ):
        src = TABLES / nimi
        if src.exists():
            (DOCS / nimi).write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print("kirjoitettu", TABLES / "fi_migr_peitto_matriisi.csv")
    print("kirjoitettu", md)


if __name__ == "__main__":
    aja()
