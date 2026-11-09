import pandas as pd
import pytest

from src.transform import transform_collisions
from src.validate import validate_collisions, validate_relationships


@pytest.fixture
def sample_collisions():

    return pd.DataFrame(
        {
            "collision_index": ["001", "002"],
            "date": ["04/02/2025", "07/05/2025"],
            "collision_severity": [1, 2],
            "number_of_vehicles": [1, 2],
            "number_of_casualties": [1, 1],
            "day_of_week": [1, 2],
            "weather_conditions": [1, 2],
            "road_surface_conditions": [1, 2],
        }
    )


@pytest.fixture
def sample_related_datasets():

    collisions = pd.DataFrame(
        {
            "collision_index": ["C001", "C002"],
            "number_of_vehicles": [2, 1],
            "number_of_casualties": [1, 2],
        }
    )

    vehicles = pd.DataFrame(
        {"collision_index": ["C001", "C001", "C002"], "vehicle_reference": [1, 2, 1]}
    )

    casualties = pd.DataFrame(
        {"collision_index": ["C001", "C002", "C002"], "casualty_reference": [1, 1, 2]}
    )

    return collisions, vehicles, casualties


def run_validation(df):

    transformed = transform_collisions(df)

    return validate_collisions(transformed)


def test_valid_dataset(sample_collisions):

    report = run_validation(sample_collisions)

    assert report["total_records"] == 2

    assert report["missing_collision_ids"] == 0

    assert report["duplicate_collision_ids"] == 0

    assert report["invalid_dates"] == 0

    assert report["invalid_severity_codes"] == 0

    assert report["invalid_day_codes"] == 0

    assert report["invalid_weather_codes"] == 0

    assert report["invalid_road_surface_codes"] == 0

    assert report["invalid_vehicle_counts"] == 0

    assert report["invalid_casualty_counts"] == 0


def test_missing_required_column(sample_collisions):

    transformed = transform_collisions(sample_collisions)

    invalid_data = transformed.drop(columns=["weather_conditions"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_collisions(invalid_data)


def test_missing_collision_ids(sample_collisions):

    sample_collisions.loc[0, "collision_index"] = pd.NA

    report = run_validation(sample_collisions)

    assert report["missing_collision_ids"] == 1


def test_duplicate_collision_ids(sample_collisions):

    sample_collisions.loc[1, "collision_index"] = "001"

    report = run_validation(sample_collisions)

    assert report["duplicate_collision_ids"] == 1


def test_invalid_dates(sample_collisions):

    sample_collisions.loc[0, "date"] = "invalid-date"

    report = run_validation(sample_collisions)

    assert report["invalid_dates"] == 1

    assert report["missing_day_labels"] == 0


def test_invalid_severity_code(sample_collisions):

    sample_collisions.loc[0, "collision_severity"] = 99

    report = run_validation(sample_collisions)

    assert report["invalid_severity_codes"] == 1

    assert report["missing_severity_labels"] == 1


def test_invalid_day_code(sample_collisions):

    sample_collisions.loc[0, "day_of_week"] = 8

    report = run_validation(sample_collisions)

    assert report["invalid_day_codes"] == 1


def test_invalid_weather_code(sample_collisions):

    sample_collisions.loc[0, "weather_conditions"] = 99

    report = run_validation(sample_collisions)

    assert report["invalid_weather_codes"] == 1

    assert report["missing_weather_labels"] == 1


def test_invalid_road_surface_code(sample_collisions):

    sample_collisions.loc[0, "road_surface_conditions"] = 99

    report = run_validation(sample_collisions)

    assert report["invalid_road_surface_codes"] == 1

    assert report["missing_road_surface_labels"] == 1


def test_invalid_vehicle_count(sample_collisions):

    sample_collisions.loc[0, "number_of_vehicles"] = 0

    report = run_validation(sample_collisions)

    assert report["invalid_vehicle_counts"] == 1


def test_invalid_casualty_count(sample_collisions):

    sample_collisions.loc[0, "number_of_casualties"] = 0

    report = run_validation(sample_collisions)

    assert report["invalid_casualty_counts"] == 1


def test_relationship_counts_match(sample_related_datasets):

    collisions, vehicles, casualties = sample_related_datasets

    report = validate_relationships(collisions, vehicles, casualties)

    assert report["vehicle_count_mismatches"] == 0
    assert report["casualty_count_mismatches"] == 0


def test_relationship_count_mismatches(sample_related_datasets):

    collisions, vehicles, casualties = sample_related_datasets

    # Deliberately introduce discrepancies
    collisions.loc[0, "number_of_vehicles"] = 3
    collisions.loc[1, "number_of_casualties"] = 3

    report = validate_relationships(collisions, vehicles, casualties)

    assert report["vehicle_count_mismatches"] == 1
    assert report["casualty_count_mismatches"] == 1


def test_relationships_detect_missing_records(sample_related_datasets):

    collisions, vehicles, casualties = sample_related_datasets

    vehicles = vehicles[vehicles["collision_index"] != "C002"]

    casualties = casualties[casualties["collision_index"] != "C002"]

    report = validate_relationships(collisions, vehicles, casualties)

    assert report["vehicle_count_mismatches"] == 1
    assert report["casualty_count_mismatches"] == 1


def test_relationship_validation_missing_required_column(sample_related_datasets):

    collisions, vehicles, casualties = sample_related_datasets

    collisions = collisions.drop(columns=["number_of_vehicles"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_relationships(collisions, vehicles, casualties)
