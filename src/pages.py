"""GitHub Pages: esirekisteröity raportti etusivulle, tutkivat maasivut erilleen."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

from src.config import DOCS_DIR, FIGURES_DIR, OUTPUT_DIR, ROOT

RAPORTTI_MD = OUTPUT_DIR / "RAPORTTI.md"
RAPORTTI_EN_MD = OUTPUT_DIR / "RAPORTTI_en.md"


def _inline(text: str) -> str:
    parts: list[str] = []
    i = 0
    n = len(text)
    while i < n:
        if text.startswith("**", i):
            j = text.find("**", i + 2)
            if j != -1:
                parts.append("<strong>" + _inline(text[i + 2 : j]) + "</strong>")
                i = j + 2
                continue
        if text[i] == "`":
            j = text.find("`", i + 1)
            if j != -1:
                parts.append("<code>" + html.escape(text[i + 1 : j]) + "</code>")
                i = j + 1
                continue
        if text[i] == "[":
            m = re.match(r"\[([^\]]+)\]\(([^)]+)\)", text[i:])
            if m:
                parts.append(
                    f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>'
                )
                i += m.end()
                continue
        if text.startswith("\\(", i):
            j = text.find("\\)", i + 2)
            if j != -1:
                parts.append("<code>" + html.escape(text[i : j + 2]) + "</code>")
                i = j + 2
                continue
        parts.append(html.escape(text[i]))
        i += 1
    return "".join(parts)


def _kuva(nimi: str) -> str:
    alt = html.escape(nimi)
    return (
        f'<figure><img src="figures/{alt}" alt="{alt}">'
        f"<figcaption>{alt}</figcaption></figure>"
    )


def _kuvat_koodista(text: str) -> str:
    def yksi(m: re.Match[str]) -> str:
        nimi = m.group(1)
        if "*" in nimi:
            pre = nimi.split("*")[0]
            tiedostot = sorted(p.name for p in FIGURES_DIR.glob(nimi) if p.suffix == ".png")
            if not tiedostot:
                tiedostot = sorted(p.name for p in FIGURES_DIR.glob(pre + "*.png"))
            return "\n" + "\n".join(f"@@KUVA:{t}@@" for t in tiedostot) + "\n" if tiedostot else m.group(0)
        if (FIGURES_DIR / nimi).exists():
            return f"\n@@KUVA:{nimi}@@\n"
        return m.group(0)

    return re.sub(r"`figures/([^`]+)`", yksi, text)


def md_html(md: str) -> str:
    md = _kuvat_koodista(md)
    rivit = md.splitlines()
    out: list[str] = []
    i = 0
    while i < len(rivit):
        r = rivit[i]
        if r.startswith("@@KUVA:") and r.endswith("@@"):
            out.append(_kuva(r[7:-2]))
            i += 1
            continue
        if r.strip() == "---":
            out.append("<hr>")
            i += 1
            continue
        if r.startswith("# "):
            out.append("<h1>" + _inline(r[2:]) + "</h1>")
            i += 1
            continue
        if r.startswith("### "):
            out.append("<h3>" + _inline(r[4:]) + "</h3>")
            i += 1
            continue
        if r.startswith("## "):
            out.append("<h2>" + _inline(r[3:]) + "</h2>")
            i += 1
            continue
        if r.startswith("|"):
            taulu = []
            while i < len(rivit) and rivit[i].startswith("|"):
                taulu.append(rivit[i])
                i += 1
            out.append(_taulu(taulu))
            continue
        if r.startswith("- "):
            out.append("<ul>")
            while i < len(rivit) and rivit[i].startswith("- "):
                out.append("<li>" + _inline(rivit[i][2:]) + "</li>")
                i += 1
            out.append("</ul>")
            continue
        if r.startswith(("1. ", "2. ", "3. ")):
            out.append("<ol>")
            while i < len(rivit) and re.match(r"\d+\. ", rivit[i]):
                out.append("<li>" + _inline(re.sub(r"^\d+\. ", "", rivit[i])) + "</li>")
                i += 1
            out.append("</ol>")
            continue
        if r.strip() == "":
            i += 1
            continue
        kappale = [r]
        i += 1
        while i < len(rivit) and rivit[i].strip() and not rivit[i].startswith(
            ("#", "|", "- ", "---", "@@KUVA:")
        ) and not re.match(r"\d+\. ", rivit[i]):
            kappale.append(rivit[i])
            i += 1
        teksti = "<br>\n".join(_inline(x) for x in kappale).strip()
        if teksti in (".", ""):
            continue
        teksti = re.sub(r"@@KUVA:([^@]+)@@", lambda m: _kuva(m.group(1)), teksti)
        teksti = re.sub(r"(?:Kaaviot?|Small multiples):\s*$", "", teksti).rstrip(" :")
        if teksti:
            out.append("<p>" + teksti + "</p>")
    html_out = "\n".join(out)
    return re.sub(r"@@KUVA:([^@]+)@@", lambda m: _kuva(m.group(1)), html_out)


def _taulu(rivit: list[str]) -> str:
    def solut(rivi: str) -> list[str]:
        osat = [s.strip() for s in rivi.strip().strip("|").split("|")]
        return osat

    data = [solut(r) for r in rivit]
    if len(data) >= 2 and all(re.fullmatch(r":?-{2,}:?", c or "") for c in data[1]):
        paa, runko = data[0], data[2:]
    else:
        paa, runko = data[0], data[1:]
    html_osat = ['<div class="taulu-wrap"><table>', "<thead><tr>"]
    for h in paa:
        html_osat.append("<th>" + _inline(h) + "</th>")
    html_osat.append("</tr></thead><tbody>")
    for r in runko:
        html_osat.append("<tr>")
        for s in r:
            html_osat.append("<td>" + _inline(s) + "</td>")
        html_osat.append("</tr>")
    html_osat.append("</tbody></table></div>")
    return "".join(html_osat)


def _sivu_html(sisalto_fi: str, sisalto_en: str) -> str:
    from src.site import LIPUT, _valikko, aihe_nav

    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title data-i18n="raportti_title">Tuomitut kansalaisuuden mukaan, EU-27, 2008–2024</title>
  <link rel="stylesheet" href="tyyli.css">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {aihe_nav(juuri=True, aktiivinen="maahanmuutto")}
      <div class="yla">
        <p class="kicker"><a href="index.html" data-i18n="raportti_kicker"></a></p>
        {LIPUT}
      </div>
      <h1 data-i18n="raportti_h1">Tuomitut kansalaisuuden mukaan, EU-27</h1>
      <p class="lead" data-i18n="raportti_lead"></p>
      <div class="valitsin">{_valikko("RAPORTTI", True)}</div>
      <p class="navi"><a href="lahteet.html">Lähteet</a></p>
    </div>
  </header>
  <main class="wrap">
    <div class="kieli-fi">
{sisalto_fi}
    </div>
    <div class="kieli-en" hidden>
{sisalto_en}
    </div>
    <p class="alaviite" data-i18n="raportti_alaviite"></p>
  </main>
  <script src="sivu.js"></script>
</body>
</html>
"""


