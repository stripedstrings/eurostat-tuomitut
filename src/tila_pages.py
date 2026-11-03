"""docs/tutkimus/tila.html — hankkeen tilannekuva (ei tulkintaa)."""

from __future__ import annotations

import html
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from src.config import DOCS_DIR, ROOT, TABLES_DIR

OUT_HTML = DOCS_DIR / "tutkimus" / "tila.html"
OUT_CSV = TABLES_DIR / "tila_yhteenveto.csv"
OUT_MD = DOCS_DIR / "tutkimus" / "TILA.md"


def _git_head() -> str:
    try:
        p = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        return (p.stdout or "").strip() or "?"
    except (OSError, subprocess.TimeoutExpired):
        return "?"


def _pytest_tulos() -> tuple[str, str]:
    try:
        p = subprocess.run(
            [str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "pytest", "-q", "--tb=no"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=180,
        )
        rivit = (p.stdout or "") + (p.stderr or "")
        viime = [ln.strip() for ln in rivit.splitlines() if ln.strip()]
        tiivis = viime[-1] if viime else f"exit={p.returncode}"
        tila = "ok" if p.returncode == 0 else "fail"
        return tila, tiivis[:500]
    except (OSError, subprocess.TimeoutExpired) as e:
        return "ei_ajettu", str(e)[:200]


def _manifest_haku() -> str:
    man = ROOT / "data" / "raw" / "MANIFEST.csv"
    if not man.exists():
        return ""
    df = pd.read_csv(man)
    col = "hakupäivä" if "hakupäivä" in df.columns else ("haettu" if "haettu" in df.columns else None)
    if col is None:
        return ""
    return ", ".join(sorted({str(x) for x in df[col].dropna().unique()}))


def _rivit(commit: str, test_tila: str, test_tiivis: str) -> list[dict[str, str]]:
    return [
        {
            "osio": "meta",
            "avain": "sivu_paivitetty",
            "arvo": date.today().isoformat(),
            "huom": "tila-sivun generointi",
        },
        {
            "osio": "meta",
            "avain": "git_commit",
            "arvo": commit,
            "huom": "HEAD lyhyt hash generointihetkellä",
        },
        {
            "osio": "esirekisterointi",
            "avain": "K1_PREREGISTRATION",
            "arvo": "2026-11-01",
            "huom": "PREREGISTRATION.md; ei sokko (tutkiva visualisointi ennen)",
        },
        {
            "osio": "esirekisterointi",
            "avain": "MEDIA_PREREGISTRATION",
            "arvo": "2026-11-01",
            "huom": "lisäys ihmiskoodaus/mediat 2026-11-03 ennen täyttöä",
        },
        {
            "osio": "data_haku",
            "avain": "eurostat_MANIFEST_hakupaivat",
            "arvo": _manifest_haku() or "ks. data/raw/MANIFEST.csv",
            "huom": "K1/K2 Eurostat-välimuisti",
        },
        {
            "osio": "data_haku",
            "avain": "FI_migr_HAETTU",
            "arvo": "2026-11-03",
            "huom": "src/fi_migr/paths.py HAETTU; StatFin/Migri",
        },
        {
            "osio": "data_haku",
            "avain": "media_vaiheet",
            "arvo": "2026-11-01…2026-11-03",
            "huom": "CDX/HTML/koodaus/analyysi; ks. MEDIA_DATA_SOURCES.md",
        },
        {
            "osio": "kattavuus",
            "avain": "K1_coverage_matrix",
            "arvo": "output/tables/coverage_matrix.csv",
            "huom": "maa × vuosi × muuttuja",
        },
        {
            "osio": "kattavuus",
            "avain": "FI_peitto_matriisi",
            "arvo": "output/tables/fi_migr/fi_migr_peitto_matriisi.csv",
            "huom": "indikaattori × vuosi; tyhjät mukana",
        },
        {
            "osio": "kattavuus",
            "avain": "media_coverage_vuosi_aukot",
            "arvo": "media/output/tables/coverage_media_vuosi_aukot.csv",
            "huom": "CDX vs HTML; ei täyttöä",
        },
        {
            "osio": "testit",
            "avain": "pytest",
            "arvo": test_tila,
            "huom": test_tiivis,
        },
        {
            "osio": "ei_testattavat",
            "avain": "K1_S2",
            "arvo": "ei_dataa",
            "huom": "citizen vain FOR,NAT,TOTAL — s2_s7_tila.csv",
        },
        {
            "osio": "ei_testattavat",
            "avain": "K1_S7",
            "arvo": "ei_dataa",
            "huom": "ei naturalisaatiota rikosaineistossa",
        },
        {
            "osio": "ei_testattavat",
            "avain": "K1_S4",
            "arvo": "ei_dataa",
            "huom": "unit=NR,P_HTHAB; henkilö vs tapaus ei dimensiossa",
        },
        {
            "osio": "ei_testattavat",
            "avain": "Media_H3",
            "arvo": "ei_testattavissa",
            "huom": "ei julkaisijan klikkianalytiikkaa",
        },
        {
            "osio": "ei_testattavat",
            "avain": "Media_H4",
            "arvo": "ei_testattavissa",
            "huom": "odottaa ihmis-sävyn kaksoiskoodausta",
        },
        {
            "osio": "ei_testattavat",
            "avain": "Media_H6",
            "arvo": "ei_testattavissa",
            "huom": "ei tuho/tuhoutuminen-luokkia + odottaa koodausta",
        },
        {
            "osio": "ei_testattavat",
            "avain": "Media_H7_paa",
            "arvo": "ei_testattavissa",
            "huom": "ei aihekoodia 2015–2025; entropia TUTKIVA erillään",
        },
        {
            "osio": "ei_testattavat",
            "avain": "Media_ihmis_koodaus",
            "arvo": "kesken",
            "huom": "lomakkeet A/B valmiina; n_ihminen=0",
        },
        {
            "osio": "ei_testattavat",
            "avain": "Brå_CSV",
            "arvo": "ei",
            "huom": "määritelmä syntymämaa/bakgrund; CSV puuttuu",
        },
    ]


def _html_taulu(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0, classes="taulu", escape=True)


def aja() -> Path:
    from src.site import aihe_nav, ristiviittaukset

    commit = _git_head()
    test_tila, test_tiivis = _pytest_tulos()
    rivit = _rivit(commit, test_tila, test_tiivis)
    df = pd.DataFrame(rivit)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "tutkimus").mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    md_rivit = [
        "# Tutkimuksen tila",
        "",
        f"Generoitu: {date.today().isoformat()}. Commit: `{commit}`.",
        "",
        "Tämä sivu on tilannekuva (commit, esirekisteröinti, haku, peitto, testit,",
        "ei testattavat). **Ei johtopäätöksiä.**",
        "",
        "| osio | avain | arvo | huom |",
        "|---|---|---|---|",
    ]
    for r in rivit:
        md_rivit.append(
            f"| {r['osio']} | {r['avain']} | {r['arvo']} | {r['huom']} |"
        )
    OUT_MD.write_text("\n".join(md_rivit) + "\n", encoding="utf-8")

    by_osio = {k: g for k, g in df.groupby("osio", sort=False)}
    osiot_html = []
    otsikot = {
        "meta": "Commit ja päivitys",
        "esirekisterointi": "Esirekisteröintipäivämäärät",
        "data_haku": "Datan hakupäivämäärät",
        "kattavuus": "Kattavuus (peittomatriisit)",
        "testit": "Testitulos (pytest)",
        "ei_testattavat": "Ei testattavat / ei dataa",
    }
    for avain, otsikko in otsikot.items():
        if avain not in by_osio:
            continue
        osiot_html.append(f"<h2>{html.escape(otsikko)}</h2>")
        osiot_html.append(_html_taulu(by_osio[avain][["avain", "arvo", "huom"]]))

    sivu = f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Tutkimuksen tila</title>
  <link rel="stylesheet" href="../tyyli.css">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {aihe_nav(sijainti="tutkimus", aktiivinen="tutkimus")}
      <h1>Tutkimuksen tila</h1>
      <p class="lead">Commit, esirekisteröinti, datan haku, kattavuus, testitulos
      ja ei-testattavat kohdat. <strong>Ei tulkintaa tai yhteisjohtopäätöstä.</strong></p>
    </div>
  </header>
  <main class="wrap">
    <p>CSV: <a href="../../output/tables/tila_yhteenveto.csv">tila_yhteenveto.csv</a>
    (kopio generoinnissa) · <a href="TILA.md">TILA.md</a> ·
    <a href="index.html">← Tutkimus-hubi</a></p>
    {"".join(osiot_html)}
    {ristiviittaukset(aktiivinen="tutkimus", sijainti="tutkimus")}
  </main>
  <script src="../sivu.js"></script>
</body>
</html>
"""
    # korjaa CSV-linkki docs-suhteelliseksi
    docs_csv = DOCS_DIR / "tutkimus" / "tila_yhteenveto.csv"
    df.to_csv(docs_csv, index=False, encoding="utf-8")
    sivu = sivu.replace(
        'href="../../output/tables/tila_yhteenveto.csv"',
        'href="tila_yhteenveto.csv"',
    )
    OUT_HTML.write_text(sivu, encoding="utf-8")
    print("kirjoitettu", OUT_HTML)
    print("pytest", test_tila, test_tiivis)
    return OUT_HTML


if __name__ == "__main__":
    aja()
