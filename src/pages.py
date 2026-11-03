"""GitHub Pages: esirekisteröity raportti etusivulle, tutkivat maasivut erilleen."""

from __future__ import annotations

import csv
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
        if (FIGURES_DIR / nimi).exists() or (
            ROOT / "media" / "output" / "figures" / nimi
        ).exists():
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
    from src.site import LIPUT, _valikko, aihe_nav, ristiviittaukset

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
      {aihe_nav(sijainti="juuri", aktiivinen="maahanmuutto")}
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
    {ristiviittaukset(aktiivinen="maahanmuutto", sijainti="juuri")}
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
    import re

    from src.site import aihe_nav

    merkit = [
        (DOCS_DIR / "vertailu.html", aihe_nav(sijainti="juuri", aktiivinen="maahanmuutto")),
    ]
    nav_maat = aihe_nav(sijainti="maat", aktiivinen="maahanmuutto")
    for p in (DOCS_DIR / "maat").glob("*.html"):
        merkit.append((p, nav_maat))
    ankkuri = '    <div class="wrap">\n'
    nav_re = re.compile(r'<nav class="aiheet"[^>]*>.*?</nav>\s*', re.DOTALL)
    for p, nav in merkit:
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        if nav_re.search(t):
            t = nav_re.sub(nav, t, count=1)
        else:
            t = t.replace(ankkuri, ankkuri + "      " + nav, 1)
        p.write_text(t, encoding="utf-8")


def _kehys(
    otsikko: str,
    aktiivinen: str,
    juuri: bool,
    media_sivu: bool,
    css: str,
    js: str,
    sisalto: str,
    *,
    sijainti: str | None = None,
    ristiviittaus: str = "",
) -> str:
    from src.site import LIPUT, aihe_nav

    if sijainti is None:
        sijainti = "media" if media_sivu else ("juuri" if juuri else "maat")
    kicker = "../index.html" if sijainti in ("media", "maat", "tutkimus", "fi_migr") else "index.html"

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
      {aihe_nav(sijainti=sijainti, aktiivinen=aktiivinen)}
      <div class="yla">
        <p class="kicker"><a href="{kicker}" data-i18n="raportti_kicker"></a></p>
        {LIPUT}
      </div>
    </div>
  </header>
  <main class="wrap">
{sisalto}
{ristiviittaus}
  </main>
  <script src="{js}"></script>
