import pandas as pd
import numpy as np
import logging
import warnings
import pathlib

warnings.filterwarnings("ignore")

# CONFIG
BASE_DIR      = pathlib.Path(__file__).resolve().parent
RAW_DIR       = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# LOGGING
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# STATUS NORMALIZATION MAP
STATUS_MAP = {
    "completed": "completed", "complete": "completed", "done": "completed",
    "DONE": "completed", "COMPLETED": "completed", "Complete": "completed", "Done": "completed",
    "pending": "pending", "Pending": "pending", "PENDING": "pending",
    "in progress": "pending", "In Progress": "pending", "waiting": "pending", "Waiting": "pending",
    "cancelled": "cancelled", "Cancelled": "cancelled", "CANCELLED": "cancelled",
    "canceled": "cancelled", "Canceled": "cancelled", "CANCELED": "cancelled", "cancel": "cancelled",
    "refunded": "refunded", "Refunded": "refunded", "REFUNDED": "refunded",
    "refund": "refunded", "Refund": "refunded", "money back": "refunded",
}

def load_csv(filepath: pathlib.Path) -> pd.DataFrame:
    """Load CSV with error handling."""
    try:
        df = pd.read_csv(filepath)
        if df.empty:
            raise pd.errors.EmptyDataError(f"{filepath.name} is empty.")
        logger.info(f"Loaded '{filepath.name}' → {len(df)} rows, {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except pd.errors.EmptyDataError as e:
        logger.error(str(e))
        raise


def is_valid_email(email) -> bool:
    """Return True if email contains '@' and '.'."""
    if pd.isna(email) or str(email).strip() == "":
        return False
    return "@" in str(email) and "." in str(email)


def parse_date_safe(val):
    """Parse date from multiple formats; return NaT and log warning if unparseable."""
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]:
        try:
            return pd.to_datetime(val, format=fmt)
        except (ValueError, TypeError):
            pass
    logger.warning(f"Unparseable date: '{val}' → NaT")
    return pd.NaT


def normalize_status(val):
    """Map messy status values to controlled vocabulary."""
    if pd.isna(val):
        return np.nan
    return STATUS_MAP.get(str(val).strip().lower(), np.nan)


def print_cleaning_report(name, before, after, dupes_removed):
    """Print a cleaning summary to stdout."""
    sep = "=" * 62
    print(f"\n{sep}")
    print(f"  CLEANING REPORT — {name}")
    print(sep)
    print(f"  Rows before cleaning   : {len(before)}")
    print(f"  Duplicate rows removed : {dupes_removed}")
    print(f"  Rows after cleaning    : {len(after)}")
    print(f"\n  NULL COUNTS PER COLUMN (before → after):")
    print(f"  {'Column':<22} {'Before':>8} {'After':>8}")
    print(f"  {'-'*40}")
    for col in before.columns:
        b = before[col].isna().sum()
        a = after[col].isna().sum() if col in after.columns else "N/A"
        print(f"  {col:<22} {b:>8} {str(a):>8}")
    print(f"{sep}\n")


# CLEAN customers.csv

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    original_df   = df.copy()

    # Strip whitespace from name and region
    df["name"]    = df["name"].astype(str).str.strip()
    df["region"]  = df["region"].astype(str).str.strip()

    # Replace empty strings with NaN
    df.replace("", np.nan, inplace=True)

    # Parse signup_date safely
    df["signup_date"] = df["signup_date"].apply(parse_date_safe)

    # Remove duplicates — keep most recent signup_date
    before_dedup  = len(df)
    df = df.sort_values("signup_date", ascending=False, na_position="last")
    df = df.drop_duplicates(subset=["customer_id"], keep="first")
    df = df.sort_values("customer_id").reset_index(drop=True)
    dupes_removed = before_dedup - len(df)
    logger.info(f"[customers] Duplicates removed: {dupes_removed}")

    # Format date → YYYY-MM-DD
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")

    df["email"] = df["email"].astype(str).str.lower().str.strip()
    df["email"] = df["email"].replace("nan", np.nan)

    # Flag invalid/missing emails
    df["is_valid_email"] = df["email"].apply(is_valid_email)
    logger.info(f"[customers] Invalid/missing emails flagged: {(~df['is_valid_email']).sum()}")

    # Fill missing region with 'Unknown'
    df["region"] = df["region"].replace("nan", np.nan)
    missing_region = df["region"].isna().sum()
    df["region"] = df["region"].fillna("Unknown")
    logger.info(f"[customers] Missing regions filled: {missing_region}")

    print_cleaning_report("customers.csv", original_df, df, dupes_removed)
    return df


# CLEAN orders.csv

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    original_df = df.copy()

    df.replace("", np.nan, inplace=True)

    before_drop = len(df)
    df = df.dropna(subset=["order_id", "customer_id"], how="all")
    dropped = before_drop - len(df)
    logger.info(f"[orders] Unrecoverable rows dropped (both IDs null): {dropped}")

    # Parse order_date with custom multi-format parser
    df["order_date"] = df["order_date"].apply(parse_date_safe)

    missing_amount = df["amount"].isna().sum()
    df["amount"]   = pd.to_numeric(df["amount"], errors="coerce")
    df["amount"]   = df.groupby("product")["amount"].transform(
        lambda x: x.fillna(x.median())
    )

    df["amount"]   = df["amount"].fillna(df["amount"].median())
    logger.info(f"[orders] Missing amounts filled: {missing_amount}")

    df["status"] = df["status"].apply(normalize_status)
    logger.info("[orders] Status column normalized to controlled vocabulary.")

    # Add derived column order_year_month (YYYY-MM)
    df["order_year_month"] = df["order_date"].dt.strftime("%Y-%m")
    logger.info("[orders] Added derived column: order_year_month")

    # 7Format order_date → YYYY-MM-DD
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")

    print_cleaning_report("orders.csv", original_df, df, dupes_removed=0)
    return df

def main():
    logger.info("=" * 50)
    logger.info("Starting Data Cleaning Pipeline — Part 1")
    logger.info("=" * 50)

    # Load
    customers_raw = load_csv(RAW_DIR / "customers.csv")
    orders_raw    = load_csv(RAW_DIR / "orders.csv")

    # Clean
    customers_clean = clean_customers(customers_raw)
    orders_clean    = clean_orders(orders_raw)

    # Save
    cust_out  = PROCESSED_DIR / "customers_clean.csv"
    order_out = PROCESSED_DIR / "orders_clean.csv"
    customers_clean.to_csv(cust_out,  index=False)
    orders_clean.to_csv(order_out,    index=False)

    logger.info(f"Saved → {cust_out}")
    logger.info(f"Saved → {order_out}")
    logger.info("Data Cleaning Pipeline Complete ✓")


if __name__ == "__main__":
    main()