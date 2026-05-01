import pathlib

BASE_DIR     = pathlib.Path(__file__).resolve().parent.parent.parent
DATA_DIR     = BASE_DIR / "data" / "processed"

CSV_FILES = {
    "monthly_revenue":      DATA_DIR / "monthly_revenue.csv",
    "top_customers":        DATA_DIR / "top_customers.csv",
    "category_performance": DATA_DIR / "category_performance.csv",
    "regional_analysis":    DATA_DIR / "regional_analysis.csv",
}
