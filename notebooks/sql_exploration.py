from pathlib import Path
import sqlite3
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

DB_PATH = BASE_DIR / "data" / "processed" / "road_safety.db"


connection = sqlite3.connect(DB_PATH)

print("Connected to database successfully!")


query = """
SELECT *
FROM collisions
WHERE collision_severity = 1;
"""


results = pd.read_sql_query(query, connection)

print(results)


query = """
SELECT *
FROM collisions
WHERE speed_limit = 70;
"""


results = pd.read_sql_query(query, connection)

print(results)

query = """
SELECT *
FROM collisions
WHERE day_name = 'Friday'
;
"""


results = pd.read_sql_query(query, connection)

print(results)


query = """
SELECT *
FROM collisions
WHERE collision_severity = 1 AND speed_limit = 30
;
"""


results = pd.read_sql_query(query, connection)

print(results)


query = """
SELECT COUNT(*)
FROM casualties
;
"""


results = pd.read_sql_query(query, connection)

print(results)


query = """
SELECT day_of_week,
COUNT(*) AS total_collisions
FROM collisions
GROUP BY day_of_week
ORDER BY total_collisions DESC
;
"""


results = pd.read_sql_query(query, connection)

print(results)


query = """
SELECT speed_limit,
COUNT(*) AS total_collisions
FROM collisions
GROUP BY speed_limit
ORDER BY total_collisions DESC
LIMIT 5
;
"""


results = pd.read_sql_query(query, connection)

print(results)


query = """
SELECT
    c.collision_index,
    c.date,
    c.severity_label,
    v.vehicle_reference,
    v.vehicle_type
FROM collisions AS c
INNER JOIN vehicles AS v
    ON c.collision_index = v.collision_index
LIMIT 20;
"""


results = pd.read_sql_query(query, connection)

print(results)


query = """
SELECT
    c.collision_index,
    c.date,
    c.severity_label,
    ca.*
FROM collisions AS c
INNER JOIN casualties AS ca
    ON c.collision_index = ca.collision_index
LIMIT 20;
"""


results = pd.read_sql_query(query, connection)


print(results)


query = """
SELECT AVG(number_of_casualties)
FROM collisions;
"""


results = pd.read_sql_query(query, connection)

print(results)
