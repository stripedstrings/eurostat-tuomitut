"""docs/tutkimus/synteesi.html — synteesiraportti ilman yhteistä johtopäätöstä."""

from __future__ import annotations

import html
import re
import shutil
from pathlib import Path

from src.config import DOCS_DIR, ROOT

SRC_MD = ROOT / "output" / "SYNTEESI.md"
OUT_HTML = DOCS_DIR / "tutkimus" / "synteesi.html"


def _md_yksinkertainen(teksti: str) -> str:
    """Kevyt md→html (otsikot, listat, kappaleet, lihavointi)."""
    osat: list[str] = []
    lista_auki = False
    for ln in teksti.splitlines():
        if ln.startswith("### "):
            if lista_auki:
                osat.append("</ul>")
                lista_auki = False
            osat.append(f"<h3>{html.escape(ln[4:])}</h3>")
        elif ln.startswith("## "):
            if lista_auki:
                osat.append("</ul>")
                lista_auki = False
            osat.append(f"<h2>{html.escape(ln[3:])}</h2>")
        elif ln.startswith("# "):
            if lista_auki:
                osat.append("</ul>")
                lista_auki = False
            osat.append(f"<h1>{html.escape(ln[2:])}</h1>")
        elif ln.startswith("- "):
            if not lista_auki:
                osat.append("<ul>")
                lista_auki = True
            sis = html.escape(ln[2:])
            sis = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", sis)
            sis = re.sub(r"`(.+?)`", r"<code>\1</code>", sis)
            osat.append(f"<li>{sis}</li>")
        elif ln.strip() == "" or ln.strip() == "---":
            if lista_auki:
                osat.append("</ul>")
                lista_auki = False
            if ln.strip() == "---":
                osat.append("<hr>")
        else:
            if lista_auki:
                osat.append("</ul>")
                lista_auki = False
            sis = html.escape(ln)
            sis = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", sis)
            sis = re.sub(r"`(.+?)`", r"<code>\1</code>", sis)
            osat.append(f"<p>{sis}</p>")
    if lista_auki:
        osat.append("</ul>")
    return "\n".join(osat)


def aja() -> Path:
    from src.site import aihe_nav, ristiviittaukset

    if not SRC_MD.exists():
        raise FileNotFoundError(SRC_MD)
    (DOCS_DIR / "tutkimus").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC_MD, DOCS_DIR / "tutkimus" / "SYNTEESI.md")
    body = _md_yksinkertainen(SRC_MD.read_text(encoding="utf-8"))
    # poista ensimmäinen h1 body:sta (sivulla jo otsikko)
    body = re.sub(r"<h1>.*?</h1>\s*", "", body, count=1)

    sivu = f"""<!DOCTYPE html>
<html lang="fi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Synteesi — ei yhteistä johtopäätöstä</title>
  <link rel="stylesheet" href="../tyyli.css">
</head>
<body class="raportti">
  <header>
    <div class="wrap">
      {aihe_nav(sijainti="tutkimus", aktiivinen="tutkimus")}
      <h1>Synteesi</h1>
      <p class="lead">Mitä kukin haara näyttää / ei näytä / avoimet kysymykset.
      <strong>Ei yhteistä johtopäätöstä.</strong></p>
    </div>
  </header>
  <main class="wrap">
    <aside class="kortti">
      <p>Lähde: <a href="SYNTEESI.md">SYNTEESI.md</a> ·
      <a href="index.html">Hub</a> · <a href="tila.html">Tila</a> ·
      <a href="aikajana.html">Aikajanat (ei päättelyyn)</a></p>
    </aside>
    {body}
    {ristiviittaukset(aktiivinen="tutkimus", sijainti="tutkimus")}
  </main>
  <script src="../sivu.js"></script>
</body>
</html>
"""
    OUT_HTML.write_text(sivu, encoding="utf-8")
    print("kirjoitettu", OUT_HTML)
    return OUT_HTML


if __name__ == "__main__":
    aja()
