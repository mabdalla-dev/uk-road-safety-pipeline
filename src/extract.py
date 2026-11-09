from pathlib import Path
import pandas as pd


def extract_csv(file_path: str | Path) -> pd.DataFrame:

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    if path.suffix.lower() != ".csv":
        raise ValueError("The provided file must be a CSV")

    df = pd.read_csv(path, dtype={"collision_index": "string"}, low_memory=False)

    return df
