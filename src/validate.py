import pandas as pd


def validate_collisions(df: pd.DataFrame) -> dict:

    required_columns = {
        "collision_index",
        "date",
        "collision_severity",
        "number_of_vehicles",
        "number_of_casualties",
        "day_of_week",
        "weather_conditions",
        "road_surface_conditions",
    }

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    report = {}

    report["total_records"] = len(df)

    missing_counts = df.isnull().sum()

    report["total_missing_values"] = int(missing_counts.sum())

    report["missing_values_by_column"] = {
        column: int(count) for column, count in missing_counts.items() if count > 0
    }

    report["missing_severity_labels"] = int(df["severity_label"].isnull().sum())
    report["missing_weather_labels"] = int(df["weather_label"].isnull().sum())

    report["missing_road_surface_labels"] = int(df["road_surface_label"].isnull().sum())

    report["missing_day_labels"] = int(df["day_name"].isnull().sum())

    report["missing_collision_ids"] = int(df["collision_index"].isnull().sum())

    report["duplicate_collision_ids"] = int(df["collision_index"].duplicated().sum())

    report["invalid_dates"] = int(df["date"].isnull().sum())

    valid_severities = [1, 2, 3]

    report["invalid_severity_codes"] = int(
        (~df["collision_severity"].isin(valid_severities)).sum()
    )

    valid_days = [1, 2, 3, 4, 5, 6, 7]

    report["invalid_day_codes"] = int((~df["day_of_week"].isin(valid_days)).sum())

    valid_weather = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    report["invalid_weather_codes"] = int(
        (~df["weather_conditions"].isin(valid_weather)).sum()
    )

    valid_road_surfaces = [-1, 1, 2, 3, 4, 5, 9]

    report["invalid_road_surface_codes"] = int(
        (~df["road_surface_conditions"].isin(valid_road_surfaces)).sum()
    )

    report["invalid_vehicle_counts"] = int((df["number_of_vehicles"] < 1).sum())

    report["invalid_casualty_counts"] = int((df["number_of_casualties"] < 1).sum())

    return report


def validate_relationships(collisions, vehicles, casualties):

    required_columns = {
        "collision_index",
        "number_of_vehicles",
        "number_of_casualties",
    }

    missing_columns = required_columns - set(collisions.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    # Count actual vehicles per collision
    vehicle_counts = (
        vehicles.groupby("collision_index").size().rename("actual_vehicles")
    )

    # Count actual casualties per collision
    casualty_counts = (
        casualties.groupby("collision_index").size().rename("actual_casualties")
    )

    # Compare actual counts with declared counts
    reconciliation = (
        collisions.set_index("collision_index")[
            ["number_of_vehicles", "number_of_casualties"]
        ]
        .join(vehicle_counts)
        .join(casualty_counts)
    )

    # Replace missing counts with zero
    reconciliation["actual_vehicles"] = reconciliation["actual_vehicles"].fillna(0)

    reconciliation["actual_casualties"] = reconciliation["actual_casualties"].fillna(0)

    # Identify mismatches
    vehicle_mismatches = (
        reconciliation["number_of_vehicles"] != reconciliation["actual_vehicles"]
    )

    casualty_mismatches = (
        reconciliation["number_of_casualties"] != reconciliation["actual_casualties"]
    )

    return {
        "vehicle_count_mismatches": int(vehicle_mismatches.sum()),
        "casualty_count_mismatches": int(casualty_mismatches.sum()),
    }
