"""Polut, EU-maat ja suomenkieliset nimet."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = ROOT / "data" / "raw"
OUTPUT_DIR = ROOT / "output"
TABLES_DIR = OUTPUT_DIR / "tables"
INTERIM_DIR = ROOT / "data" / "interim"
PROCESSED_DIR = ROOT / "data" / "processed"
MANIFEST_PATH = CACHE_DIR / "MANIFEST.csv"
MAA_VUOSI_PATH = PROCESSED_DIR / "maa_vuosi.csv"
COVERAGE_PATH = TABLES_DIR / "coverage_matrix.csv"

SDMX_CSV_URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{code}"
    "?format=SDMX-CSV"
)

# Käyttäjän nimeämät lähteet (varmistettu API-haulla, ei arvattu).
CRIME_DATASET = "crim_just_ctz"
POP_DATASET = "migr_pop5ctz"

YEARS_ABS = list(range(2008, 2025))
YEARS_RATE = list(range(2009, 2025))
YEARS_AVG = list(range(2020, 2025))

# EU-27 (tilanne 2020–). Yhdenmukainen joukko koko aikasarjalle.
EU27 = [
    "AT", "BE", "BG", "CY", "CZ", "DE", "DK", "EE", "EL", "ES",
    "FI", "FR", "HR", "HU", "IE", "IT", "LT", "LU", "LV", "MT",
    "NL", "PL", "PT", "RO", "SE", "SI", "SK",
]

MAAN_NIMET_EN = {
    "AT": "Austria",
    "BE": "Belgium",
    "BG": "Bulgaria",
    "CY": "Cyprus",
    "CZ": "Czechia",
    "DE": "Germany",
    "DK": "Denmark",
    "EE": "Estonia",
    "EL": "Greece",
    "ES": "Spain",
    "FI": "Finland",
    "FR": "France",
    "HR": "Croatia",
    "HU": "Hungary",
    "IE": "Ireland",
    "IT": "Italy",
    "LT": "Lithuania",
    "LU": "Luxembourg",
    "LV": "Latvia",
    "MT": "Malta",
    "NL": "Netherlands",
    "PL": "Poland",
    "PT": "Portugal",
    "RO": "Romania",
    "SE": "Sweden",
    "SI": "Slovenia",
    "SK": "Slovakia",
}

MAAN_NIMET = {
    "AT": "Itävalta",
    "BE": "Belgia",
    "BG": "Bulgaria",
    "CY": "Kypros",
    "CZ": "Tšekki",
    "DE": "Saksa",
    "DK": "Tanska",
    "EE": "Viro",
    "EL": "Kreikka",
    "ES": "Espanja",
    "FI": "Suomi",
    "FR": "Ranska",
    "HR": "Kroatia",
    "HU": "Unkari",
    "IE": "Irlanti",
    "IT": "Italia",
    "LT": "Liettua",
    "LU": "Luxemburg",
    "LV": "Latvia",
    "MT": "Malta",
    "NL": "Alankomaat",
    "PL": "Puola",
    "PT": "Portugali",
    "RO": "Romania",
    "SE": "Ruotsi",
    "SI": "Slovenia",
    "SK": "Slovakia",
}

VARIT = {
    "NAT": "#2c5aa0",
    "FOR": "#c45c26",
}

ALAVIITE = (
    "Ei ikä- ja sukupuolivakioitu. "
    "Eurostatin oikeuslaitostilastoissa laskentayksikkö vaihtelee maittain "
    "(henkilöitä vs. tapauksia). Lähde: Eurostat (crim_just_ctz, migr_pop5ctz)."
)

# crim_just_ctz / leg_stat (tarkistettu datasta, ei arvattu)
VAIHEET = {
    "PER_CNV": "tuomitut",
    "PER_SUSP": "epaillyt",
    "PER_PRSC": "syyteeseen",
}

VAIHE_NIMET = {
    "tuomitut": "Tuomitut",
    "epaillyt": "Epäillyt",
    "syyteeseen": "Syytteeseen asetetut",
}

DOCS_DIR = ROOT / "docs"
