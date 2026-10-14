"""Kontrollera kunddata innan modellen tränas."""

import argparse
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from pandera.errors import SchemaErrors

KUND_SCHEMA = pa.DataFrameSchema(
    {
        "kund_id": pa.Column(
            int,
            checks=pa.Check.gt(0),
            nullable=False,
            unique=True,
        ),
        "alder": pa.Column(
            int,
            checks=pa.Check.ge(0),
            nullable=False,
        ),
        "region": pa.Column(
            str,
            checks=pa.Check.str_matches(r"\S"),
            nullable=False,
        ),
        "abonnemang": pa.Column(
            str,
            checks=pa.Check.isin(["Bas", "Standard", "Premium"]),
            nullable=False,
        ),
        "manader_som_kund": pa.Column(
            int,
            checks=pa.Check.ge(0),
            nullable=False,
        ),
        "manadskostnad": pa.Column(
            float,
            checks=pa.Check.ge(0),
            nullable=False,
            coerce=True,
        ),
        "data_gb_per_manad": pa.Column(
            float,
            checks=pa.Check.ge(0),
            nullable=False,
            coerce=True,
        ),
        "supportarenden_12m": pa.Column(
            int,
            checks=pa.Check.ge(0),
            nullable=False,
        ),
        "avslutat": pa.Column(
            int,
            checks=pa.Check.isin([0, 1]),
            nullable=False,
        ),
    },
    strict=True,
    checks=pa.Check(
        lambda df: len(df) > 0,
        error="Datafilen får inte vara tom.",
    ),
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validera kunddata med Pandera.")
    parser.add_argument(
        "datafil",
        type=Path,
        help="Sökväg till CSV-filen som ska kontrolleras.",
    )
    args = parser.parse_args()

    try:
        kunddata = pd.read_csv(args.datafil)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        print(f"Kunde inte läsa datafilen: {exc}")
        return 1

    try:
        KUND_SCHEMA.validate(kunddata, lazy=True)
    except SchemaErrors as exc:
        print(f"UNDERKÄND: {args.datafil}")
        print("Upptäckta schemafel:")
        print(exc.failure_cases.to_string(index=False))
        return 1

    print(f"GODKÄND: {args.datafil} ({len(kunddata)} rader)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