def korjaa_valikot() -> None:
    """Suomi ei ole etusivu; valikkoon Raportti."""
    opt_maat = (
        '<option value="../index.html" data-fi="Raportti" data-en="Report">Raportti</option>\n'
    )
    opt_juuri = (
        '<option value="index.html" data-fi="Raportti" data-en="Report">Raportti</option>\n'
    )
    alku = '<select id="maa" onchange="location.href=this.value">\n'
    for p in (DOCS_DIR / "maat").glob("*.html"):
        t = p.read_text(encoding="utf-8")
        t = t.replace(
            '<option value="../index.html" data-fi="Suomi" data-en="Finland"',
            '<option value="fi.html" data-fi="Suomi" data-en="Finland"',
        )
        if 'data-fi="Raportti"' not in t:
            t = t.replace(alku, alku + opt_maat, 1)
        p.write_text(t, encoding="utf-8")
    vert = DOCS_DIR / "vertailu.html"
    if vert.exists():
        t = vert.read_text(encoding="utf-8")
        t = t.replace(
            '<option value="index.html" data-fi="Suomi" data-en="Finland"',
            '<option value="maat/fi.html" data-fi="Suomi" data-en="Finland"',
        )
        if 'data-fi="Raportti"' not in t:
            t = t.replace(alku, alku + opt_juuri, 1)
        vert.write_text(t, encoding="utf-8")


def lisaa_aihe_palkki() -> None:
    from src.site import aihe_nav

    merkit = [
        (DOCS_DIR / "vertailu.html", aihe_nav(juuri=True, aktiivinen="maahanmuutto")),
    ]
    nav_maat = aihe_nav(juuri=False, aktiivinen="maahanmuutto")
    for p in (DOCS_DIR / "maat").glob("*.html"):
        merkit.append((p, nav_maat))
    ankkuri = '    <div class="wrap">\n'
    for p, nav in merkit:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        if 'class="aiheet"' in t:
            continue
        t = t.replace(ankkuri, ankkuri + "      " + nav, 1)
        p.write_text(t, encoding="utf-8")


