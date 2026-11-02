"""Mediahaara vaihe 2: CDX-indeksi ja RSS-näyte. Ei täyttöä, ei koodausta."""

from __future__ import annotations

import csv
import json
import subprocess
import time
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlencode

from src.config import ROOT

RAW = ROOT / "media" / "data" / "raw"
TABLES = ROOT / "media" / "output" / "tables"
MANIFEST = RAW / "MANIFEST.csv"
USER_AGENT = "eurostat-tuomitut-media/0.2 (tutkimus; CDX-indeksi; ei massahakua HTML:ään)"
CDX = "https://web.archive.org/cdx/search/cdx"
ALKU = date(2015, 1, 1)
LOPPU = date(2025, 12, 31)

# Vain vaiheessa 1 vastanneet etusivu-URL:t. Ei uusia medioita ilman testiä.
MEDIT: list[dict[str, str]] = [
    {
        "media": "iltalehti_etusivu",
        "url": "www.iltalehti.fi/",
        "rss": "https://www.iltalehti.fi/rss.xml",
    },
    {
        "media": "yle_uutiset",
        "url": "yle.fi/uutiset",
        "rss": "https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss",
    },
]


def _paivat(a: date, b: date) -> list[date]:
    out: list[date] = []
    d = a
    while d <= b:
        out.append(d)
        d += timedelta(days=1)
    return out


