"""Hae ja siivoa FI-maahanmuuttopaneelin taulut. Ei täyttöä, ei K1."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from datetime import date
from pathlib import Path

import pandas as pd

from src.config import CACHE_DIR, ROOT
from src.fi_migr.paths import HAETTU, INTERIM, RAW, TABLES
from src.national.common import kirjaa_manifest

USER_AGENT = "eu-rikollisuus-kansalaisuus/0.1 (tutkimuskäyttö; FI-migr)"
STATFIN_11A8 = "https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/muutl/11a8.px"
STATFIN_11RT = "https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/vaerak/11rt.px"
STATFIN_159T = "https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/vaerak/159t.px"
MIGRI_KIINTIO = "https://migri.fi/kiintiopakolaistilastot"


def _curl_post_json(url: str, payload: dict, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    body = INTERIM / (dest.stem + "_query.json")
    INTERIM.mkdir(parents=True, exist_ok=True)
    body.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    p = subprocess.run(
        [
            "curl.exe",
            "-sS",
            "-L",
            "-A",
            USER_AGENT,
            "--max-time",
            "120",
            "-H",
            "Content-Type: application/json",
            "-d",
            f"@{body}",
            "-o",
            str(dest),
            "-w",
            "%{http_code}",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=130,
        check=False,
    )
    try:
        return int((p.stdout or "").strip()[-3:])
    except ValueError:
        return 0


def _curl_get(url: str, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    p = subprocess.run(
        [
            "curl.exe",
            "-sS",
            "-L",
            "-A",
            USER_AGENT,
            "--max-time",
            "60",
            "-o",
            str(dest),
            "-w",
            "%{http_code}",
            url,
        ],
        capture_output=True,
        text=True,
        timeout=70,
        check=False,
    )
    try:
        return int((p.stdout or "").strip()[-3:])
    except ValueError:
        return 0


def hae_statfin_11a8() -> Path:
    """Maahan-/maastamuutto kansalaisuus × syntyperä, koko maa."""
    vuodet = [str(y) for y in range(1990, 2026)]
    payload = {
        "query": [
            {"code": "timeperiod_y", "selection": {"filter": "item", "values": vuodet}},
            {
                "code": "valtio_19_20190101",
                "selection": {"filter": "item", "values": ["SSS", "246", "ULK"]},
            },
            {
                "code": "kieli_15_20180102",
                "selection": {"filter": "item", "values": ["SSS"]},
            },
            {
                "code": "syntypera_101_20180101",
                "selection": {"filter": "item", "values": ["SSS"]},
            },
            {
                "code": "sukupuoli_9_20180101",
                "selection": {"filter": "item", "values": ["SSS"]},
            },
            {
                "code": "contentscode",
                "selection": {
                    "filter": "item",
                    "values": ["muutl-vm41", "muutl-vm42", "muutl-vm4142"],
                },
            },
        ],
        "response": {"format": "csv"},
    }
    dest = RAW / "statfin_11a8.csv"
    code = _curl_post_json(STATFIN_11A8, payload, dest)
    if code != 200 or dest.stat().st_size < 50:
        raise RuntimeError(f"StatFin 11a8 HTTP {code}")
    kirjaa_manifest(dest.name, "StatFin 11a8", STATFIN_11A8, f"http={code}")
    return dest


def hae_statfin_11rt() -> Path:
    """Väestö ikä × sukupuoli × syntyperä, koko maa, taustamaa SSS."""
    vuodet = [str(y) for y in range(2000, 2026)]
    payload = {
        "query": [
            {
                "code": "alue_23_20260101",
                "selection": {"filter": "item", "values": ["SSS"]},
            },
            {
                "code": "valtio_19_20190101",
                "selection": {"filter": "item", "values": ["SSS"]},
            },
            {
                "code": "sukupuoli_9_20180101",
                "selection": {"filter": "item", "values": ["SSS", "1", "2"]},
            },
            {
                "code": "ikaryhma_10_20180101",
                "selection": {"filter": "item", "values": ["SSS", "0-6", "7-14", "15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-"]},
            },
            {
                "code": "syntypera_101_20180101",
                "selection": {"filter": "item", "values": ["1", "2"]},
            },
            {"code": "timeperiod_y", "selection": {"filter": "item", "values": vuodet}},
            {
                "code": "contentscode",
                "selection": {"filter": "item", "values": ["vaerak-vaesto"]},
            },
        ],
        "response": {"format": "csv"},
    }
    dest = RAW / "statfin_11rt.csv"
    code = _curl_post_json(STATFIN_11RT, payload, dest)
    if code != 200 or dest.stat().st_size < 50:
        raise RuntimeError(f"StatFin 11rt HTTP {code}")
    kirjaa_manifest(dest.name, "StatFin 11rt", STATFIN_11RT, f"http={code}")
    return dest


def hae_statfin_159t() -> Path:
    vuodet = [str(y) for y in range(1990, 2026)]
    payload = {
        "query": [
            {"code": "timeperiod_y", "selection": {"filter": "item", "values": vuodet}},
            {
                "code": "alue_23_20260101",
                "selection": {"filter": "item", "values": ["SSS"]},
            },
            {
                "code": "contentscode",
                "selection": {
                    "filter": "item",
                    "values": [
                        "vaerak-vaesto",
                        "vaesto_kansa_ulk",
                        "vaesto_svaltio_ulk",
                        "vaesto_kieli_ulk",
                        "vaesto_tausta_ulk",
                        "vaesto_kansa_ulk_p",
                        "vaesto_svaltio_ulk_p",
                        "vaesto_kieli_ulk_p",
                        "vaesto_tausta_ulk_p",
                    ],
                },
            },
        ],
        "response": {"format": "csv"},
    }
    dest = RAW / "statfin_159t.csv"
    code = _curl_post_json(STATFIN_159T, payload, dest)
    if code != 200 or dest.stat().st_size < 50:
        raise RuntimeError(f"StatFin 159t HTTP {code}")
    kirjaa_manifest(dest.name, "StatFin 159t", STATFIN_159T, f"http={code}")
    return dest


def hae_migri_kiintio_html() -> Path:
    dest = RAW / "migri_kiintiopakolaiset.html"
    code = _curl_get(MIGRI_KIINTIO, dest)
    if code != 200:
        raise RuntimeError(f"Migri kiintiö HTTP {code}")
    kirjaa_manifest(dest.name, "Migri", MIGRI_KIINTIO, f"http={code}")
    return dest


def _lue_eurostat_fi(koodi: str) -> pd.DataFrame:
    path = CACHE_DIR / f"{koodi}.csv"
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, low_memory=False)
    geo = "geo" if "geo" in df.columns else "GEO"
    if geo not in df.columns:
        return pd.DataFrame()
    return df[df[geo].astype(str) == "FI"].copy()


def _num_sarja(s: pd.Series) -> pd.Series:
    return pd.to_numeric(
        s.astype(str)
        .str.replace("\u00a0", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )


def siivoa_tulot(path_11a8: Path) -> pd.DataFrame:
    df = pd.read_csv(path_11a8)
    cols = list(df.columns)
    vuosi_c = cols[0]
    kans_c = cols[1]
    maa_c = next(c for c in cols if "Maahanmuutto" in c)
    maa_out = next(c for c in cols if "Maastamuutto" in c and "Netto" not in c)
    netto_c = next(c for c in cols if "Netto" in c)
    out = pd.DataFrame(
        {
            "vuosi": pd.to_numeric(df[vuosi_c], errors="coerce").astype("Int64"),
            "kansalaisuus": df[kans_c].astype(str),
            "maahanmuutto": _num_sarja(df[maa_c]),
            "maastamuutto": _num_sarja(df[maa_out]),
            "nettomaahanmuutto": _num_sarja(df[netto_c]),
            "lahde": "StatFin 11a8",
            "haettu": HAETTU,
        }
    )
    return out


def siivoa_ika_sukupuoli(path_11rt: Path) -> pd.DataFrame:
    """PxWeb leveä: sarakkeet 'Sukupuoli Ikä Syntyperä Vuosi Väestö 31.12.'."""
    df = pd.read_csv(path_11rt)
    # Pidä vain KOKO MAA + YHTEENSÄ taustamaa
    if "Maakunta" in df.columns:
        df = df[df["Maakunta"].astype(str).str.contains("KOKO MAA", case=False, na=False)]
    if "Taustamaa" in df.columns:
        df = df[df["Taustamaa"].astype(str).str.contains("YHTEENSÄ|Yhteensä", case=False, na=False)]
    rivit: list[dict] = []
    pat = re.compile(
        r"^(Yhteensä|Miehet|Naiset)\s+(.+?)\s+(Suomalaistaustaiset yhteensä|Ulkomaalaistaustaiset yhteensä)\s+(20\d{2})\s+Väestö",
        re.I,
    )
    for c in df.columns:
        m = pat.match(str(c).strip())
        if not m:
            continue
        suk, ika, syn, vuosi = m.group(1), m.group(2), m.group(3), m.group(4)
        val = _num_sarja(df[c]).iloc[0] if len(df) else float("nan")
        rivit.append(
            {
                "vuosi": int(vuosi),
                "sukupuoli": suk,
                "ika": ika,
                "syntypera": syn,
                "vaesto": val,
                "lahde": "StatFin 11rt",
                "haettu": HAETTU,
            }
        )
    return pd.DataFrame(rivit)


def siivoa_stock_159t(path_159t: Path) -> pd.DataFrame:
    df = pd.read_csv(path_159t)
    vuosi_col = next(c for c in df.columns if "vuosi" in c.lower())
    skip = {vuosi_col}
    skip |= {c for c in df.columns if "alue" in c.lower()}
    rivit = []
    for _, row in df.iterrows():
        vuosi = pd.to_numeric(row[vuosi_col], errors="coerce")
        for c in df.columns:
            if c in skip:
                continue
            rivit.append(
                {
                    "vuosi": vuosi,
                    "mittari": c,
                    "arvo": _num_sarja(pd.Series([row[c]])).iloc[0],
                    "lahde": "StatFin 159t",
                    "haettu": HAETTU,
                }
            )
    return pd.DataFrame(rivit)


def siivoa_tyollisyys_koulutus() -> tuple[pd.DataFrame, pd.DataFrame]:
    tyo_rivit: list[dict] = []
    kou_rivit: list[dict] = []
    ergan = _lue_eurostat_fi("lfsa_ergan")
    if not ergan.empty:
        # typical columns: sex, age, citizen, unit, TIME_PERIOD, OBS_VALUE
        for col in ergan.columns:
            if col.lower() in {"obs_value", "obsvalue"}:
                ergan = ergan.rename(columns={col: "OBS_VALUE"})
        tp = "TIME_PERIOD" if "TIME_PERIOD" in ergan.columns else "time"
        sub = ergan.copy()
        if "sex" in sub.columns:
            sub = sub[sub["sex"].astype(str) == "T"]
        if "age" in sub.columns:
            # prefer Y15-64 if present
            ages = set(sub["age"].astype(str))
            prefer = "Y15-64" if "Y15-64" in ages else ("Y20-64" if "Y20-64" in ages else None)
            if prefer:
                sub = sub[sub["age"].astype(str) == prefer]
        if "unit" in sub.columns:
            units = set(sub["unit"].astype(str))
            if "PC" in units:
                sub = sub[sub["unit"].astype(str) == "PC"]
        if "citizen" in sub.columns:
            sub = sub[sub["citizen"].astype(str).isin(["NAT", "FOR", "TOTAL", "EU27_2020_FOR", "NEU27_2020_FOR"])]
        for _, r in sub.iterrows():
            tyo_rivit.append(
                {
                    "vuosi": int(float(r[tp])) if pd.notna(r[tp]) else pd.NA,
                    "citizen": str(r.get("citizen", "")),
                    "age": str(r.get("age", "")),
                    "mittari": "tyollisyysaste_pct",
                    "arvo": pd.to_numeric(r.get("OBS_VALUE"), errors="coerce"),
                    "lahde": "Eurostat lfsa_ergan",
                    "haettu": HAETTU,
                    "huom": "kansalaisuus ≠ maahanmuuttotausta",
                }
            )
    urgan = _lue_eurostat_fi("lfsa_urgan")
    if not urgan.empty:
        for col in urgan.columns:
            if col.lower() in {"obs_value", "obsvalue"}:
                urgan = urgan.rename(columns={col: "OBS_VALUE"})
        tp = "TIME_PERIOD" if "TIME_PERIOD" in urgan.columns else "time"
        sub = urgan.copy()
        if "sex" in sub.columns:
            sub = sub[sub["sex"].astype(str) == "T"]
        if "age" in sub.columns:
            ages = set(sub["age"].astype(str))
            prefer = "Y15-74" if "Y15-74" in ages else ("Y15-64" if "Y15-64" in ages else None)
            if prefer:
                sub = sub[sub["age"].astype(str) == prefer]
        if "unit" in sub.columns and "PC_ACT" in set(sub["unit"].astype(str)):
            sub = sub[sub["unit"].astype(str) == "PC_ACT"]
        if "citizen" in sub.columns:
            sub = sub[sub["citizen"].astype(str).isin(["NAT", "FOR", "TOTAL", "EU27_2020_FOR", "NEU27_2020_FOR"])]
        for _, r in sub.iterrows():
            tyo_rivit.append(
                {
                    "vuosi": int(float(r[tp])) if pd.notna(r[tp]) else pd.NA,
                    "citizen": str(r.get("citizen", "")),
                    "age": str(r.get("age", "")),
                    "mittari": "tyottomyysaste_pct",
                    "arvo": pd.to_numeric(r.get("OBS_VALUE"), errors="coerce"),
                    "lahde": "Eurostat lfsa_urgan",
                    "haettu": HAETTU,
                    "huom": "kansalaisuus ≠ maahanmuuttotausta",
                }
            )
    edat = _lue_eurostat_fi("edat_lfs_9911")
    if not edat.empty:
        for col in edat.columns:
            if col.lower() in {"obs_value", "obsvalue"}:
                edat = edat.rename(columns={col: "OBS_VALUE"})
        tp = "TIME_PERIOD" if "TIME_PERIOD" in edat.columns else "time"
        sub = edat.copy()
        if "sex" in sub.columns:
            sub = sub[sub["sex"].astype(str) == "T"]
        if "age" in sub.columns:
            ages = set(sub["age"].astype(str))
            prefer = "Y25-64" if "Y25-64" in ages else None
            if prefer:
                sub = sub[sub["age"].astype(str) == prefer]
        if "unit" in sub.columns and "PC" in set(sub["unit"].astype(str)):
            sub = sub[sub["unit"].astype(str) == "PC"]
        if "citizen" in sub.columns:
            sub = sub[sub["citizen"].astype(str).isin(["NAT", "FOR", "TOTAL", "EU27_2020_FOR", "NEU27_2020_FOR"])]
        if "isced11" in sub.columns:
            # keep broad levels if present
            keep = [v for v in ("ED0-2", "ED3_4", "ED5-8", "TOTAL") if v in set(sub["isced11"].astype(str))]
            if keep:
                sub = sub[sub["isced11"].astype(str).isin(keep)]
        for _, r in sub.iterrows():
            kou_rivit.append(
                {
                    "vuosi": int(float(r[tp])) if pd.notna(r[tp]) else pd.NA,
                    "citizen": str(r.get("citizen", "")),
                    "isced11": str(r.get("isced11", "")),
                    "arvo_pct": pd.to_numeric(r.get("OBS_VALUE"), errors="coerce"),
                    "lahde": "Eurostat edat_lfs_9911",
                    "haettu": HAETTU,
                    "huom": "kansalaisuus ≠ maahanmuuttotausta",
                }
            )
    return pd.DataFrame(tyo_rivit), pd.DataFrame(kou_rivit)


def siivoa_luvat() -> pd.DataFrame:
    rivit: list[dict] = []
    for koodi, nimi in (("migr_resfirst", "ensimmaiset"), ("migr_resvalid", "voimassa")):
        df = _lue_eurostat_fi(koodi)
        if df.empty:
            continue
        for col in df.columns:
            if col.lower() in {"obs_value", "obsvalue"}:
                df = df.rename(columns={col: "OBS_VALUE"})
        tp = "TIME_PERIOD" if "TIME_PERIOD" in df.columns else "time"
        sub = df.copy()
        if "citizen" in sub.columns:
            sub = sub[sub["citizen"].astype(str) == "TOTAL"]
        if "reason" in sub.columns:
            syyt = ["TOTAL", "EDUC", "EMP", "FAM", "OTH", "RFG", "SPROT"]
            sub = sub[sub["reason"].astype(str).isin(syyt)]
        if "unit" in sub.columns:
            units = set(sub["unit"].astype(str))
            prefer = "PER" if "PER" in units else ("NR" if "NR" in units else None)
            if prefer:
                sub = sub[sub["unit"].astype(str) == prefer]
        if "duration" in sub.columns:
            durs = set(sub["duration"].astype(str))
            prefer = "TOTAL" if "TOTAL" in durs else None
            if prefer:
                sub = sub[sub["duration"].astype(str) == prefer]
        for _, r in sub.iterrows():
            rivit.append(
                {
                    "vuosi": int(float(r[tp])) if pd.notna(r[tp]) else pd.NA,
                    "lupa": nimi,
                    "reason": str(r.get("reason", "")),
                    "arvo": pd.to_numeric(r.get("OBS_VALUE"), errors="coerce"),
                    "lahde": f"Eurostat {koodi}",
                    "haettu": HAETTU,
                    "huom": "kolmansien maiden kansalaiset; ei EU-kansalaisia",
                }
            )
    return pd.DataFrame(rivit)


def parse_migri_kiintio(html_path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Poimi saapuneet/valitut jos HTML:ssä; meta asettajasta. Ei arvaa lukuja."""
    teksti = html_path.read_text(encoding="utf-8", errors="replace")
    meta_rivit = [
        {
            "vuosi": "",
            "paatetty_kiintio": "",
            "asettaja": "Suomen valtioneuvosto (esitys) / eduskunta (talousarvio / päätös)",
            "unhcr_rooli": "ehdottaa uudelleensijoitettavia henkilöitä; ei aseta Suomen vuosikiintiötä",
            "lahde_url": MIGRI_KIINTIO,
            "haettu": HAETTU,
            "huom": "TUTKIVA; vuosikohtainen päätetty luku täytetään vain jos löytyy lähteestä",
        }
    ]
    # Etsi "Suomeen saapui N…" — vuosi h3-otsikosta "...jakauma YYYY"
    saapuneet: list[dict] = []
    for m in re.finditer(
        r"ikä- ja sukupuolijakauma\s+(20\d{2}).{0,400}?Suomeen saapui\s+(\d[\d\s]*)\s+kiintiöpakolaista",
        teksti,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        vuosi = m.group(1)
        n = int(re.sub(r"\s+", "", m.group(2)))
        saapuneet.append(
            {
                "vuosi": vuosi,
                "mittari": "saapuneet_kiintiopakolaiset",
                "arvo": n,
                "lahde": "Migri kiintiöpakolaistilastot",
                "lahde_url": MIGRI_KIINTIO,
                "haettu": HAETTU,
            }
        )
    # Vuosittaiset päätetyt kiintiöt: etsi "kiintiö" + luku lähellä vuotta — vain selkeät taulukon "Yhteensä | N"
    for m in re.finditer(r"Yhteensä</t[dh]>\s*<t[dh][^>]*>\s*(\d+)\s*<", teksti, flags=re.I):
        n = int(m.group(1))
        ennen = teksti[max(0, m.start() - 2500) : m.start()]
        vuodet = re.findall(r"<h[1-4][^>]*>\s*(20\d{2})\s*<", ennen)
        if not vuodet:
            vuodet = re.findall(r">\s*(20\d{2})\s*<", ennen)
        vuosi = vuodet[-1] if vuodet else ""
        if vuosi and 100 <= n <= 5000:
            meta_rivit.append(
                {
                    "vuosi": vuosi,
                    "paatetty_kiintio": str(n),
                    "asettaja": "Suomen valtioneuvosto / eduskunta (ks. vuosittainen päätös); Migri julkaisee toteutuman",
                    "unhcr_rooli": "ehdottaa henkilöitä",
                    "lahde_url": MIGRI_KIINTIO,
                    "haettu": HAETTU,
                    "huom": "poimittu Migri-sivun Yhteensä-riviltä (valitut); tarkista lähteestä",
                }
            )
    return pd.DataFrame(saapuneet), pd.DataFrame(meta_rivit)


def kirjoita_kieli_na() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "mittari": "kielitaito_taso",
                "saatavuus": "ei",
                "arvo": "",
                "huom": "kotoutumisindikaattorien PxWeb ei vastannut probe:ssa; ei täytetä",
                "haettu": HAETTU,
            },
            {
                "mittari": "kieli_oppimisaika_kk",
                "saatavuus": "ei",
                "arvo": "",
                "huom": "ei avointa aikasarjaa; ei estimoida",
                "haettu": HAETTU,
            },
        ]
    )