def _kehys(otsikko: str, aktiivinen: str, juuri: bool, media_sivu: bool, css: str, js: str, sisalto: str) -> str:
    from src.site import LIPUT, aihe_nav

    return f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{otsikko}</title>
  <link rel="stylesheet" href="{css}">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {aihe_nav(juuri=juuri, aktiivinen=aktiivinen, media_sivu=media_sivu)}
      <div class="yla">
        <p class="kicker"><a href="{'../index.html' if media_sivu else 'index.html'}" data-i18n="raportti_kicker"></a></p>
        {LIPUT}
      </div>
    </div>
  </header>
  <main class="wrap">
{sisalto}
  </main>
  <script src="{js}"></script>
</body>
</html>
"""


def kirjoita_aihesivut() -> None:
    (DOCS_DIR / "media").mkdir(parents=True, exist_ok=True)
    for nimi in (
        "MEDIA_README.md",
        "MEDIA_PREREGISTRATION.md",
        "MEDIA_DATA_SOURCES.md",
        "MEDIA_METHODS.md",
        "MEDIA_CURSOR_TASKS.md",
        "DATA_SOURCES.md",
    ):
        src = ROOT / nimi
        if src.exists():
            kohde = DOCS_DIR / "media" / nimi if nimi.startswith("MEDIA") else DOCS_DIR / nimi
            shutil.copy2(src, kohde)
    for csv_polku in (ROOT / "media" / "output" / "tables").glob("*.csv"):
        shutil.copy2(csv_polku, DOCS_DIR / "media" / csv_polku.name)

    lahteet = """
    <div class="kieli-fi">
      <h1>Viralliset lähteet (maahanmuutto / K1)</h1>
      <p>Koodit on luettu Eurostat SDMX-CSV:stä 2026-11-01. Koodeja ei ole keksitty. Täysi lista: <a href="DATA_SOURCES.md">DATA_SOURCES.md</a>.</p>
      <p><a href="index.html">K1-raportti</a></p>
      <div class="taulu-wrap"><table>
        <thead><tr><th>Koodi</th><th>Sisältö</th><th>Tila</th></tr></thead>
        <tbody>
          <tr><td><a href="https://doi.org/10.2908/crim_just_ctz">crim_just_ctz</a></td><td>epäillyt ja tuomitut kansalaisuuden mukaan</td><td>haettu 2026-11-01</td></tr>
          <tr><td><a href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop5ctz/default/table?lang=en">migr_pop5ctz</a></td><td>väestö kansalaisuuden ja syntymämaan ryhmän mukaan</td><td>haettu 2026-11-01</td></tr>
          <tr><td><a href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table?lang=en">migr_pop1ctz</a></td><td>väestö ikä × sukupuoli × kansalaisuus</td><td>haettu 2026-11-01</td></tr>
          <tr><td><a href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop3ctb/default/table?lang=en">migr_pop3ctb</a></td><td>väestö ikä × sukupuoli × syntymämaa</td><td>haettu 2026-11-01</td></tr>
          <tr><td>lfsa_ergan, lfsa_urgan, edat_lfs_9911</td><td>K2 työllisyys, työttömyys, koulutus</td><td>haettu 2026-11-01</td></tr>
          <tr><td>migr_resfirst, migr_resvalid</td><td>K2 oleskeluluvat</td><td>haettu 2026-11-01</td></tr>
          <tr><td>DST STRFNA13, StatFin 15hh</td><td>kansalliset lukumäärät (ei EU-aggregaatti)</td><td>haettu 2026-11-01</td></tr>
          <tr><td>Brå</td><td>Ruotsi</td><td>CSV puuttuu</td></tr>
        </tbody>
      </table></div>
    </div>
    <div class="kieli-en" hidden>
      <h1>Official sources (immigration / K1)</h1>
      <p>Codes were read from Eurostat SDMX-CSV on 2026-11-01. Codes were not invented. Full list: <a href="DATA_SOURCES.md">DATA_SOURCES.md</a>.</p>
      <p><a href="index.html">K1 report</a></p>
      <div class="taulu-wrap"><table>
        <thead><tr><th>Code</th><th>Content</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td><a href="https://doi.org/10.2908/crim_just_ctz">crim_just_ctz</a></td><td>suspects and convicted persons by citizenship</td><td>retrieved 2026-11-01</td></tr>
          <tr><td><a href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop5ctz/default/table?lang=en">migr_pop5ctz</a></td><td>population by citizenship and country-of-birth group</td><td>retrieved 2026-11-01</td></tr>
          <tr><td><a href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop1ctz/default/table?lang=en">migr_pop1ctz</a></td><td>population by age × sex × citizenship</td><td>retrieved 2026-11-01</td></tr>
          <tr><td><a href="https://ec.europa.eu/eurostat/databrowser/view/migr_pop3ctb/default/table?lang=en">migr_pop3ctb</a></td><td>population by age × sex × country of birth</td><td>retrieved 2026-11-01</td></tr>
          <tr><td>lfsa_ergan, lfsa_urgan, edat_lfs_9911</td><td>K2 employment, unemployment, education</td><td>retrieved 2026-11-01</td></tr>
          <tr><td>migr_resfirst, migr_resvalid</td><td>K2 residence permits</td><td>retrieved 2026-11-01</td></tr>
          <tr><td>DST STRFNA13, StatFin 15hh</td><td>national counts (not in EU aggregate)</td><td>retrieved 2026-11-01</td></tr>
          <tr><td>Brå</td><td>Sweden</td><td>CSV missing</td></tr>
        </tbody>
      </table></div>
    </div>
    <p class="alaviite"><a href="index.html">K1</a> · <a href="media/index.html">Media</a></p>
