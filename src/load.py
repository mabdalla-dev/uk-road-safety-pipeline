from pathlib import Path
import sqlite3

import pandas as pd
import os
import tempfile

from pandas.api.types import is_bool_dtype, is_integer_dtype, is_float_dtype


def get_sqlite_type(series):

    dtype = series.dtype

    if is_bool_dtype(dtype):
        return "INTEGER"

    if is_integer_dtype(dtype):
        return "INTEGER"

    if is_float_dtype(dtype):
        return "REAL"

    return "TEXT"


def prepare_for_sql(df):

    prepared = df.copy()

    for column in prepared.columns:

        if pd.api.types.is_datetime64_any_dtype(prepared[column]):
            prepared[column] = prepared[column].dt.strftime("%Y-%m-%d")

    return prepared


def create_table(connection, table_name, df, primary_key, foreign_keys=None):

    if foreign_keys is None:
        foreign_keys = []

    column_definitions = []

    for column in df.columns:

        column_type = get_sqlite_type(df[column])

        column_definitions.append(f'"{column}" {column_type}')

    constraints = []

    # Define primary key
    primary_key_columns = ", ".join(f'"{column}"' for column in primary_key)

    constraints.append(f"PRIMARY KEY ({primary_key_columns})")

    # Define foreign keys
    for local_columns, referenced_table, referenced_columns in foreign_keys:

        local = ", ".join(f'"{column}"' for column in local_columns)

        referenced = ", ".join(f'"{column}"' for column in referenced_columns)

        constraints.append(
            f"FOREIGN KEY ({local}) " f'REFERENCES "{referenced_table}" ({referenced})'
        )

    all_definitions = column_definitions + constraints

    sql = f'CREATE TABLE "{table_name}" ' f'({", ".join(all_definitions)})'

    connection.execute(sql)


def load_datasets(collisions, vehicles, casualties, db_path):

    db_path = Path(db_path)

    # Create the database directory if it doesn't exist
    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Prepare datasets
    collisions = prepare_for_sql(collisions)
    vehicles = prepare_for_sql(vehicles)
    casualties = prepare_for_sql(casualties)

    # Define primary keys
    primary_keys = {
        "collisions": ["collision_index"],
        "vehicles": ["collision_index", "vehicle_reference"],
        "casualties": ["collision_index", "casualty_reference"],
    }

    datasets = {
        "collisions": collisions,
        "vehicles": vehicles,
        "casualties": casualties,
    }

    # Check primary keys before loading
    for table_name, df in datasets.items():

        key_columns = primary_keys[table_name]

        if df[key_columns].isnull().any().any():
            raise ValueError(f"Missing primary key values in {table_name}")

        if df.duplicated(subset=key_columns).any():
            raise ValueError(f"Duplicate primary keys in {table_name}")

    # Create a temporary database in the same directory
    temp_fd, temp_name = tempfile.mkstemp(
        prefix=f"{db_path.stem}_", suffix=".tmp", dir=db_path.parent
    )

    os.close(temp_fd)

    temp_db_path = Path(temp_name)

    connection = None

    try:

        # Connect to the temporary database
        connection = sqlite3.connect(temp_db_path)

        # Enable foreign key enforcement
        connection.execute("PRAGMA foreign_keys = ON")

        enabled = connection.execute("PRAGMA foreign_keys").fetchone()[0]

        if enabled != 1:
            raise RuntimeError("Foreign key enforcement is disabled")

        # Create tables in dependency order
        create_table(connection, "collisions", collisions, ["collision_index"])

        create_table(
            connection,
            "vehicles",
            vehicles,
            ["collision_index", "vehicle_reference"],
            [(["collision_index"], "collisions", ["collision_index"])],
        )

        create_table(
            connection,
            "casualties",
            casualties,
            ["collision_index", "casualty_reference"],
            [
                (["collision_index"], "collisions", ["collision_index"]),
                (
                    ["collision_index", "vehicle_reference"],
                    "vehicles",
                    ["collision_index", "vehicle_reference"],
                ),
            ],
        )

        # Load data into tables
        for table_name, df in datasets.items():

            df.to_sql(
                table_name, connection, if_exists="append", index=False, chunksize=5000
            )

            print(f"Loaded {len(df):,} records into {table_name}")

        # Check foreign key integrity
        foreign_key_errors = connection.execute("PRAGMA foreign_key_check").fetchall()

        if foreign_key_errors:
            raise ValueError(f"Foreign key violations: {foreign_key_errors[:10]}")

        # Verify table counts
        row_counts = {}

        for table_name in datasets:

            count = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()[0]

            row_counts[table_name] = count

        connection.commit()

        # Close connection before replacing the database
        connection.close()
        connection = None

        # Atomically replace the original database
        os.replace(temp_db_path, db_path)

        print("\nDatabase loading completed successfully!")

        return row_counts

    except Exception:

        if connection is not None:
            connection.rollback()

        raise

    finally:

        if connection is not None:
            connection.close()

        # Remove temporary database if loading failed
        if temp_db_path.exists():
            temp_db_path.unlink()