</body>
</html>
"""


def _media_taulu_osio(
    polku: Path,
    otsikko_fi: str,
    teksti_fi: str,
    otsikko_en: str,
    teksti_en: str,
) -> tuple[str, str]:
    if not polku.exists():
        return "", ""
    with polku.open(encoding="utf-8", newline="") as f:
        rivit = list(csv.DictReader(f))
    if not rivit:
        return "", ""
    avaimet = list(rivit[0].keys())
    solut = "".join(
        "<tr>"
        + "".join(f"<td>{html.escape(str(r[k]))}</td>" for k in avaimet)
        + "</tr>"
        for r in rivit
    )
    paa = "".join(f"<th>{html.escape(k)}</th>" for k in avaimet)
    taulu = (
        f'<div class="taulu-wrap"><table><thead><tr>{paa}</tr></thead>'
        f"<tbody>{solut}</tbody></table></div>"
    )
    return (
        f"<h2>{html.escape(otsikko_fi)}</h2><p>{teksti_fi}</p>{taulu}",
        f"<h2>{html.escape(otsikko_en)}</h2><p>{teksti_en}</p>{taulu}",
    )


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
    kuvat = DOCS_DIR / "media" / "figures"
    kuvat.mkdir(parents=True, exist_ok=True)
    for png in (ROOT / "media" / "output" / "figures").glob("*.png"):
        shutil.copy2(png, kuvat / png.name)
    for koodikirja_nimi in (
        "codebook_esikasittely_v1.md",
        "codebook_koodaus_v1.md",
        "codebook_m4_v1.md",
        "codebook_uhkakehys_v1.md",
    ):
        koodikirja = ROOT / "media" / koodikirja_nimi
        if koodikirja.exists():
            shutil.copy2(koodikirja, DOCS_DIR / "media" / koodikirja.name)

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

    peitto_fi, peitto_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "coverage_media_yhteenveto.csv",
        "Peitto (vaihe 2, CDX, 2015–2025)",
        "Kalenteriruudukko, puuttuva päivä tyhjä. "
        '<a href="coverage_media_yhteenveto.csv">yhteenveto</a>, '
        '<a href="coverage_media_vuosi.csv">media×vuosi (TUTKIVA)</a>, '
        '<a href="coverage_media_paiva.csv">päivittäin</a>.',
        "Coverage (phase 2, CDX, 2015–2025)",
        "Full calendar; missing days left empty. "
        '<a href="coverage_media_yhteenveto.csv">summary</a>, '
        '<a href="coverage_media_vuosi.csv">media×year (EXPLORATORY)</a>, '
        '<a href="coverage_media_paiva.csv">by day</a>.',
    )
    kood_fi, kood_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "koodaus_yhteenveto.csv",
        "Koodaus (vaihe 4, 2026-11-03)",
        "Otos 500, siemen 20261103. Ihmiskoodit tyhjiä. Sääntö-α/F1 = "
        "TUTKIVA (ei esirekisteröity). "
        '<a href="koodaus_yhteenveto.csv">yhteenveto</a>, '
        '<a href="koodaus_otos.csv">otos</a>, '
        '<a href="koodaus_f1.csv">F1</a>, '
        '<a href="codebook_koodaus_v1.md">koodikirja</a>.',
        "Coding (phase 4, 2026-11-03)",
        "Sample of 500, seed 20261103. Human codes empty. Rule α/F1 = "
        "EXPLORATORY (not preregistered). "
        '<a href="koodaus_yhteenveto.csv">summary</a>, '
        '<a href="koodaus_otos.csv">sample</a>, '
        '<a href="koodaus_f1.csv">F1</a>, '
        '<a href="codebook_koodaus_v1.md">codebook</a>.',
    )
    p1h_fi, p1h_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "p1_entiteetti_osuus_havaittu.csv",
        "P1 entiteettiosuudet (havaittu HTML)",
        "Wilson 95 %. Nimittäjä ≠ kalenteripäivät. "
        '<a href="p1_entiteetti_osuus_havaittu.csv">havaittu</a>, '
        '<a href="p1_entiteetti_osuus.csv">myös vuosittain</a>.',
        "P1 entity shares (observed HTML)",
        "Wilson 95%. Denominator ≠ calendar days. "
        '<a href="p1_entiteetti_osuus_havaittu.csv">observed</a>, '
        '<a href="p1_entiteetti_osuus.csv">by year too</a>.',
    )
    h_fi, h_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "h1_h7.csv",
        "H1–H7",
        "Ei testattavat merkitty. "
        '<a href="h1_h7.csv">taulu</a>, '
        '<a href="p3_p5_tila.csv">P3/P5</a>, '
        '<a href="h7_entropia_tutkiva.csv">H7 TUTKIVA</a>, '
        '<a href="p2_aihe_otos.csv">P2 TUTKIVA</a>.',
        "H1–H7",
        "Untestable hypotheses marked. "
        '<a href="h1_h7.csv">table</a>, '
        '<a href="p3_p5_tila.csv">P3/P5</a>, '
        '<a href="h7_entropia_tutkiva.csv">H7 EXPLORATORY</a>, '
        '<a href="p2_aihe_otos.csv">P2 EXPLORATORY</a>.',
    )
    p4t_fi, p4t_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "p4_mediavertailu.csv",
        "P4 mediavertailu",
        "Pearson-r kuuden entiteettiosuuden välillä (kaksi mediaa).",
        "P4 outlet comparison",
        "Pearson r across six entity shares (two outlets).",
    )
    s_fi, s_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "herkkyys_media_yhteenveto.csv",
        "Herkkyys S1–S7 (vaihe 6)",
        "Pää = P1 otsikko, havaittu jakso. Taulukko: pää vs. kukin S. "
        '<a href="herkkyys_media_yhteenveto.csv">yhteenveto</a>, '
        '<a href="herkkyys_media_S1_S7.csv">kaikki rivit</a>.',
        "Sensitivity S1–S7 (phase 6)",
        "Main = P1 headline, observed period. Table: main vs each S. "
        '<a href="herkkyys_media_yhteenveto.csv">summary</a>, '
        '<a href="herkkyys_media_S1_S7.csv">all rows</a>.',
    )
    m4_fi, m4_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "m4_media_vs_k1.csv",
        "M4 media vs. K1 (vaihe 7)",
        "Suomi (FI) tuomitut vs. rikosotsikon NAT/FOR-avaimet. Yksiköt eivät täsmää. "
        "Ei syy-yhteyttä. Erilliset haarat: "
        '<a href="../index.html">K1</a>, '
        '<a href="../maahanmuutto-fi/index.html">FI-paneeli</a>. '
        '<a href="m4_media_vs_k1.csv">taulu</a>, '
        '<a href="m4_varoitukset.csv">varoitukset</a>, '
        '<a href="codebook_m4_v1.md">koodikirja</a>.',
        "M4 media vs K1 (phase 7)",
        "Finland (FI) convictions vs NAT/FOR strings in crime headlines. Units differ. "
        "No causal claim. Separate branches: "
        '<a href="../index.html">K1</a>, '
        '<a href="../maahanmuutto-fi/index.html">FI panel</a>. '
        '<a href="m4_media_vs_k1.csv">table</a>, '
        '<a href="m4_varoitukset.csv">warnings</a>, '
        '<a href="codebook_m4_v1.md">codebook</a>.',
    )
    uhk_fi, uhk_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "uhkakehys_osuus.csv",
        "TUTKIVA terveysuhka ja uhkakehys",
        "Ei esirekisteröity. Ei korvaa H4:ää. Kaksi kenttää: terveysuhka (aihe) ja "
        "uhkakehys (kärjistys). Wilson 95 %. "
        '<a href="uhkakehys_osuus.csv">osuudet</a>, '
        '<a href="uhkakehys_otsikko.csv">otsikkoliput</a>, '
        '<a href="codebook_uhkakehys_v1.md">koodikirja</a>.',
        "EXPLORATORY health topic and threat frame",
        "Not preregistered. Does not replace H4. Two fields: health-threat topic "
        "and threat frame. Wilson 95%. "
        '<a href="uhkakehys_osuus.csv">shares</a>, '
        '<a href="uhkakehys_otsikko.csv">headline flags</a>, '
        '<a href="codebook_uhkakehys_v1.md">codebook</a>.',
    )
    ana_fi = p1h_fi + h_fi + p4t_fi + s_fi + m4_fi + uhk_fi
    ana_en = p1h_en + h_en + p4t_en + s_en + m4_en + uhk_en
    kuvat_fi = ""
    kuvat_en = ""
    if (ROOT / "media" / "output" / "figures" / "01_entiteetti_osuus.png").exists():
        kuvat_fi = """
      <h2>Kaaviot (vaihe 5)</h2>
      <figure><img src="figures/01_entiteetti_osuus.png" alt="P1 entiteettiosuudet"><figcaption>P1: entiteettiosuudet, Wilson 95 %.</figcaption></figure>
      <figure><img src="figures/02_entiteetti_vuosi.png" alt="P1 vuosittain"><figcaption>P1: osuudet vuosittain. Katkos = ei HTML:ää.</figcaption></figure>
      <figure><img src="figures/03_h1_h2.png" alt="H1 ja H2"><figcaption>H1 Iltalehti 2023 Putin; H2 presidentti, Putin, Zelenskyi.</figcaption></figure>
      <figure><img src="figures/04_m4_media_vs_k1.png" alt="M4"><figcaption>M4: K1 FI vs. rikosotsikon kansalaisuusmaininta. Yksiköt eivät täsmää.</figcaption></figure>
      <figure><img src="figures/05_uhkakehys.png" alt="TUTKIVA uhkakehys"><figcaption>TUTKIVA: terveysuhka ja uhkakehys (tiivis asteikko). Ei H4.</figcaption></figure>
      <figure><img src="figures/06_entiteetti_vuosi.png" alt="Entiteetit vuodittain"><figcaption>TUTKIVA: entiteettiosuudet vuodittain (vain vuodet joilla n&gt;0), Wilson 95 %.</figcaption></figure>
      <figure><img src="figures/07_uhkakehys_vuosi.png" alt="Uhkakehys vuodittain"><figcaption>TUTKIVA: terveysuhka ja uhkakehys vuodittain.</figcaption></figure>
      <figure><img src="figures/08_uhkakehys_kuukausi.png" alt="Uhkakehys kuukausittain"><figcaption>TUTKIVA: kuukausittain; puuttuvaa ei täytetä nollaksi.</figcaption></figure>
