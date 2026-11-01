"""GitHub Pages: esirekisteröity raportti etusivulle, tutkivat maasivut erilleen."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

from src.config import DOCS_DIR, FIGURES_DIR, OUTPUT_DIR

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
    from src.site import LIPUT, _valikko

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
      <div class="yla">
        <p class="kicker"><a href="index.html" data-i18n="raportti_kicker"></a></p>
        {LIPUT}
      </div>
      <h1 data-i18n="raportti_h1">Tuomitut kansalaisuuden mukaan, EU-27</h1>
      <p class="lead" data-i18n="raportti_lead"></p>
      <div class="valitsin">{_valikko("RAPORTTI", True)}</div>
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


if __name__ == "__main__":
    kirjoita()
    print("kirjoitettu", DOCS_DIR / "index.html")
