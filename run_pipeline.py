from pathlib import Path

from src.extract import extract_csv
from src.transform import transform_collisions
from src.validate import validate_collisions, validate_relationships
import pandas as pd
from src.load import load_datasets

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "data" / "processed" / "road_safety.db"

RAW_DIR = BASE_DIR / "data" / "raw"

# Dataset locations
COLLISIONS_PATH = RAW_DIR / "dft-road-casualty-statistics-collision-2025.csv"
VEHICLES_PATH = RAW_DIR / "dft-road-casualty-statistics-vehicle-2025.csv"
CASUALTIES_PATH = RAW_DIR / "dft-road-casualty-statistics-casualty-2025.csv"


def main():

    print("Starting data pipeline...")

    # EXTRACTION
    print("\nExtracting datasets...")

    collisions_raw = extract_csv(COLLISIONS_PATH)
    vehicles_raw = extract_csv(VEHICLES_PATH)
    casualties_raw = extract_csv(CASUALTIES_PATH)

    print("Extraction completed.")

    # TRANSFORMATION
    print("\nTransforming collision dataset...")

    collisions_processed = transform_collisions(collisions_raw)

    print("Transformation completed.")

    # VALIDATION
    print("\nValidating collision dataset...")

    validation_report = validate_collisions(collisions_processed)

    print("\nValidation Report:")

    for check, result in validation_report.items():
        print(f"{check}: {result}")

    # RELATIONSHIP VALIDATION
    print("\nValidating relationships between datasets...")
    relationship_report = validate_relationships(
        collisions_processed, vehicles_raw, casualties_raw
    )

    print("\nRelationship Validation Report:")
    for check, result in relationship_report.items():
        print(f"{check}: {result}")
    # Stop the pipeline if relationship discrepancies are found
    if any(relationship_report.values()):
        raise ValueError(
            "Relationship validation failed. " "Database loading has been aborted."
        )
    print("\nAll relationship checks passed!")

    # LOADING
    print("\nLoading datasets into SQLite...")

    loaded_counts = load_datasets(
        collisions_processed, vehicles_raw, casualties_raw, DB_PATH
    )
    print("\nDatabase summary:")
    for table, count in loaded_counts.items():
        print(f"{table}: {count:,} records")

    print(f"\nDatabase location: {DB_PATH}")

    # RESULTS
    print("\nPipeline results:")

    print(f"Collisions: {len(collisions_processed):,}")
    print(f"Vehicles: {len(vehicles_raw):,}")
    print(f"Casualties: {len(casualties_raw):,}")

    print("\nProcessed collision sample:")

    print(
        collisions_processed[
            ["date", "severity_label", "day_name", "weather_label"]
        ].head()
    )

    print(collisions_raw["date"].dtype)
    print(collisions_processed["date"].dtype)


if __name__ == "__main__":
    main()