def _curl(url: str, dest: Path, yritykset: int = 5) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    koodi = 0
    for i in range(yritykset):
        if i:
            time.sleep(3 * i)
        proc = subprocess.run(
            [
                "curl.exe",
                "-sS",
                "-L",
                "-A",
                USER_AGENT,
                "-o",
                str(dest),
                "-w",
                "%{http_code}",
                "--max-time",
                "120",
                url,
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        koodi = int(proc.stdout.strip() or "0")
        if koodi == 200 and dest.exists() and dest.stat().st_size > 0:
            return koodi
        if koodi in {429, 503, 0}:
            continue
        return koodi
    return koodi


def _kirjaa_manifest(tiedosto: str, lahde: str, url: str, kuvaus: str, huomiot: str) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    kentat = ["tiedosto", "lahde", "url", "hakupaiva", "kuvaus", "huomiot"]
    rivit: list[dict[str, str]] = []
    if MANIFEST.exists() and MANIFEST.stat().st_size > 0:
        with MANIFEST.open(encoding="utf-8", newline="") as f:
            rivit = list(csv.DictReader(f))
    rivit = [r for r in rivit if r.get("tiedosto") != tiedosto]
    rivit.append(
        {
            "tiedosto": tiedosto,
            "lahde": lahde,
            "url": url,
            "hakupaiva": date.today().isoformat(),
            "kuvaus": kuvaus,
            "huomiot": huomiot,
        }
    )
    with MANIFEST.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kentat)
        w.writeheader()
        w.writerows(rivit)


def _cdx_url(page_url: str, vain_200: bool) -> str:
    q = {
        "url": page_url,
        "from": ALKU.strftime("%Y%m%d"),
        "to": LOPPU.strftime("%Y%m%d"),
        "output": "json",
        "collapse": "timestamp:8",
        "limit": "20000",
        "fl": "original,timestamp,statuscode,mimetype,length",
    }
    url = CDX + "?" + urlencode(q)
    if vain_200:
        url += "&filter=statuscode:200"
    return url


def _lue_cdx(polku: Path) -> list[dict[str, str]]:
    if not polku.exists() or polku.stat().st_size == 0:
        return []
    data = json.loads(polku.read_text(encoding="utf-8"))
    if not data:
        return []
    paa = data[0]
    rivit = []
    for r in data[1:]:
        rivit.append({str(paa[i]): str(r[i]) if i < len(r) else "" for i in range(len(paa))})
    return rivit


def hae_cdx(media: str, page_url: str, vain_200: bool) -> Path:
    liite = "200" if vain_200 else "all"
    polku = RAW / f"cdx_{media}_{liite}_{ALKU.year}_{LOPPU.year}.json"
    url = _cdx_url(page_url, vain_200)
    print(f"CDX {media} {liite} ...", flush=True)
    time.sleep(2)
    koodi = _curl(url, polku)
    huom = f"HTTP {koodi}; koko_tavua={polku.stat().st_size if polku.exists() else 0}"
    if koodi != 200:
        huom += "; ei täytetty"
    _kirjaa_manifest(polku.name, "Wayback CDX", url, f"päiväkollapsi {media}", huom)
    if koodi != 200:
        raise RuntimeError(f"CDX {media} {liite} HTTP {koodi}")
    return polku


def hae_rss(media: str, rss_url: str) -> Path:
    polku = RAW / f"rss_{media}_{date.today().isoformat()}.xml"
    print(f"RSS {media} ...", flush=True)
    time.sleep(1)
    koodi = _curl(rss_url, polku)
    n = 0
    if polku.exists():
        n = polku.read_text(encoding="utf-8", errors="replace").count("<item>")
    _kirjaa_manifest(
        polku.name,
        "RSS",
        rss_url,
        f"tuoreet otsikot {media}",
        f"HTTP {koodi}; item={n}; ei historiallinen arkisto",
    )
    return polku


def coverage() -> Path:
    TABLES.mkdir(parents=True, exist_ok=True)
    ruudukko = _paivat(ALKU, LOPPU)
    rivit: list[dict[str, object]] = []
    for m in MEDIT:
        c200 = {r["timestamp"][:8]: r for r in _lue_cdx(RAW / f"cdx_{m['media']}_200_{ALKU.year}_{LOPPU.year}.json")}
        call = {r["timestamp"][:8]: r for r in _lue_cdx(RAW / f"cdx_{m['media']}_all_{ALKU.year}_{LOPPU.year}.json")}
        for d in ruudukko:
            avain = d.strftime("%Y%m%d")
            a = call.get(avain)
            b = c200.get(avain)
            r = b or a
            rivit.append(
                {
                    "media": m["media"],
                    "url": m["url"],
                    "paiva": d.isoformat(),
                    "cdx_statuscode": r["statuscode"] if r else "",
                    "cdx_timestamp": r["timestamp"] if r else "",
                    "cdx_original": r["original"] if r else "",
                    "on_cdx": bool(a),
                    "on_cdx_200": bool(b),
                    "snapshot_url": (
                        f"https://web.archive.org/web/{r['timestamp']}/{r['original']}" if r else ""
                    ),
                }
            )
    df_polku = TABLES / "coverage_media_paiva.csv"
    with df_polku.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rivit[0].keys()))
        w.writeheader()
        w.writerows(rivit)
    yhte = TABLES / "coverage_media_yhteenveto.csv"
    with yhte.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["media", "n_paivaa", "n_cdx", "n_cdx_200", "n_puuttuu_cdx", "n_puuttuu_200"],
        )
        w.writeheader()
        for m in MEDIT:
            osat = [r for r in rivit if r["media"] == m["media"]]
            n = len(osat)
            n_any = sum(1 for r in osat if r["on_cdx"])
            n_200 = sum(1 for r in osat if r["on_cdx_200"])
            w.writerow(
                {
                    "media": m["media"],
                    "n_paivaa": n,
                    "n_cdx": n_any,
                    "n_cdx_200": n_200,
                    "n_puuttuu_cdx": n - n_any,
                    "n_puuttuu_200": n - n_200,
                }
            )
    return df_polku


def hae_kaikki() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    for m in MEDIT:
        hae_cdx(m["media"], m["url"], vain_200=False)
        hae_cdx(m["media"], m["url"], vain_200=True)
        hae_rss(m["media"], m["rss"])
    polku = coverage()
    print("coverage", polku, flush=True)


if __name__ == "__main__":
    hae_kaikki()
