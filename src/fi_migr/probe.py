"""Vaihe 0: lähteiden saatavuustesti. Ei täyttöä, ei arvattuja koodeja."""

from __future__ import annotations

import csv
import json
import subprocess
from datetime import date
from pathlib import Path

from src.config import CACHE_DIR, ROOT
from src.fi_migr.paths import INTERIM, TABLES
from src.national.common import kirjaa_manifest

USER_AGENT = "eu-rikollisuus-kansalaisuus/0.1 (tutkimuskäyttö; FI-migr-probe)"
SDMX = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{code}"
    "?format=SDMX-CSV&geo=FI&lastNObservations=1"
)

EUROSTAT_KOODIT = (
    ("migr_imm1ctz", "maahanmuutto kansalaisuuden mukaan"),
    ("migr_imm3ctb", "maahanmuutto syntymämaan mukaan"),
    ("migr_asyappctza", "turvapaikkahakemukset"),
    ("migr_asydcfsta", "turvapaikkapäätökset"),
    ("migr_pop1ctz", "väestö ikä×sukupuoli×kansalaisuus (välimuisti)"),
    ("lfsa_ergan", "työllisyysaste kansalaisuus (välimuisti)"),
    ("lfsa_urgan", "työttömyysaste kansalaisuus (välimuisti)"),
    ("edat_lfs_9911", "koulutusaste kansalaisuus (välimuisti)"),
    ("migr_resfirst", "ensimmäiset oleskeluluvat (välimuisti)"),
    ("migr_resvalid", "voimassa olevat luvat (välimuisti)"),
)

STATFIN_URLS = (
    (
        "statfin_vaerak_pxt_11ra",
        "https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/vaerak/statfin_vaerak_pxt_11ra.px",
        "väestö syntyperän mukaan (ehdokas)",
    ),
    (
        "statfin_muutl_pxt_11a8",
        "https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/muutl/statfin_muutl_pxt_11a8.px",
        "maahan-/maastamuutto (ehdokas)",
    ),
)

HTTP_URLS = (
    ("migri_tilastot", "https://tilastot.migri.fi/", "Migri tilastopalvelu"),
    (
        "migri_kiintio",
        "https://migri.fi/kiintiopakolaistilastot",
        "Migri kiintiöpakolaistilastot",
    ),
    (
        "kotoutuminen_indikaattorit",
        "https://kotoutuminen.fi/kotoutumisen-indikaattorit-tietokanta",
        "Kotoutumisen indikaattorit (kuvaussivu)",
    ),
    (
        "kotoutuminen_pxweb",
        "https://kototietokannat.stat.fi/PXWeb/pxweb/fi/Kotoutumisenindikaattorit/",
        "Kotoutumisen indikaattorit PxWeb (ehdokas)",
    ),
)


def _curl_meta(url: str, out: Path | None = None, max_bytes: int = 0) -> tuple[int, int]:
    """Palauta (http_koodi, tavut). Timeout 45 s."""
    dest = str(out) if out else "NUL"
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "curl.exe",
        "-sS",
        "-L",
        "-A",
        USER_AGENT,
        "--max-time",
        "45",
        "-w",
        "%{http_code}",
        "-o",
        dest,
        url,
    ]
    if max_bytes > 0:
        cmd.insert(-1, "--max-filesize")
        cmd.insert(-1, str(max_bytes))
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=55, check=False)
        code_s = (p.stdout or "").strip()[-3:]
        try:
            code = int(code_s)
        except ValueError:
            code = 0
        size = out.stat().st_size if out and out.exists() else 0
        return code, size
    except (OSError, subprocess.TimeoutExpired):
        return 0, 0


def _eurostat_rivi(koodi: str, kuvaus: str) -> dict[str, str]:
    cache = CACHE_DIR / f"{koodi}.csv"
    if cache.exists() and cache.stat().st_size > 1000:
        # Pikainen FI-peitto välimuistista
        try:
            import pandas as pd

            df = pd.read_csv(cache, usecols=lambda c: c in {"geo", "GEO", "TIME_PERIOD"}, low_memory=False)
            geo_col = "geo" if "geo" in df.columns else ("GEO" if "GEO" in df.columns else None)
            n_fi = int((df[geo_col].astype(str) == "FI").sum()) if geo_col else -1
            return {
                "lahde": "Eurostat",
                "koodi": koodi,
                "kuvaus": kuvaus,
                "url": SDMX.format(code=koodi),
                "http": "200",
                "tavut": str(cache.stat().st_size),
                "saatavuus": "kylla" if n_fi > 0 else "osittainen",
                "huom": f"välimuisti; FI-rivejä≈{n_fi}",
            }
        except Exception as e:  # noqa: BLE001
            return {
                "lahde": "Eurostat",
                "koodi": koodi,
                "kuvaus": kuvaus,
                "url": SDMX.format(code=koodi),
                "http": "200",
                "tavut": str(cache.stat().st_size),
                "saatavuus": "osittainen",
                "huom": f"välimuisti; lukuvirhe={type(e).__name__}",
            }
    dest = INTERIM / f"probe_{koodi}.csv"
    code, size = _curl_meta(SDMX.format(code=koodi), dest, max_bytes=500_000)
    ok = code == 200 and size > 200
    huom = "FI-suodatettu SDMX-CSV-näyte" if ok else "ei dataa / virhe"
    if ok:
        try:
            txt = dest.read_text(encoding="utf-8", errors="replace")[:2000]
            if "FI" not in txt and "geo" in txt.lower():
                huom = "HTTP200 mutta FI ei näy näytteessä"
                ok = False
        except OSError:
            pass
    return {
        "lahde": "Eurostat",
        "koodi": koodi,
        "kuvaus": kuvaus,
        "url": SDMX.format(code=koodi),
        "http": str(code),
        "tavut": str(size),
        "saatavuus": "kylla" if ok else "ei",
        "huom": huom,
    }


