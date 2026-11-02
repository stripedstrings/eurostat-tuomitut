"""Vaihe 3: etusivusnapshotit ja otsikkopoiminta. Ei täyttöä, ei sävykoodausta."""

from __future__ import annotations

import csv
import html as htmlmod
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path

from src.config import ROOT
from src.fetch_media import TABLES, USER_AGENT, _kirjaa_manifest

RAW_SNAP = ROOT / "media" / "data" / "raw" / "snapshots"
COVERAGE = TABLES / "coverage_media_paiva.csv"

# M1-esimerkit MEDIA_README.md:stä; osuma otsikkotekstissä, ei ihmiskoodaus.
ENTITEETTI_AVAIMET = (
    "putin",
    "zelenskyi",
    "zelenskyy",
    "zelenskiy",
    "zelensky",
    "zelenski",
    "tasavallan presidentti",
    "suomen presidentti",
    "maahanmuutto",
    "pakolais",
    "siirtolais",
    "rikollis",
    "rikos",
    "tuomittu",
    "tuomitut",
    "terveysuhka",
    "epidemia",
    "pandemia",
)

def _lue_html(polku: Path) -> str:
    raaka = polku.read_bytes()
    for enc in ("utf-8", "windows-1252", "iso-8859-1"):
        try:
            teksti = raaka.decode(enc)
        except UnicodeDecodeError:
            continue
        if enc == "utf-8" and "\ufffd" in teksti[:8000]:
            continue
        return teksti
    return raaka.decode("utf-8", errors="replace")


OHITA = {
    "pääuutiset",
    "paa uutiset",
    "lisää aiheesta",
    "lisaa aiheesta",
    "suosittelemme",
    "luetuimmat",
    "uusimmat",
    "lue myös nämä",
    "lue myos nama",
    "hakemisto",
    "mainos",
    "yle uutiset",
    "iltalehti.fi",
    "sää tunti tunnilta",
    "saa tunti tunnilta",
}


OTSIKKO_LUOKAT = (
    "otsikko",
    "headline",
    "article-title",
    "front-title",
    "a-title-font",
    "latest-pala-title",
    "big-title",
    "newsticker-title-text",
)


class _Kerailija(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.path: list[tuple[str, str]] = []
        self.bufs: list[list[str]] = []
        self.skip = 0
        self.osat: list[tuple[str, str, str]] = []
        self.figcaptionit: list[str] = []
        self.og_image = ""
        self.doc_title = ""
        self._in_title = False
        self._in_fig = False
        self._fig_buf = ""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: (v or "") for k, v in attrs}
        cls = a.get("class", "")
        if tag in ("script", "style", "noscript", "svg"):
            self.skip += 1
        if tag == "meta":
            prop = (a.get("property") or a.get("name") or "").lower()
            if prop in {"og:image", "twitter:image"} and a.get("content") and not self.og_image:
                self.og_image = a["content"]
        if tag == "title":
            self._in_title = True
        if tag == "figcaption":
            self._in_fig = True
            self._fig_buf = ""
        self.path.append((tag, cls))
        self.bufs.append([])

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style", "noscript", "svg") and self.skip:
            self.skip -= 1
        if tag == "title":
            self._in_title = False
        if tag == "figcaption":
            t = " ".join(self._fig_buf.split())
            if t:
                self.figcaptionit.append(t)
            self._in_fig = False
        if self.path and self.path[-1][0] == tag:
            cls = self.path[-1][1]
            palat = self.bufs.pop() if self.bufs else []
            teksti = " ".join(" ".join(palat).split())
            if teksti and self.skip == 0:
                self.osat.append((tag, cls, teksti))
                if self.bufs:
                    self.bufs[-1].append(teksti)
            self.path.pop()

    def handle_data(self, data: str) -> None:
        if self.skip:
            return
        if self._in_title:
            self.doc_title += data
        if self._in_fig:
            self._fig_buf += data
        if self.bufs:
            self.bufs[-1].append(data)


def _siisti(s: str) -> str:
    s = htmlmod.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _luokka_osuu(cls: str) -> bool:
    """Täysi luokkatokeni, ei osamerkkijono (esim. MinimalHeadlines ≠ headline)."""
    tokenit = cls.lower().split()
    for k in OTSIKKO_LUOKAT:
        for t in tokenit:
            if t == k or t.startswith(k + "-") or t.endswith("-" + k):
                return True
    return False


def _kelpaa(teksti: str) -> bool:
    t = _siisti(teksti)
    if len(t) < 18 or len(t) > 180:
        return False
    low = t.lower()
    if low in OHITA or any(low.startswith(x) for x in ("cookie", "accept", "tilaa")):
        return False
    if low in {x.lower() for x in OHITA}:
        return False
    kirjaimet = sum(c.isalpha() for c in t)
    return kirjaimet >= 10


