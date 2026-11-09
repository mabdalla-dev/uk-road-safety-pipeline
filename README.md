# UK Road Safety ETL Pipeline

![Python CI](https://github.com/mabdalla-dev/uk-road-safety-pipeline/actions/workflows/tests.yml/badge.svg)

An end-to-end Python ETL pipeline that processes UK road safety data from the Department for Transport (DfT), performs data quality validation, and loads related datasets into a relational SQLite database.

The project demonstrates practical data engineering concepts including data extraction, transformation, validation, relational database design, automated testing and SQL analysis.

## Project Overview

This project uses the 2025 STATS19 road safety datasets, which contain information about road collisions, vehicles involved and casualties.

The pipeline extracts the three datasets, processes and validates the data, and loads the resulting datasets into a relational SQLite database.

### Key Features

- Extracting multiple CSV datasets using Python and pandas.
- Transforming dates and mapping coded values into descriptive labels.
- Validating data quality, primary keys and referential integrity.
- Creating relational SQLite tables with primary and foreign key constraints.
- Loading datasets into SQLite using pandas.
- Executing SQL queries to analyze road collision data.
- Automated testing using pytest.
- Code coverage measurement using pytest-cov.

## Technology Stack

| Technology | Purpose                            |
| ---------- | ---------------------------------- |
| Python     | Pipeline development               |
| Pandas     | Data extraction and transformation |
| SQLite     | Relational database storage        |
| SQL        | Data querying and analysis         |
| pytest     | Automated testing                  |
| pytest-cov | Test coverage reporting            |
| Git        | Version control                    |

## Pipeline Architecture

The pipeline follows an Extract, Transform, Load (ETL) structure.

```text
        DfT STATS19 CSV Datasets
                   |
                   v
             EXTRACTION
              extract.py
                   |
                   v
            TRANSFORMATION
              transform.py
                   |
                   v
              VALIDATION
              validate.py
                   |
                   v
                 LOADING
                load.py
                   |
                   v
             SQLite Database
             road_safety.db
                   |
                   v
             SQL Exploration
```

### 1. Extraction

The extraction module reads the three source CSV files:

- Collisions
- Vehicles
- Casualties

### 2. Transformation

The transformation stage processes the data, including:

- Converting date columns into datetime values.
- Mapping collision severity codes to descriptive labels.
- Mapping day-of-week codes to day names.
- Mapping weather condition codes to descriptive labels.
- Mapping road surface condition codes to descriptive labels.

Currently, descriptive transformations are applied to the collision dataset. The vehicle and casualty datasets retain their original fields and coded values during loading.

### 3. Validation

The validation stage performs data quality checks before loading.

Collision validation includes:

- Missing required columns.
- Missing and duplicate collision identifiers.
- Invalid dates.
- Invalid categorical codes.
- Invalid vehicle and casualty counts.
- Missing descriptive labels.

Cross-dataset relationship validation checks:

- Actual vehicle counts against declared vehicle counts.
- Actual casualty counts against declared casualty counts.

These checks help identify inconsistencies between the collision, vehicle and casualty datasets.

Database-level integrity checks are also performed during loading using primary key and foreign key constraints.

### 4. Loading

The loading module creates and populates three relational SQLite tables.

It includes:

- Builds a temporary database and replaces the existing database only after successful loading and integrity checks.
- Automatic SQLite column type selection.
- Primary key and foreign key constraints.
- Primary key validation before loading.
- Foreign key enforcement.
- Foreign key integrity checks after loading.
- Database record-count verification.

## Database Design

The project stores the three datasets in separate relational tables.

| Table      | Primary Key                         |
| ---------- | ----------------------------------- |
| collisions | collision_index                     |
| vehicles   | collision_index, vehicle_reference  |
| casualties | collision_index, casualty_reference |

### Relationships

- Each vehicle record references a collision.
- Each casualty record references a collision.
- Each casualty record references a vehicle through the composite vehicle key.

These relationships are enforced using SQLite foreign key constraints.

## Dataset

The project uses the Department for Transport's 2025 STATS19 road safety open data.

Source: [Department for Transport – Road Safety Open Data](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data)

The three datasets contain information about personal injury road collisions reported to the police, the vehicles involved and the resulting casualties.

### Data Profile

The following figures represent the datasets processed during development.

| Dataset    | Records |
| ---------- | ------: |
| Collisions | 101,525 |
| Vehicles   | 183,948 |
| Casualties | 127,883 |

Eight missing values were identified in the collision dataset, all relating to geographical coordinate fields.

The relationship checks confirmed that vehicle and casualty records matched their corresponding collision records in the processed datasets.

**Note:** The raw datasets and generated SQLite database are not committed to this repository. They can be downloaded and regenerated locally.

## SQL Analysis

SQL queries are used to explore the processed data.

Examples include:

- Identifying fatal collisions.
- Filtering collisions by speed limit.
- Analysing collisions by day of the week.
- Counting total casualties.
- Grouping collisions by speed limit.
- Joining collision, vehicle and casualty tables.
- Calculating average casualties per collision.

SQL exploration is documented in `notebooks/sql_exploration.py`.

## Automated Testing

The project uses pytest to test individual pipeline components.

The current test suite contains 37 automated tests, achieving 100% statement coverage across the `src` modules.

Test coverage includes:

- CSV extraction and file handling.
- Data transformations and mapping.
- Data validation and error handling.
- SQLite database creation and loading.
- Primary key and foreign key integrity.
- Database error handling.

Code coverage is measured using pytest-cov.

The latest local coverage report achieved **100% statement coverage across the `src` modules**.

Run the tests:

```bash
python -m pytest -v
```

Run tests with coverage:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

Generate an HTML coverage report:

```bash
python -m pytest --cov=src --cov-report=html
```

Open `htmlcov/index.html` to inspect the report.

## Project Structure

```text
uk-road-safety-pipeline/
│
├── data/
│   ├── raw/                  # Downloaded source CSV files
│   └── processed/            # Generated SQLite database
│
├── notebooks/
│   ├── day1_exploration.py
│   └── sql_exploration.py
│
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   └── load.py
│
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   ├── test_validate.py
│   └── test_load.py
│
├── run_pipeline.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd uk-road-safety-pipeline
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Download the datasets

Download the 2025 collision, vehicle and casualty CSV files from the Department for Transport's [Road Safety Open Data page](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data).

Place the three files in:

```text
data/raw/
```

Use the following filenames:

```text
dft-road-casualty-statistics-collision-2025.csv
dft-road-casualty-statistics-vehicle-2025.csv
dft-road-casualty-statistics-casualty-2025.csv
```

### 5. Run the pipeline

From the project root:

```bash
python run_pipeline.py
```

The pipeline processes the datasets, performs validation and creates the SQLite database at:

```text
data/processed/road_safety.db
```

### 6. Run the tests

```bash
python -m pytest -v
```

## Future Improvements

Potential extensions to the project include:

- Automated CI testing using GitHub Actions.
- Advanced SQL analysis using CTEs and window functions.
- Implementing a distributed processing version using PySpark.
- Storing processed datasets in Parquet format.
- Exploring data partitioning and scalable storage techniques.

## Data Limitations

The STATS19 dataset records personal injury collisions on public roads that are reported to the police. It does not represent every road collision or incident.

Results should therefore be interpreted within the limitations of the underlying data collection process.