"""
        kuvat_en = """
      <h2>Figures (phase 5)</h2>
      <figure><img src="figures/01_entiteetti_osuus.png" alt="P1 entity shares"><figcaption>P1: entity shares, Wilson 95%.</figcaption></figure>
      <figure><img src="figures/02_entiteetti_vuosi.png" alt="P1 by year"><figcaption>P1: shares by year. Gap = no HTML.</figcaption></figure>
      <figure><img src="figures/03_h1_h2.png" alt="H1 and H2"><figcaption>H1 Iltalehti 2023 Putin; H2 president, Putin, Zelenskyi.</figcaption></figure>
      <figure><img src="figures/04_m4_media_vs_k1.png" alt="M4"><figcaption>M4: K1 FI vs citizenship strings in crime headlines. Units differ.</figcaption></figure>
      <figure><img src="figures/05_uhkakehys.png" alt="EXPLORATORY threat frame"><figcaption>EXPLORATORY: health-threat and threat frame (tight scale). Not H4.</figcaption></figure>
      <figure><img src="figures/06_entiteetti_vuosi.png" alt="Entities by year"><figcaption>EXPLORATORY: entity shares by year (years with n&gt;0 only), Wilson 95%.</figcaption></figure>
      <figure><img src="figures/07_uhkakehys_vuosi.png" alt="Threat frame by year"><figcaption>EXPLORATORY: health-threat and threat frame by year.</figcaption></figure>
      <figure><img src="figures/08_uhkakehys_kuukausi.png" alt="Threat frame by month"><figcaption>EXPLORATORY: by month; missing months not filled with zero.</figcaption></figure>
