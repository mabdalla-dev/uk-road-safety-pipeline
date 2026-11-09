from src.extract import extract_csv
import pytest


def test_extract_csv_reads_valid_file(tmp_path):

    # Create a temporary CSV file
    csv_file = tmp_path / "collisions.csv"

    csv_file.write_text(
        "collision_index,collision_year\n00123,2025\n00456,2025\n", encoding="utf-8"
    )

    # Execute the extraction function
    df = extract_csv(csv_file)

    # Verify the results
    assert len(df) == 2

    assert "collision_index" in df.columns

    assert df.loc[0, "collision_index"] == "00123"


def test_extract_csv_missing_file(tmp_path):

    missing_file = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        extract_csv(missing_file)


def test_extract_csv_invalid_extension(tmp_path):

    invalid_file = tmp_path / "collisions.txt"

    invalid_file.write_text("This is not a CSV file", encoding="utf-8")

    with pytest.raises(ValueError):
        extract_csv(invalid_file)
