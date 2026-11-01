"""Aja: python -m src.main   (projektin juuresta)."""

from __future__ import annotations

import argparse

from src.charts import (
    kaavio_absoluuttiset,
    kaavio_eu_per_100k,
    kaavio_pienoiskaaviot,
    kaavio_suhdeluku,
)
from src.config import CRIME_DATASET, OUTPUT_DIR, POP_DATASET, YEARS_ABS
from src.fetch import inspect_dimensions, load_dataset
from src.process import (
    coverage_matrix,
    eu_aggregaatti,
    keskiarvo_2020_2024,
    suodata_tuomitut,
    suodata_vaesto,
    yhdista,
)


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

    tuomitut = suodata_tuomitut(crime)
    vaesto = suodata_vaesto(pop)
    df = yhdista(tuomitut, vaesto)
    cov = coverage_matrix(df)
    eu = eu_aggregaatti(df, YEARS_ABS)
    avg = keskiarvo_2020_2024(df)

    df.to_csv(OUTPUT_DIR / "yhdistetty_data.csv", index=False, encoding="utf-8")
    cov.to_csv(OUTPUT_DIR / "coverage_matrix.csv", index=False, encoding="utf-8")
    eu.to_csv(OUTPUT_DIR / "eu_aggregaatti.csv", index=False, encoding="utf-8")
    avg.to_csv(OUTPUT_DIR / "keskiarvo_2020_2024.csv", index=False, encoding="utf-8")

    kaavio_eu_per_100k(eu, OUTPUT_DIR / "01_eu_per_100000.png")
    kaavio_suhdeluku(avg, OUTPUT_DIR / "02_suhdeluku_maittain.png")
    kaavio_pienoiskaaviot(df, OUTPUT_DIR / "03_pienoiskaaviot_maittain.png")
    kaavio_absoluuttiset(eu, OUTPUT_DIR / "04_absoluuttiset_maarat.png")

    print(f"Valmis. Tiedostot kansiossa {OUTPUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Eurostat: tuomitut kansalaisuuden mukaan")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Hae API-data uudelleen (ohita välimuisti)",
    )
    args = parser.parse_args()
    main(refresh=args.refresh)