def _tallenna(df: pd.DataFrame, nimi: str) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    polku = TABLES / nimi
    df.to_csv(polku, index=False, encoding="utf-8")
    print("kirjoitettu", polku, "rivit", len(df), flush=True)


def peitto(
    tulot: pd.DataFrame,
    ika: pd.DataFrame,
    tyo: pd.DataFrame,
    kou: pd.DataFrame,
    luvat: pd.DataFrame,
    kiintio: pd.DataFrame,
    kieli: pd.DataFrame,
) -> pd.DataFrame:
    rivit = []

    def add(aihe: str, lahde: str, df: pd.DataFrame, vuosi_col: str = "vuosi") -> None:
        if df is None or df.empty:
            rivit.append(
                {
                    "aihe": aihe,
                    "lahde": lahde,
                    "vuosi_min": "",
                    "vuosi_max": "",
                    "n_rivia": "0",
                    "saatavuus": "ei",
                }
            )
            return
        if vuosi_col in df.columns:
            v = pd.to_numeric(df[vuosi_col], errors="coerce").dropna()
            vmin = str(int(v.min())) if len(v) else ""
            vmax = str(int(v.max())) if len(v) else ""
        else:
            vmin = vmax = ""
        rivit.append(
            {
                "aihe": aihe,
                "lahde": lahde,
                "vuosi_min": vmin,
                "vuosi_max": vmax,
                "n_rivia": str(len(df)),
                "saatavuus": "kylla" if len(df) else "ei",
            }
        )

    add("tulot_maahanmuutto", "StatFin 11a8", tulot)
    add("ika_sukupuoli_syntypera", "StatFin 11rt", ika)
    add("tyollisyys", "Eurostat LFS", tyo)
    add("koulutus", "Eurostat edat_lfs_9911", kou)
    add("oleskeluluvat", "Eurostat migr_res*", luvat)
    add("kiintiopakolaiset", "Migri", kiintio)
    if kieli is None or kieli.empty:
        add("kieli_oppimisaika", "—", pd.DataFrame())
    else:
        rivit.append(
            {
                "aihe": "kieli_oppimisaika",
                "lahde": "—",
                "vuosi_min": "",
                "vuosi_max": "",
                "n_rivia": "0",
                "saatavuus": "ei",
            }
        )
    return pd.DataFrame(rivit)


