"""Aja: python -m src.main   (projektin juuresta)."""

from __future__ import annotations

import argparse

import pandas as pd

from src.charts import (
    kaavio_absoluuttiset,
    kaavio_eu_per_100k,
    kaavio_pienoiskaaviot,
    kaavio_suhdeluku,
)
from src.config import CRIME_DATASET, OUTPUT_DIR, POP_DATASET, VAIHEET, YEARS_ABS
from src.fetch import inspect_dimensions, load_dataset
from src.process import (
    coverage_matrix,
    eu_aggregaatti,
    keskiarvo_2020_2024,
    suodata_oikeus,
    suodata_vaesto,
    yhdista,
)
from src.site import kirjoita_sivusto


def main(refresh: bool = False) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    crime = load_dataset(CRIME_DATASET, refresh=refresh)
    pop = load_dataset(POP_DATASET, refresh=refresh)

    dim_txt = (
        inspect_dimensions(crime, CRIME_DATASET)
        + "\n"
        + inspect_dimensions(pop, POP_DATASET)
    )
    (OUTPUT_DIR / "dimensiot.txt").write_text(dim_txt, encoding="utf-8")
    print(dim_txt)

    vaiheet = {
        nimi: suodata_oikeus(crime, koodi, nimi) for koodi, nimi in VAIHEET.items()
    }
    vaesto = suodata_vaesto(pop)
    df = yhdista(vaiheet, vaesto)
    cov = coverage_matrix(df)
    eu = eu_aggregaatti(df, YEARS_ABS, "tuomitut")
    avg = pd.concat(
        [
            keskiarvo_2020_2024(df, "tuomitut"),
            keskiarvo_2020_2024(df, "epaillyt"),
        ],
        ignore_index=True,
    )

    df.to_csv(OUTPUT_DIR / "yhdistetty_data.csv", index=False, encoding="utf-8")
    cov.to_csv(OUTPUT_DIR / "coverage_matrix.csv", index=False, encoding="utf-8")
    eu.to_csv(OUTPUT_DIR / "eu_aggregaatti.csv", index=False, encoding="utf-8")
    avg.to_csv(OUTPUT_DIR / "keskiarvo_2020_2024.csv", index=False, encoding="utf-8")

    avg_tuom = avg[avg["vaihe"] == "tuomitut"]
    kaavio_eu_per_100k(eu, OUTPUT_DIR / "01_eu_per_100000.png")
    kaavio_suhdeluku(avg_tuom, OUTPUT_DIR / "02_suhdeluku_maittain.png")
    kaavio_pienoiskaaviot(df, OUTPUT_DIR / "03_pienoiskaaviot_maittain.png")
    kaavio_absoluuttiset(eu, OUTPUT_DIR / "04_absoluuttiset_maarat.png")

    kirjoita_sivusto(df, avg, eu)
    print(f"Valmis. Tiedostot: {OUTPUT_DIR} ja docs/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eurostat: tuomitut kansalaisuuden mukaan")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Hae API-data uudelleen (ohita välimuisti)",
    )
    args = parser.parse_args()
    main(refresh=args.refresh)