"""
    tulk_fi = """
      <h2>Tulkinta ja rajat</h2>
      <p>Luvut ovat osuuksia havaituissa Wayback-snapshotissa, eivät kaikkien kalenteripäivien osuuksia. Puuttuvaa HTML:ää ei ole täytetty nollaksi. Entiteetti on merkkijono-osuma, ei ihmiskoodaus. H3, H4, H6, H7 (pää), P2 (pää), P3 ja P5 on merkitty ei testattaviksi. M4 vertaa eri yksiköitä (tuomio vs. otsikko); se ei osoita vinoumaa eikä syytä. TUTKIVA uhkakehys ei ole validoitu H4. Pearson-r perustuu kahteen mediaan. Ei motiiveja, ei lukijavaikutusta, ei propaganda-väitettä.</p>
"""
    tulk_en = """
      <h2>Interpretation and limits</h2>
      <p>Shares are among observed Wayback snapshots, not among all calendar days. Missing HTML is not filled with zero. Entity flags are string matches, not human codes. H3, H4, H6, H7 (main), P2 (main), P3 and P5 are not testable. M4 compares different units (conviction vs headline); it does not show bias or cause. The exploratory threat-frame flags are not validated H4. Pearson r uses two outlets. No motives, audience effects, or propaganda claims.</p>