def aja() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    INTERIM.mkdir(parents=True, exist_ok=True)

    p11 = hae_statfin_11a8()
    p11rt = hae_statfin_11rt()
    p159 = hae_statfin_159t()
    pmig = hae_migri_kiintio_html()

    tulot = siivoa_tulot(p11)
    _tallenna(tulot, "fi_migr_tulot_vuosi.csv")

    ika = siivoa_ika_sukupuoli(p11rt)
    _tallenna(ika, "fi_migr_ika_sukupuoli.csv")

    stock = siivoa_stock_159t(p159)
    _tallenna(stock, "fi_migr_vaesto_osuudet.csv")

    tyo, kou = siivoa_tyollisyys_koulutus()
    _tallenna(tyo, "fi_migr_tyollisyys.csv")
    _tallenna(kou, "fi_migr_koulutus.csv")

    luvat = siivoa_luvat()
    _tallenna(luvat, "fi_migr_luvat.csv")

    kiintio, meta = parse_migri_kiintio(pmig)
    _tallenna(kiintio, "fi_migr_kiintio.csv")
    _tallenna(meta, "fi_migr_kiintio_meta.csv")

    kieli = kirjoita_kieli_na()
    _tallenna(kieli, "fi_migr_kieli_kotoutuminen.csv")

    pe = peitto(tulot, ika, tyo, kou, luvat, kiintio, kieli)
    _tallenna(pe, "fi_migr_peitto.csv")


if __name__ == "__main__":
    aja()