def poimi_otsikot(html: str) -> tuple[list[str], str, str]:
    p = _Kerailija()
    try:
        p.feed(html)
    except Exception:
        pass
    otsikot: list[str] = []
    nain: set[str] = set()
    for tag, cls, teksti in p.osat:
        t = _siisti(teksti)
        cl = cls.lower()
        if "saa_otsikko" in cl or "list-title" in cl or "vignette" in cl:
            continue
        ehdokas = False
        if _luokka_osuu(cl):
            ehdokas = True
        if tag in {"h1", "h2", "h3"} and _kelpaa(t):
            ehdokas = True
        if ehdokas and _kelpaa(t):
            avain = t.lower()
            if avain not in nain:
                nain.add(avain)
                otsikot.append(t)
    kuva = _siisti(p.og_image)
    kuvateksti = _siisti(p.figcaptionit[0]) if p.figcaptionit else ""
    if kuvateksti.lower() in OHITA or len(kuvateksti) < 8:
        kuvateksti = ""
    return otsikot, kuvateksti, kuva


def entiteetti_osumat(tekstit: list[str]) -> str:
    blob = " ".join(tekstit).lower()
    hit = [k for k in ENTITEETTI_AVAIMET if k in blob]
    return ";".join(hit)


def _curl_snapshot(url: str, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [
            "curl.exe",
            "-sS",
            "-L",
            "--max-redirs",
            "8",
            "-A",
            USER_AGENT.replace("ei massahakua HTML:ään", "etusivusnapshotit otsikoille"),
            "-o",
            str(dest),
            "-w",
            "%{http_code}",
            "--max-time",
            "25",
            url,
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    try:
        return int(proc.stdout.strip() or "0")
    except ValueError:
        return 0


def _snap_polku(media: str, paiva: str) -> Path:
    return RAW_SNAP / media / f"{paiva}.html"


def _lue_coverage() -> list[dict[str, str]]:
    with COVERAGE.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def hae_yksi(rivi: dict[str, str]) -> tuple[str, str, int]:
    media, paiva = rivi["media"], rivi["paiva"]
    dest = _snap_polku(media, paiva)
    if dest.exists() and dest.stat().st_size > 1500:
        return media, paiva, 200
    url = rivi.get("snapshot_url") or ""
    if not url:
        return media, paiva, 0
    koodi = 0
    for yritys in range(2):
        if yritys:
            time.sleep(3)
        koodi = _curl_snapshot(url, dest)
        if koodi == 200 and dest.exists() and dest.stat().st_size >= 500:
            return media, paiva, koodi
        if koodi not in {0, 429, 503}:
            break
    if dest.exists() and dest.stat().st_size < 500:
        dest.unlink()
    return media, paiva, koodi


def hae_snapshotit(
    max_tyot: int = 1,
    vuosi: str | None = None,
    max_uusia: int | None = None,
) -> None:
    rivit = [r for r in _lue_coverage() if (r.get("snapshot_url") or "").strip()]
    if vuosi:
        rivit = [r for r in rivit if r["paiva"].startswith(vuosi)]
    rivit.sort(key=lambda r: (0 if r["paiva"].startswith("2023") else 1, r["paiva"], r["media"]))
    puuttuvat: list[dict[str, str]] = []
    ok = 0
    for r in rivit:
        dest = _snap_polku(r["media"], r["paiva"])
        if dest.exists() and dest.stat().st_size > 1500:
            ok += 1
        else:
            puuttuvat.append(r)
    if max_uusia is not None:
        puuttuvat = puuttuvat[:max_uusia]
    n = len(puuttuvat)
    print(f"snapshotteja jo levyllä {ok}, haetaan {n}", flush=True)

    def tyo(rivi: dict[str, str]) -> tuple[str, str, int]:
        time.sleep(1.5 if max_tyot == 1 else 0.25)
        return hae_yksi(rivi)

    with ThreadPoolExecutor(max_workers=max_tyot) as ex:
        futs = [ex.submit(tyo, r) for r in puuttuvat]
        for i, fut in enumerate(as_completed(futs), 1):
            _m, _p, koodi = fut.result()
            if koodi == 200:
                ok += 1
            if i % 10 == 0 or i == n:
                print(f"  {i}/{n} uutta, HTTP200-tiedostoja {ok} viime_http={koodi}", flush=True)


def rakenna_tietueet() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    coverage = _lue_coverage()
    etusivu_kentat = [
        "media",
        "url",
        "paiva",
        "snapshot_url",
        "http_tiedosto",
        "n_otsikkoa",
        "kuvateksti",
        "kuva_url",
        "entiteetti",
        "aihe",
        "savy",
        "koodaaja",
        "koodikirja_versio",
    ]
    otsikko_kentat = [
        "media",
        "paiva",
        "jarjestys",
        "otsikko",
        "entiteetti",
        "kuvateksti",
        "kuva_url",
        "snapshot_url",
        "aihe",
        "savy",
        "koodaaja",
        "koodikirja_versio",
    ]
    etu_rivit: list[dict[str, str]] = []
    ots_rivit: list[dict[str, str]] = []
    for r in coverage:
        media, paiva = r["media"], r["paiva"]
        dest = _snap_polku(media, paiva)
        pohja = {
            "media": media,
            "url": r.get("url", ""),
            "paiva": paiva,
            "snapshot_url": r.get("snapshot_url", ""),
            "http_tiedosto": "",
            "n_otsikkoa": "",
            "kuvateksti": "",
            "kuva_url": "",
            "entiteetti": "",
            "aihe": "",
            "savy": "",
            "koodaaja": "",
            "koodikirja_versio": "",
        }
        if not dest.exists():
            etu_rivit.append(pohja)
            continue
        html = _lue_html(dest)
        otsikot, kuvateksti, kuva = poimi_otsikot(html)
        ent = entiteetti_osumat(otsikot)
        pohja.update(
            {
                "http_tiedosto": str(dest.stat().st_size),
                "n_otsikkoa": str(len(otsikot)),
                "kuvateksti": kuvateksti,
                "kuva_url": kuva,
                "entiteetti": ent,
                "koodaaja": "kone",
                "koodikirja_versio": "esikasittely-v1",
            }
        )
        etu_rivit.append(pohja)
        for i, ots in enumerate(otsikot, 1):
            ots_rivit.append(
                {
                    "media": media,
                    "paiva": paiva,
                    "jarjestys": str(i),
                    "otsikko": ots,
                    "entiteetti": entiteetti_osumat([ots]),
                    "kuvateksti": kuvateksti if i == 1 else "",
                    "kuva_url": kuva if i == 1 else "",
                    "snapshot_url": r.get("snapshot_url", ""),
                    "aihe": "",
                    "savy": "",
                    "koodaaja": "kone",
                    "koodikirja_versio": "esikasittely-v1",
                }
            )
    with (TABLES / "tietueet_etusivu.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=etusivu_kentat)
        w.writeheader()
        w.writerows(etu_rivit)
    with (TABLES / "tietueet_otsikko.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=otsikko_kentat)
        w.writeheader()
        w.writerows(ots_rivit)
    n_html = sum(1 for _ in RAW_SNAP.glob("*/*.html")) if RAW_SNAP.exists() else 0
    _kirjaa_manifest(
        "snapshots/",
        "Wayback HTML",
        "https://web.archive.org/web/",
        "etusivusnapshotit",
        f"n_tiedosto={n_html}; git-ignorissa; ei täyttöä",
    )
    with (TABLES / "tietueet_yhteenveto.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["media", "n_paivaa", "n_tiedosto", "n_otsikko_paiva", "n_otsikkoa", "n_ilman_otsikkoa"],
        )
        w.writeheader()
        for media in sorted({r["media"] for r in etu_rivit}):
            osat = [r for r in etu_rivit if r["media"] == media]
            tied = [r for r in osat if r["http_tiedosto"]]
            with_o = [r for r in tied if r["n_otsikkoa"] and int(r["n_otsikkoa"]) > 0]
            n_ots = sum(int(r["n_otsikkoa"]) for r in with_o)
            w.writerow(
                {
                    "media": media,
                    "n_paivaa": str(len(osat)),
                    "n_tiedosto": str(len(tied)),
                    "n_otsikko_paiva": str(len(with_o)),
                    "n_otsikkoa": str(n_ots),
                    "n_ilman_otsikkoa": str(len(tied) - len(with_o)),
                }
            )


def aja(
    hae: bool = True,
    max_tyot: int = 1,
    vuosi: str | None = None,
    max_uusia: int | None = None,
) -> None:
    if hae:
        hae_snapshotit(max_tyot=max_tyot, vuosi=vuosi, max_uusia=max_uusia)
    rakenna_tietueet()
    print("kirjoitettu", TABLES / "tietueet_etusivu.csv", flush=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--vain-parse", action="store_true")
    parser.add_argument("--tyot", type=int, default=1)
    parser.add_argument("--vuosi", default=None)
    parser.add_argument("--max-uusia", type=int, default=None)
    args = parser.parse_args()
    aja(
        hae=not args.vain_parse,
        max_tyot=args.tyot,
        vuosi=args.vuosi,
        max_uusia=args.max_uusia,
    )
