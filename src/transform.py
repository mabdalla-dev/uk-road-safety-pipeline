import pandas as pd

# Mapping dictionaries
SEVERITY_MAP = {1: "Fatal", 2: "Serious", 3: "Slight"}

DAY_MAP = {
    1: "Sunday",
    2: "Monday",
    3: "Tuesday",
    4: "Wednesday",
    5: "Thursday",
    6: "Friday",
    7: "Saturday",
}

WEATHER_MAP = {
    1: "Fine without high winds",
    2: "Raining without high winds",
    3: "Snowing without high winds",
    4: "Fine with high winds",
    5: "Raining with high winds",
    6: "Snowing with high winds",
    7: "Fog or mist",
    8: "Other",
    9: "Unknown",
}

ROAD_SURFACE_MAP = {
    1: "Dry",
    2: "Wet or damp",
    3: "Snow",
    4: "Frost or ice",
    5: "Flooding",
    9: "Unknown",
    -1: "Data missing or out of range",
}


def transform_collisions(df: pd.DataFrame) -> pd.DataFrame:

    transformed = df.copy()

    # Convert date column into datetime format
    transformed["date"] = pd.to_datetime(
        transformed["date"], format="%d/%m/%Y", errors="coerce"
    )

    # Map categorical codes into readable descriptions
    transformed["severity_label"] = transformed["collision_severity"].map(SEVERITY_MAP)

    transformed["day_name"] = transformed["day_of_week"].map(DAY_MAP)

    transformed["weather_label"] = transformed["weather_conditions"].map(WEATHER_MAP)

    transformed["road_surface_label"] = transformed["road_surface_conditions"].map(
        ROAD_SURFACE_MAP
    )

    return transformed
