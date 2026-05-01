import pandas as pd
import logging
import pathlib

# CONFIG
BASE_DIR      = pathlib.Path(__file__).resolve().parent
DATA_DIR      = BASE_DIR / "data" / "processed"
RAW_DIR       = BASE_DIR / "data" / "raw"

# LOGGING
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def load_csv(path: pathlib.Path) -> pd.DataFrame:
    """Load CSV with error handling for FileNotFoundError and EmptyDataError."""
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise pd.errors.EmptyDataError(f"{path.name} is empty")
        logger.info(f"Loaded '{path.name}' → {len(df)} rows, {len(df.columns)} columns")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except pd.errors.EmptyDataError as e:
        logger.error(str(e))
        raise

def main():
    logger.info("=" * 50)
    logger.info("Starting Data Merging & Analysis Pipeline — Part 2")
    logger.info("=" * 50)

    customers = load_csv(DATA_DIR / "customers_clean.csv")
    orders    = load_csv(DATA_DIR / "orders_clean.csv")
    products  = load_csv(RAW_DIR  / "products.csv")

    # Left-join orders onto customers on customer_id
    orders_with_customers = pd.merge(
        orders,
        customers,
        on="customer_id",
        how="left"
    )
    logger.info(f"Merged orders + customers → {len(orders_with_customers)} rows")

    # Left-join products onto orders_with_customers
    full_data = pd.merge(
        orders_with_customers,
        products,
        left_on="product",
        right_on="product_name",
        how="left"
    )
    logger.info(f"Merged with products → {len(full_data)} rows")

    # Report unmatched rows
    missing_customers = orders_with_customers["name"].isna().sum()
    missing_products  = full_data["product_name"].isna().sum()

    logger.info(f"Order rows with no matching customer: {missing_customers}")
    logger.info(f"Order rows with no matching product:  {missing_products}")


    full_data["order_date"] = pd.to_datetime(full_data["order_date"], errors="coerce")
    completed = full_data[full_data["status"] == "completed"]

    # MONTHLY REVENUE TREND
    monthly_revenue = (
        completed
        .groupby("order_year_month")["amount"]
        .sum()
        .reset_index(name="total_revenue")
        .sort_values("order_year_month")
    )

    out_path = DATA_DIR / "monthly_revenue.csv"
    monthly_revenue.to_csv(out_path, index=False)
    logger.info(f"Saved → {out_path}")

    # TOP CUSTOMERS
    top_customers = (
        completed
        .groupby(["customer_id", "name", "region"])["amount"]
        .sum()
        .reset_index(name="total_spend")
        .sort_values(by="total_spend", ascending=False)
        .head(10)
    )

    latest_date = full_data["order_date"].max()
    cutoff_date = latest_date - pd.Timedelta(days=90)
    logger.info(f"Churn cutoff: {cutoff_date.date()} (90 days before {latest_date.date()})")

    recent_customers = completed[
        completed["order_date"] >= cutoff_date
    ]["customer_id"].unique()

    top_customers["churned"] = ~top_customers["customer_id"].isin(recent_customers)

    out_path = DATA_DIR / "top_customers.csv"
    top_customers.to_csv(out_path, index=False)
    logger.info(f"Saved → {out_path}")

    # CATEGORY PERFORMANCE
    category_performance = (
        completed
        .groupby("category")
        .agg(
            total_revenue=("amount", "sum"),
            avg_order_value=("amount", "mean"),
            num_orders=("amount", "count")
        )
        .reset_index()
    )

    out_path = DATA_DIR / "category_performance.csv"
    category_performance.to_csv(out_path, index=False)
    logger.info(f"Saved → {out_path}")

    # REGIONAL ANALYSIS
    regional_analysis = (
        completed
        .groupby("region")
        .agg(
            num_customers=("customer_id", "nunique"),
            num_orders=("order_id", "count"),
            total_revenue=("amount", "sum")
        )
        .reset_index()
    )

    regional_analysis["avg_revenue_per_customer"] = (
        regional_analysis["total_revenue"] / regional_analysis["num_customers"]
    )

    out_path = DATA_DIR / "regional_analysis.csv"
    regional_analysis.to_csv(out_path, index=False)
    logger.info(f"Saved → {out_path}")

    logger.info("Data Merging & Analysis Pipeline Complete ✓")


if __name__ == "__main__":
    main()