"""
    (DOCS_DIR / "lahteet.html").write_text(
        _kehys(
            "Lähteet — maahanmuutto",
            "maahanmuutto",
            True,
            False,
            "tyyli.css",
            "sivu.js",
            lahteet,
        ),
        encoding="utf-8",
    )

    peitto_fi = ""
    peitto_en = ""
    yht = ROOT / "media" / "output" / "tables" / "coverage_media_yhteenveto.csv"
    if yht.exists():
        import csv as _csv

        with yht.open(encoding="utf-8", newline="") as f:
            rivit = list(_csv.DictReader(f))
        solut = "".join(
            "<tr>"
            + "".join(f"<td>{html.escape(str(r[k]))}</td>" for k in rivit[0].keys())
            + "</tr>"
            for r in rivit
        )
        paa = "".join(f"<th>{html.escape(k)}</th>" for k in rivit[0].keys())
        taulu = f'<div class="taulu-wrap"><table><thead><tr>{paa}</tr></thead><tbody>{solut}</tbody></table></div>'
        peitto_fi = (
            "<h2>Peitto (vaihe 2, CDX, 2015–2025)</h2>"
            "<p>Kalenteriruudukko, puuttuva päivä tyhjä. Ei HTML-otsikoita. "
            '<a href="coverage_media_yhteenveto.csv">yhteenveto</a>, '
            '<a href="coverage_media_paiva.csv">päivittäin</a>.</p>'
            + taulu
        )
        peitto_en = (
            "<h2>Coverage (phase 2, CDX, 2015–2025)</h2>"
            "<p>Full calendar; missing days left empty. No HTML headlines. "
            '<a href="coverage_media_yhteenveto.csv">summary</a>, '
            '<a href="coverage_media_paiva.csv">by day</a>.</p>'
            + taulu
        )

    media = f"""
    <div class="kieli-fi">
      <h1>Media</h1>
      <p><strong>Analyysiä ei ole ajettu.</strong> Esirekisteröinti: 2026-11-01. Vaihe 2: CDX-indeksi haettu 2026-11-02. Otsikot = vaihe 3.</p>
      <p>Kysymykset M1–M5 (näkyvyys, suhteutus tapahtumiin, sävy, media vs. tilasto, vertailu). M4 ei ennen vaihetta 7. H3 ilman julkaisijan analytiikkaa = ei testattavissa.</p>
      <ul>
        <li><a href="MEDIA_PREREGISTRATION.md">MEDIA_PREREGISTRATION.md</a></li>
        <li><a href="MEDIA_README.md">MEDIA_README.md</a></li>
        <li><a href="MEDIA_DATA_SOURCES.md">MEDIA_DATA_SOURCES.md</a></li>
        <li><a href="MEDIA_METHODS.md">MEDIA_METHODS.md</a></li>
      </ul>
      <h2>Lähteet (vaihe 1, 2026-11-01)</h2>
      <p>Pieni näyte. Ei koko-arkistoa. Tiedot: <a href="MEDIA_DATA_SOURCES.md">MEDIA_DATA_SOURCES.md</a>.</p>
      <div class="taulu-wrap"><table>
        <thead><tr><th>Ehdokas</th><th>Käyttö</th><th>Tila</th></tr></thead>
        <tbody>
          <tr><td>Wayback Machine CDX</td><td>etusivuindeksi</td><td>saatavilla (HTTP 200; yksi 503)</td></tr>
          <tr><td>Yle API</td><td>artikkelit</td><td>ei julkista artikkeli-API:a; teksti-TV</td></tr>
          <tr><td>GDELT DOC 2.0</td><td>uutisvirta</td><td>HTTP 429; ei JSON-otosta</td></tr>
          <tr><td>Media Cloud</td><td>mediavertailu</td><td>api.mediacloud.org ei DNS; ei JSON-hakua</td></tr>
          <tr><td>RSS (Yle, IL)</td><td>tuoreet otsikot</td><td>saatavilla; ei historiaa</td></tr>
        </tbody>
      </table></div>
      {peitto_fi}
    </div>
    <div class="kieli-en" hidden>
      <h1>Media</h1>
      <p><strong>No analysis has been run.</strong> Preregistration: 2026-11-01. Phase 2: CDX index retrieved 2026-11-02. Headlines = phase 3.</p>
      <p>Questions M1–M5 (visibility, alignment with events, tone, media vs statistics, comparison). M4 not before phase 7. H3 without publisher analytics = not testable.</p>
      <ul>
        <li><a href="MEDIA_PREREGISTRATION.md">MEDIA_PREREGISTRATION.md</a></li>
        <li><a href="MEDIA_README.md">MEDIA_README.md</a></li>
        <li><a href="MEDIA_DATA_SOURCES.md">MEDIA_DATA_SOURCES.md</a></li>
        <li><a href="MEDIA_METHODS.md">MEDIA_METHODS.md</a></li>
      </ul>
      <h2>Sources (phase 1, 2026-11-01)</h2>
      <p>Small sample. No full archive. Details: <a href="MEDIA_DATA_SOURCES.md">MEDIA_DATA_SOURCES.md</a>.</p>
      <div class="taulu-wrap"><table>
        <thead><tr><th>Candidate</th><th>Use</th><th>Status</th></tr></thead>
        <tbody>
          <tr><td>Wayback Machine CDX</td><td>front-page index</td><td>available (HTTP 200; one 503)</td></tr>
          <tr><td>Yle API</td><td>articles</td><td>no public article API; teletext only</td></tr>
          <tr><td>GDELT DOC 2.0</td><td>news stream</td><td>HTTP 429; no JSON sample</td></tr>
          <tr><td>Media Cloud</td><td>outlet comparison</td><td>api.mediacloud.org no DNS; no JSON search</td></tr>
          <tr><td>RSS (Yle, IL)</td><td>recent headlines</td><td>available; not a historical archive</td></tr>
        </tbody>
      </table></div>
      {peitto_en}
    </div>
