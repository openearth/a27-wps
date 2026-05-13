#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingest tree health data (bomenpy.xlsx) into gws.boom and gws.boom_meting.

Run the three CREATE TABLE scripts first, then execute this script once:

    sql/create_table_boom.sql
    sql/create_table_boom_meting.sql
    sql/create_table_boom_conditie_lookup.sql

    python sql/ingest_bomen.py \
        [--xlsx PATH_TO_BOMENPY.XLSX] \
        [--locations-xlsx PATH_TO_LOCATIEBOMEN.XLSX]

The script is idempotent (ON CONFLICT DO UPDATE) and can be re-run safely.

COORDINATE ASSUMPTION
    X/Y values in locatiebomen.xlsx are treated as RD New (EPSG:28992), which
    is the project's native coordinate system.  RD New X typically ranges
    0–300 000 and Y 289 000–629 000.  Verify before the first run.

WHY NOT GEOPANDAS?
    The location source is an Excel file with simple X/Y columns, not a
    shapefile or GeoPackage.  Using pyproj + PostGIS ST_MakePoint keeps the
    ingestion script lightweight and avoids adding the GeoPandas/GDAL dependency
    stack just to create point geometries.  If future tree locations arrive as a
    shapefile, GeoPandas would be a good fit for that ingestion path.
