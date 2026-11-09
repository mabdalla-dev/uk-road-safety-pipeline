import pandas as pd
import pytest

from src.transform import transform_collisions


@pytest.fixture
def sample_collisions():

    return pd.DataFrame(
        {
            "collision_index": ["001", "002"],
            "date": ["04/02/2025", "07/05/2025"],
            "collision_severity": [1, 2],
            "day_of_week": [1, 2],
            "weather_conditions": [1, 2],
            "road_surface_conditions": [1, 2],
        }
    )


def test_date_conversion(sample_collisions):

    transformed = transform_collisions(sample_collisions)

    assert pd.api.types.is_datetime64_any_dtype(transformed["date"])

    assert transformed.loc[0, "date"] == pd.Timestamp("2025-02-04")


def test_severity_mapping(sample_collisions):

    transformed = transform_collisions(sample_collisions)

    assert transformed["severity_label"].tolist() == ["Fatal", "Serious"]


def test_day_mapping(sample_collisions):

    transformed = transform_collisions(sample_collisions)

    assert transformed["day_name"].tolist() == ["Sunday", "Monday"]


def test_weather_mapping(sample_collisions):

    transformed = transform_collisions(sample_collisions)

    assert transformed["weather_label"].tolist() == [
        "Fine without high winds",
        "Raining without high winds",
    ]


def test_road_surface_mapping(sample_collisions):

    transformed = transform_collisions(sample_collisions)

    assert transformed["road_surface_label"].tolist() == ["Dry", "Wet or damp"]


def test_original_dataframe_is_not_modified(sample_collisions):

    original_dates = sample_collisions["date"].tolist()

    transform_collisions(sample_collisions)

    assert sample_collisions["date"].tolist() == original_dates

    assert "severity_label" not in sample_collisions.columns


def test_invalid_severity_code_produces_missing_label(sample_collisions):

    sample_collisions.loc[0, "collision_severity"] = 99

    transformed = transform_collisions(sample_collisions)

    assert pd.isna(transformed.loc[0, "severity_label"])
