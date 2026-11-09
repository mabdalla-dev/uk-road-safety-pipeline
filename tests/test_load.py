import sqlite3

import pandas as pd
import pytest
import src.load as load_module

from contextlib import closing

from src.load import load_datasets, get_sqlite_type


@pytest.fixture
def sample_datasets():

    collisions = pd.DataFrame(
        {
            "collision_index": ["C001", "C002"],
            "collision_year": [2025, 2025],
            "date": pd.to_datetime(["2025-01-01", "2025-01-02"]),
            "number_of_vehicles": [2, 1],
            "number_of_casualties": [2, 1],
        }
    )

    vehicles = pd.DataFrame(
        {
            "collision_index": ["C001", "C001", "C002"],
            "vehicle_reference": [1, 2, 1],
            "vehicle_type": [2, 9, 2],
        }
    )

    casualties = pd.DataFrame(
        {
            "collision_index": ["C001", "C001", "C002"],
            "vehicle_reference": [1, 2, 1],
            "casualty_reference": [1, 2, 1],
            "casualty_severity": [3, 2, 3],
        }
    )

    return collisions, vehicles, casualties


def test_successful_database_loading(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    db_path = tmp_path / "road_safety.db"

    counts = load_datasets(collisions, vehicles, casualties, db_path)

    assert db_path.exists()

    assert counts == {"collisions": 2, "vehicles": 3, "casualties": 3}


# Verify records exist in SQLite
def test_database_contains_correct_records(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    db_path = tmp_path / "road_safety.db"

    load_datasets(collisions, vehicles, casualties, db_path)

    with closing(sqlite3.connect(db_path)) as connection:

        collision_count = connection.execute(
            "SELECT COUNT(*) FROM collisions"
        ).fetchone()[0]

        vehicle_count = connection.execute("SELECT COUNT(*) FROM vehicles").fetchone()[
            0
        ]

        casualty_count = connection.execute(
            "SELECT COUNT(*) FROM casualties"
        ).fetchone()[0]

    assert collision_count == 2
    assert vehicle_count == 3
    assert casualty_count == 3


# Verify dates are being stored correctly
def test_dates_are_stored_correctly(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    db_path = tmp_path / "road_safety.db"

    load_datasets(collisions, vehicles, casualties, db_path)

    with closing(sqlite3.connect(db_path)) as connection:

        result = connection.execute("""
            SELECT date
            FROM collisions
            WHERE collision_index = 'C001'
            """).fetchone()

    assert result[0] == "2025-01-01"


# Verify rejection of duplicate primary keys
def test_duplicate_vehicle_primary_key_rejected(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    duplicate_vehicle = pd.concat([vehicles, vehicles.iloc[[0]]], ignore_index=True)

    db_path = tmp_path / "road_safety.db"

    with pytest.raises(ValueError, match="Duplicate primary keys in vehicles"):

        load_datasets(collisions, duplicate_vehicle, casualties, db_path)


# Verify rejection of missing primary keys
def test_missing_primary_key_rejected(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    collisions.loc[0, "collision_index"] = pd.NA

    db_path = tmp_path / "road_safety.db"

    with pytest.raises(ValueError, match="Missing primary key values in collisions"):

        load_datasets(collisions, vehicles, casualties, db_path)


# Verify invalid foreign keys are rejected
def test_invalid_vehicle_foreign_key_rejected(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    invalid_vehicle = pd.DataFrame(
        {"collision_index": ["C999"], "vehicle_reference": [1], "vehicle_type": [2]}
    )

    vehicles = pd.concat([vehicles, invalid_vehicle], ignore_index=True)

    db_path = tmp_path / "road_safety.db"

    with pytest.raises(pd.errors.DatabaseError) as exc_info:

        load_datasets(collisions, vehicles, casualties, db_path)

    assert isinstance(exc_info.value.__cause__, sqlite3.IntegrityError)


# Verify invalid relationships between tables are rejected
def test_invalid_casualty_vehicle_reference_rejected(sample_datasets, tmp_path):
    collisions, vehicles, casualties = sample_datasets

    invalid_casualty = pd.DataFrame(
        {
            "collision_index": ["C001"],
            "vehicle_reference": [99],
            "casualty_reference": [99],
            "casualty_severity": [3],
        }
    )

    casualties = pd.concat([casualties, invalid_casualty], ignore_index=True)

    db_path = tmp_path / "road_safety.db"

    with pytest.raises(pd.errors.DatabaseError) as exc_info:
        load_datasets(collisions, vehicles, casualties, db_path)

    assert isinstance(exc_info.value.__cause__, sqlite3.IntegrityError)


# Verify reloading the database does not duplicate records
def test_reloading_database_does_not_duplicate_records(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    db_path = tmp_path / "road_safety.db"

    first_run = load_datasets(collisions, vehicles, casualties, db_path)

    second_run = load_datasets(collisions, vehicles, casualties, db_path)

    assert first_run == second_run

    assert second_run == {"collisions": 2, "vehicles": 3, "casualties": 3}


def test_get_sqlite_type_boolean():
    series = pd.Series([True, False])

    assert get_sqlite_type(series) == "INTEGER"


def test_get_sqlite_type_float():
    series = pd.Series([1.5, 2.5])

    assert get_sqlite_type(series) == "REAL"


def test_load_datasets_raises_when_foreign_keys_disabled(tmp_path, monkeypatch):

    class FakeCursor:

        def fetchone(self):
            return (0,)

    class FakeConnection:

        def execute(self, query):
            return FakeCursor()

        def rollback(self):
            pass

        def close(self):
            pass

    fake_connection = FakeConnection()

    monkeypatch.setattr(load_module.sqlite3, "connect", lambda db_path: fake_connection)

    collisions = pd.DataFrame({"collision_index": ["C1"]})

    vehicles = pd.DataFrame({"collision_index": ["C1"], "vehicle_reference": [1]})

    casualties = pd.DataFrame({"collision_index": ["C1"], "casualty_reference": [1]})

    with pytest.raises(RuntimeError, match="Foreign key enforcement is disabled"):

        load_datasets(collisions, vehicles, casualties, tmp_path / "test.db")


def test_load_datasets_raises_on_foreign_key_violations(tmp_path, monkeypatch):

    class FakeCursor:

        def fetchone(self):
            return (1,)

        def fetchall(self):
            return [("casualties", 1, "vehicles", 0)]

    class FakeConnection:

        def execute(self, query):
            return FakeCursor()

        def rollback(self):
            pass

        def close(self):
            pass

    fake_connection = FakeConnection()

    monkeypatch.setattr(load_module.sqlite3, "connect", lambda db_path: fake_connection)

    # Prevent pandas from attempting to load data into our fake connection.
    monkeypatch.setattr(pd.DataFrame, "to_sql", lambda self, *args, **kwargs: None)

    collisions = pd.DataFrame({"collision_index": ["C1"]})

    vehicles = pd.DataFrame({"collision_index": ["C1"], "vehicle_reference": [1]})

    casualties = pd.DataFrame(
        {"collision_index": ["C1"], "casualty_reference": [1], "vehicle_reference": [1]}
    )

    with pytest.raises(ValueError, match="Foreign key violations"):

        load_datasets(collisions, vehicles, casualties, tmp_path / "test.db")


def test_failed_reload_preserves_existing_database(sample_datasets, tmp_path):

    collisions, vehicles, casualties = sample_datasets

    db_path = tmp_path / "road_safety.db"

    # First load: create a valid database
    original_counts = load_datasets(collisions, vehicles, casualties, db_path)

    # Introduce a vehicle referencing a nonexistent collision
    invalid_vehicle = pd.DataFrame(
        {"collision_index": ["C999"], "vehicle_reference": [1], "vehicle_type": [2]}
    )

    vehicles_with_invalid_record = pd.concat(
        [vehicles, invalid_vehicle], ignore_index=True
    )

    # Second load should fail
    with pytest.raises((pd.errors.DatabaseError, sqlite3.IntegrityError)):

        load_datasets(collisions, vehicles_with_invalid_record, casualties, db_path)

    # Check that the original database remains intact
    with closing(sqlite3.connect(db_path)) as connection:

        current_counts = {}

        for table in ["collisions", "vehicles", "casualties"]:

            count = connection.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]

            current_counts[table] = count

    assert current_counts == original_counts