"""
    esik_fi, esik_en = _media_taulu_osio(
        ROOT / "media" / "output" / "tables" / "tietueet_yhteenveto.csv",
        "Esikäsittely (vaihe 3, 2026-11-02)",
        "Otsikot Wayback-HTML:stä. Puuttuva snapshot = tyhjä rivi, ei täyttöä. "
        "Koko ruudukon aihe ja sävy tyhjiä. "
        '<a href="tietueet_yhteenveto.csv">yhteenveto</a>, '
        '<a href="tietueet_etusivu.csv">etusivu</a>, '
        '<a href="tietueet_otsikko.csv">otsikot</a>, '
        '<a href="codebook_esikasittely_v1.md">koodikirja</a>.',
        "Preprocessing (phase 3, 2026-11-02)",
        "Headlines from Wayback HTML. Missing snapshot = empty row, no fill. "
        "Topic and tone empty on the full grid. "
        '<a href="tietueet_yhteenveto.csv">summary</a>, '
        '<a href="tietueet_etusivu.csv">front page</a>, '
        '<a href="tietueet_otsikko.csv">headlines</a>, '
        '<a href="codebook_esikasittely_v1.md">codebook</a>.',
    )

    media = f"""
    <div class="kieli-fi">
      <h1>Media</h1>
      <p><strong>Vaiheet 5–7 ajettu 2026-11-03.</strong> Esirekisteröinti: 2026-11-01. P1 Wilson. S1–S7. M4: FI-tuomitut vs. rikosotsikon kansalaisuusmaininta (yksiköt eivät täsmää). Vaihe 8 = raportti.</p>
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
      {esik_fi}
      {kood_fi}
      {ana_fi}
      {kuvat_fi}
      {tulk_fi}
    </div>
    <div class="kieli-en" hidden>
      <h1>Media</h1>
      <p><strong>Phases 5–7 run 2026-11-03.</strong> Preregistration: 2026-11-01. P1 Wilson. S1–S7. M4: FI convictions vs citizenship strings in crime headlines (units differ). Phase 8 = report.</p>
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
      {esik_en}
      {kood_en}
      {ana_en}
      {kuvat_en}
      {tulk_en}
    </div>
"""
    rap_media = ROOT / "media" / "output" / "RAPORTTI_MEDIA.md"
    if rap_media.exists():
        shutil.copy2(rap_media, DOCS_DIR / "media" / "RAPORTTI_MEDIA.md")
        m4_huom = """
    <aside class="kortti" id="m4-ristiviittaus">
      <h2>M4 ja muut haarat</h2>
      <p>M4 vertaa FI-tuomioita (K1) rikosotsikon kansalaisuusavaimiin. Yksiköt eivät
      täsmää; media ei selitä K1:tä. Linkit:
      <a href="../index.html">K1</a>,
      <a href="../maahanmuutto-fi/index.html">FI-paneeli</a> (erillinen TUTKIVA),
      <a href="../tutkimus/index.html">tutkimus-hubi</a>.</p>
    </aside>
"""
        media = f"""
    <div class="kieli-fi">
{md_html(rap_media.read_text(encoding="utf-8"))}
{m4_huom}
    </div>
    <div class="kieli-en" hidden>
      <h1>Media</h1>
      <p>The phase-8 report is in Finnish: <a href="RAPORTTI_MEDIA.md">RAPORTTI_MEDIA.md</a>.</p>
      <p>Preregistration 2026-11-01. Outlets: Iltalehti and Yle. Calendar 2015–2025; missing HTML is empty, not zero. Human coding is missing. H3, H4, H6, H7 (main), P2 (main), P3 and P5 are not testable. M4 compares FI convictions with citizenship strings in crime headlines; the units differ. No motives, audience effects, or causal claims.</p>
      <p>Separate branches: <a href="../index.html">K1</a>,
      <a href="../maahanmuutto-fi/index.html">FI panel</a>,
      <a href="../tutkimus/index.html">research hub</a>.</p>
    </div>
"""
    from src.site import ristiviittaukset

    (DOCS_DIR / "media" / "index.html").write_text(
        _kehys(
            "Media",
            "media",
            True,
            True,
            "../tyyli.css",
            "../sivu.js",
            media,
            sijainti="media",
            ristiviittaus=ristiviittaukset(aktiivinen="media", sijainti="media"),
        ),
        encoding="utf-8",
    )


def kirjoita_tutkimus_hub() -> None:
    from src.site import tutkimus_hub_html

    kohde = DOCS_DIR / "tutkimus"
    kohde.mkdir(parents=True, exist_ok=True)
    (kohde / "index.html").write_text(tutkimus_hub_html(), encoding="utf-8")


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
    kirjoita_tutkimus_hub()


if __name__ == "__main__":
    kirjoita()
    print("kirjoitettu", DOCS_DIR / "index.html")