def _statfin_rivi(koodi: str, url: str, kuvaus: str) -> dict[str, str]:
    dest = INTERIM / f"probe_{koodi}.json"
    code, size = _curl_meta(url, dest)
    saat = "kylla" if code == 200 and size > 50 else "ei"
    huom = "PxWeb meta JSON"
    if saat == "kylla":
        try:
            meta = json.loads(dest.read_text(encoding="utf-8"))
            title = meta.get("title") or meta.get("label") or ""
            huom = f"PxWeb meta; title={title[:80]}"
        except (OSError, json.JSONDecodeError):
            huom = "HTTP200 mutta JSON ei parseudu"
            saat = "ei"
    return {
        "lahde": "StatFin",
        "koodi": koodi,
        "kuvaus": kuvaus,
        "url": url,
        "http": str(code),
        "tavut": str(size),
        "saatavuus": saat,
        "huom": huom,
    }


def _http_rivi(koodi: str, url: str, kuvaus: str) -> dict[str, str]:
    dest = INTERIM / f"probe_{koodi}.html"
    code, size = _curl_meta(url, dest, max_bytes=80_000)
    saat = "kylla" if code == 200 and size > 100 else "ei"
    return {
        "lahde": "HTTP",
        "koodi": koodi,
        "kuvaus": kuvaus,
        "url": url,
        "http": str(code),
        "tavut": str(size),
        "saatavuus": saat,
        "huom": "sivutason saatavuus; ei vielä aikasarjaa",
    }


def aja() -> Path:
    INTERIM.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    rivit: list[dict[str, str]] = []
    for koodi, kuvaus in EUROSTAT_KOODIT:
        print(f"probe Eurostat {koodi}...", flush=True)
        rivit.append(_eurostat_rivi(koodi, kuvaus))
    for koodi, url, kuvaus in STATFIN_URLS:
        print(f"probe StatFin {koodi}...", flush=True)
        rivit.append(_statfin_rivi(koodi, url, kuvaus))
    for koodi, url, kuvaus in HTTP_URLS:
        print(f"probe HTTP {koodi}...", flush=True)
        rivit.append(_http_rivi(koodi, url, kuvaus))

    # Kielitaidon oppimisaika: ei ehdokasta ilman avointa aikasarjaa
    rivit.append(
        {
            "lahde": "—",
            "koodi": "kieli_oppimisaika_kk",
            "kuvaus": "kielitaidon oppimisaika kuukausina",
            "url": "",
            "http": "",
            "tavut": "0",
            "saatavuus": "ei",
            "huom": "ei avointa aikasarjaa; ei estimoida",
        }
    )

    polku = TABLES / "fi_migr_saatavuus.csv"
    with polku.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rivit[0].keys()))
        w.writeheader()
        w.writerows(rivit)

    md = ROOT / "FI_MIGR_DATA_SOURCES.md"
    lines = [
        "# FI maahanmuuttopaneeli — datalähteet (TUTKIVA)",
        "",
        f"Probe {date.today().isoformat()}. Koodeja ei arvattu. Puuttuva = puuttuva.",
        "",
        "| lähde | koodi | saatavuus | http | huom |",
        "|---|---|---|---:|---|",
    ]
    for r in rivit:
        lines.append(
            f"| {r['lahde']} | `{r['koodi']}` | {r['saatavuus']} | {r['http']} | {r['huom']} |"
        )
    lines += [
        "",
        "Kiintiön asettaja (meta, ei arvattu): Suomen valtioneuvosto / eduskunnan",
        "hyväksymä vuosittainen pakolaiskiintiö; UNHCR ehdottaa henkilöitä.",
        "Lähde dokumentoidaan `fi_migr_kiintio_meta.csv`:hen haun yhteydessä.",
        "",
    ]
    md.write_text("\n".join(lines), encoding="utf-8")
    kirjaa_manifest(
        "fi_migr/fi_migr_saatavuus.csv",
        "probe",
        str(polku),
        f"n={len(rivit)}; TUTKIVA",
    )
    print("kirjoitettu", polku, flush=True)
    return polku


if __name__ == "__main__":
    aja()