"""

import argparse
import configparser
import math
import sys
from pathlib import Path

import pandas as pd
import pyproj
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SERVICE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_XLSX = Path(r"C:\data\a27\bomenpy.xlsx")
DEFAULT_LOCATIONS_XLSX = Path(r"C:\data\a27\locatiebomen.xlsx")

# ---------------------------------------------------------------------------
# Condition-label → numeric-score mapping  (source: bomendata.py)
# ---------------------------------------------------------------------------
VALTONUM = {
    "Goed":                                 8,
    "goed":                                 8,
    "Voldoende-goed":                       7,
    "voldoende-goed":                       7,
    "voldoende-Goed":                       7,
    "Voldoende-Goed":                       7,
    "Voldoende":                            6,
    "Voldoende (?)":                         6,
    "voldoende":                            6,
    "Voldoende-matig":                      5,
    "voldoende-matig":                      5,
    "Matig":                                4,
    "matig":                                4,
    "Matig-slecht":                         3,
    "matig-slecht":                         3,
    "Slecht":                               2,
    "Bijna dood":                           1,
    "Dood":                                 0,
    "Meegesleurd door vallende es":         0,
    "c":                                    0,
    # Unmeasurable / not yet assessed → score stored as NULL
    "Nog niet voldoende zichtbaar":         None,
    "Nog niet in monitoring":               None,
    "Niet vast te stellen (te vroeg)":      None,
    "Niet meer voldoende zichtbaar":        None,
}

# Trees excluded from the group mean (matches bomendata.py comment)
EXCLUDE_FROM_GROUP_STATS: set[str] = {"9FS"}

# Columns that are tree metadata, not inspection-date columns
META_COLS = {"Boomnaam", "X", "Y", "soort"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def assign_group(boomcode: str) -> str:
    """Derive species group from boomcode prefix (mirrors bomendata.py)."""
    s = str(boomcode)
    if "Fs" in s or "FS" in s:
        return "Beuken"
    if "Fx" in s:
        return "Essen"
    if "Qu" in s:
        return "Eiken"
    return "undefined"


def load_xlsx(path: Path) -> pd.DataFrame:
    """
    Load and clean bomenpy.xlsx, replicating bomendata.py's preparation steps.

    Returns a DataFrame with:
        index   : boomcode  ("Boom- \\ncode")
        columns : soort, Boomnaam, X, Y, <date columns (datetime objects)…>
    """
    df = pd.read_excel(path)

    # The actual column header is stored in row 1 (0-indexed) of the raw sheet
    df.columns = df.iloc[1]
    df = df.drop(index=[0, 1, 2]).reset_index(drop=True)

    df = df.set_index("Boom- \ncode")

    # Preserve Soort before dropping.  The source Excel uses merged cells for
    # the tree groups, so pandas only sees the value on the first row of each
    # group.  Forward-fill to store the visible Excel value for every tree.
    soort_col = df["Soort"].ffill().copy() if "Soort" in df.columns else None
    df = df.drop(columns=["Soort"], errors="ignore")

    # Drop the first remaining unnamed column (present after Soort in the xlsx)
    df = df.drop(df.columns[0], axis=1)

    if soort_col is not None:
        df.insert(0, "soort", soort_col)

    # Remove rows with no boomcode
    df = df[df.index.notna()]
    df.index = df.index.astype(str).str.strip()
    df = df[~df.index.isin(("", "nan"))]

    return df


def load_locations_xlsx(path: Path) -> dict[str, tuple[float, float]]:
    """Load tree coordinates from locatiebomen.xlsx.

    The workbook is expected to contain columns: X, Y, Boomnaam.
    X/Y are RD New (EPSG:28992).
    """
    df = pd.read_excel(path)
    required_cols = {"X", "Y", "Boomnaam"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(
            f"Missing required columns in {path}: {', '.join(sorted(missing_cols))}"
        )

    locations = {}
    for _, row in df.iterrows():
        boomnaam = clean_text(row.get("Boomnaam"))
        x = to_float_or_none(row.get("X"))
        y = to_float_or_none(row.get("Y"))
        if boomnaam and x is not None and y is not None:
            locations[boomnaam] = (x, y)

    return locations


def clean_text(value) -> str | None:
    """Return a stripped string, treating pandas/Excel empty values as NULL."""
    if value is None or pd.isna(value):
        return None
    text_value = str(value).strip()
    if not text_value or text_value.lower() == "nan":
        return None
    return text_value


def to_float_or_none(value) -> float | None:
    """Parse numeric Excel cell values safely."""
    if value is None or pd.isna(value):
        return None
    try:
        result = float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def create_db_engine(config_path: Path):
    cf = configparser.RawConfigParser()
    cf.read(config_path)
    user     = cf.get("PostGIS", "USER")
    password = cf.get("PostGIS", "PASSWORD")
    host     = cf.get("PostGIS", "HOST")
    port     = cf.get("PostGIS", "PORT")
    database = cf.get("PostGIS", "DATABASE")
    return create_engine(
        f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--xlsx",
        default=str(DEFAULT_XLSX),
        help=f"Path to bomenpy.xlsx (default: {DEFAULT_XLSX})",
    )
    parser.add_argument(
        "--locations-xlsx",
        default=str(DEFAULT_LOCATIONS_XLSX),
        help=f"Path to locatiebomen.xlsx (default: {DEFAULT_LOCATIONS_XLSX})",
    )
    args = parser.parse_args()

    xlsx_path      = Path(args.xlsx)
    locations_path = Path(args.locations_xlsx)
    config_path    = SERVICE_DIR / "configuration.txt"

    for p, label in [
        (xlsx_path, "xlsx"),
        (locations_path, "locations xlsx"),
        (config_path, "configuration.txt"),
    ]:
        if not p.exists():
            sys.exit(f"ERROR: {label} not found at {p}")

    print(f"Loading {xlsx_path} …")
    df = load_xlsx(xlsx_path)
    print(f"Loading {locations_path} …")
    locations = load_locations_xlsx(locations_path)

    date_cols = [c for c in df.columns if c not in META_COLS]
    print(f"  Trees : {len(df)}")
    print(f"  Dates : {len(date_cols)}  ({date_cols[0]} … {date_cols[-1]})")
    print(f"  Locations : {len(locations)}")

    # RD New (EPSG:28992) → WGS84 (EPSG:4326)
    rd_to_wgs = pyproj.Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)
    engine    = create_db_engine(config_path)

    with engine.begin() as conn:

        # ------------------------------------------------------------------
        # 1. Upsert gws.boom  (one row per tree)
        # ------------------------------------------------------------------
        boom_rows = 0
        for boomcode, row in df.iterrows():
            boomnaam = clean_text(row.get("Boomnaam")) or boomcode
            soort    = clean_text(row.get("soort"))

            x_rd = to_float_or_none(row.get("X"))
            y_rd = to_float_or_none(row.get("Y"))
            if x_rd is None or y_rd is None:
                x_rd, y_rd = locations.get(boomcode, (None, None))

            if x_rd is not None and y_rd is not None:
                lon, lat   = rd_to_wgs.transform(x_rd, y_rd)
            else:
                lon = lat = None

            conn.execute(text("""
                INSERT INTO gws.boom
                    (boomcode, boomnaam, soort, soort_group,
                     geom, longitude_wgs84, latitude_wgs84,
                     exclude_from_group_stats)
                VALUES (
                    :boomcode, :boomnaam, :soort, :soort_group,
                    CASE WHEN :x IS NOT NULL
                         THEN ST_SetSRID(ST_MakePoint(:x, :y), 28992)
                    END,
                    :lon, :lat,
                    :exclude
                )
                ON CONFLICT (boomcode) DO UPDATE SET
                    boomnaam                 = EXCLUDED.boomnaam,
                    soort                    = EXCLUDED.soort,
                    soort_group              = EXCLUDED.soort_group,
                    geom                     = EXCLUDED.geom,
                    longitude_wgs84          = EXCLUDED.longitude_wgs84,
                    latitude_wgs84           = EXCLUDED.latitude_wgs84,
                    exclude_from_group_stats = EXCLUDED.exclude_from_group_stats
            """), {
                "boomcode":    boomcode,
                "boomnaam":    boomnaam,
                "soort":       soort,
                "soort_group": assign_group(boomcode),
                "x": x_rd, "y": y_rd,
                "lon": lon, "lat": lat,
                "exclude":     boomcode in EXCLUDE_FROM_GROUP_STATS,
            })
            boom_rows += 1

        print(f"  Upserted {boom_rows} rows → gws.boom")

        # ------------------------------------------------------------------
        # 2. Upsert gws.boom_meting  (wide → long melt)
        # ------------------------------------------------------------------

        # Bulk-load boom_id lookup to avoid per-row SELECT
        id_map: dict[str, int] = {
            row[0]: row[1]
            for row in conn.execute(
                text("SELECT boomcode, boom_id FROM gws.boom")
            ).fetchall()
        }

        df_long = (
            df[date_cols]
            .reset_index()
            .rename(columns={"Boom- \ncode": "boomcode"})
            .melt(
                id_vars=["boomcode"],
                value_vars=date_cols,
                var_name="datumtijd",
                value_name="conditie_text",
            )
        )

        df_long["boomcode"]  = df_long["boomcode"].astype(str).str.strip()
        df_long["datumtijd"] = pd.to_datetime(df_long["datumtijd"], errors="coerce")
        df_long = df_long.dropna(subset=["datumtijd"])
        df_long = df_long[~df_long["boomcode"].isin(("", "nan"))]

        df_long["conditie_text"]  = df_long["conditie_text"].map(clean_text)
        # Only keep rows with an actual observation
        df_long = df_long[df_long["conditie_text"].notna()].copy()
        df_long["conditie_score"] = df_long["conditie_text"].map(
            lambda v: VALTONUM.get(v)
        )

        meting_ok = meting_skip = 0
        for _, mrow in df_long.iterrows():
            boom_id = id_map.get(mrow["boomcode"])
            if boom_id is None:
                meting_skip += 1
                continue

            score = mrow["conditie_score"]
            conn.execute(text("""
                INSERT INTO gws.boom_meting
                    (boom_id, datumtijd, conditie_text, conditie_score)
                VALUES (:boom_id, :dt, :text, :score)
                ON CONFLICT (boom_id, datumtijd) DO UPDATE SET
                    conditie_text  = EXCLUDED.conditie_text,
                    conditie_score = EXCLUDED.conditie_score
            """), {
                "boom_id": boom_id,
                "dt":      mrow["datumtijd"].to_pydatetime(),
                "text":    mrow["conditie_text"],
                "score":   int(score) if score is not None and pd.notna(score) else None,
            })
            meting_ok += 1

        print(f"  Upserted {meting_ok} rows → gws.boom_meting"
              f"  (skipped {meting_skip} unmapped boomcodes)")

    print("Done.")


if __name__ == "__main__":
    main()
