import pandas as pd

collisions = pd.read_csv(
    "data/raw/dft-road-casualty-statistics-collision-2025.csv"
)

casualties = pd.read_csv(
    "data/raw/dft-road-casualty-statistics-casualty-2025.csv"
)

severity_map = {
    1: "Fatal",
    2: "Serious",
    3: "Slight"
}

day_map = {
    1: "Sunday",
    2: "Monday",
    3: "Tuesday",
    4: "Wednesday",
    5: "Thursday",
    6: "Friday",
    7: "Saturday"
}

weather_map = {
    1: "Fine without high winds",
    2: "Raining without high winds",
    3: "Snowing without high winds",
    4: "Fine with high winds",
    5: "Raining with high winds",
    6: "Snowing with high winds",
    7: "Fog or mist",
    8: "Other",
    9: "Unknown"
}

road_surface_map = {
    1: "Dry",
    2: "Wet or damp",
    3: "Snow",
    4: "Frost or ice",
    5: "Flooding",
    9: "Unknown",
    -1: "Data missing or out of range"
}


collisions["severity_label"] = collisions["collision_severity"].map(severity_map)
collisions["day_name"] = collisions["day_of_week"].map(day_map)
collisions["weather_label"] = collisions["weather_conditions"].map(weather_map)
collisions["road_surface_label"] = collisions["road_surface_conditions"].map(road_surface_map)

print(collisions.dtypes)

print(collisions["date"].dtype)

print(collisions["collision_severity"].dtype)

print(collisions["number_of_vehicles"].dtype)

print(collisions["date"].head(10))


dates = pd.to_datetime(
    collisions["date"],
    dayfirst=True,
    errors="coerce"
)

print(dates.head(10))

print("Earliest date:", dates.min())
print("Latest date:", dates.max())
print("Invalid dates:", dates.isnull().sum())

print(collisions["collision_severity"].unique())

print(collisions["day_of_week"].unique())

print(collisions["weather_conditions"].unique())

print(collisions["road_surface_conditions"].unique())

print(collisions["weather_conditions"].value_counts(dropna=False))
print(collisions["day_of_week"].value_counts(dropna=False))
print(collisions["road_surface_conditions"].value_counts(dropna=False))
print(collisions["collision_severity"].value_counts(dropna=False))


print(
    collisions[
        ["number_of_vehicles",
         "number_of_casualties",
         "speed_limit"]
    ].describe()
)


collisions_by_day_of_week = collisions.groupby("day_of_week").size()
print(collisions_by_day_of_week)


print(collisions[["collision_severity", "severity_label"]].head(10))

print(collisions["day_name"].value_counts())

print(collisions["weather_label"].value_counts())

print(collisions["road_surface_label"].value_counts())



print(
    collisions[
        collisions["number_of_casualties"] > 20
    ][
        ["collision_index", "date", "number_of_casualties", "collision_severity"]
    ]
)

target = collisions[
    collisions["collision_index"] == "2025052501204"
]

print(target.T)

target_casualties = casualties[
    casualties["collision_index"] == "2025052501204"
]

print(target_casualties.shape)

print(target_casualties.head(20))

print(target_casualties["casualty_reference"].nunique())
print(target_casualties["casualty_reference"].duplicated().sum())
print(
    target_casualties["casualty_severity"].value_counts()
)


reported_casualties = int(target["number_of_casualties"].iloc[0])

actual_casualty_records = len(target_casualties)

print("Collision dataset:", reported_casualties)

print("Casualties dataset:", actual_casualty_records)

print("Counts match:", reported_casualties == actual_casualty_records)