import pandas as pd
from fastapi import HTTPException
from backend.config.settings import CSV_FILES


def load_csv_data(name: str) -> list[dict]:
    path = CSV_FILES.get(name)
    if path is None:
        raise HTTPException(status_code=404, detail=f"Unknown dataset: '{name}'")

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Data file not found: '{path.name}'. Run the analysis pipeline first.",
        )

    try:
        df = pd.read_csv(path)
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"Data file is empty: '{path.name}'.",
            )
        # Replace NaN with None for clean JSON serialization
        df = df.where(df.notna(), None)
        return df.to_dict(orient="records")
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=404,
            detail=f"Data file is empty: '{path.name}'.",
        )