"""
    (DOCS_DIR / "media" / "index.html").write_text(
        _kehys(
            "Media",
            "media",
            True,
            True,
            "../tyyli.css",
            "../sivu.js",
            media,
        ),
        encoding="utf-8",
    )


def kirjoita() -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    kohde = DOCS_DIR / "figures"
    kohde.mkdir(exist_ok=True)
    for png in FIGURES_DIR.glob("*.png"):
        shutil.copy2(png, kohde / png.name)
    shutil.copy2(RAPORTTI_MD, DOCS_DIR / "RAPORTTI.md")
    shutil.copy2(RAPORTTI_EN_MD, DOCS_DIR / "RAPORTTI_en.md")
    (DOCS_DIR / ".nojekyll").write_text("", encoding="utf-8")
    sisalto_fi = md_html(RAPORTTI_MD.read_text(encoding="utf-8"))
    sisalto_en = md_html(RAPORTTI_EN_MD.read_text(encoding="utf-8"))
    (DOCS_DIR / "index.html").write_text(
        _sivu_html(sisalto_fi, sisalto_en), encoding="utf-8"
    )
    korjaa_valikot()
    lisaa_aihe_palkki()
    kirjoita_aihesivut()


if __name__ == "__main__":
    kirjoita()
    print("kirjoitettu", DOCS_DIR / "index.html")
