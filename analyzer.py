import logging
import pandas as pd

logger = logging.getLogger(__name__)


def analyze_basic(df: pd.DataFrame) -> None:
    """
    Basic structure and quality check.
    """
    logger.info("Starting basic analysis...")
    logger.debug(f"Data shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    print("=== Basic Information ===")
    print(f"Rows × Columns: {df.shape[0]} × {df.shape[1]}")
    print("\nColumn names:")
    print(list(df.columns))
    
    missing_values = df.isna().sum()
    total_missing = missing_values.sum()
    if total_missing > 0:
        logger.warning(f"Found {total_missing} missing values")
    else:
        logger.info("Data is complete, no missing values")
    
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nMissing values statistics:")
    print(missing_values)
    print("\nDescriptive statistics:")
    print(df.describe(include="all"))
    
    logger.info("Basic analysis completed")


def analyze_trend(df: pd.DataFrame) -> None:
    """
    Annual sales and price trend analysis (using actual columns: Year, Price_USD, Sales_Volume).
    """
    logger.info("Starting trend analysis...")
    cols = set(df.columns)

    print("\n=== Annual Sales Trend (Sales_Volume) ===")
    if {"Year", "Sales_Volume"}.issubset(cols):
        logger.debug("Performing annual sales aggregation...")
        yearly_vol = (
            df.groupby("Year")["Sales_Volume"]
            .sum()
            .reset_index()
            .sort_values("Year")
        )
        yearly_vol.rename(columns={"Sales_Volume": "Total_Sales_Volume"}, inplace=True)
        # Calculate year-over-year growth rate
        yearly_vol["YoY_growth_%"] = (
            yearly_vol["Total_Sales_Volume"].pct_change() * 100
        ).round(2)
        print(yearly_vol)
        logger.info(f"Annual sales trend analysis completed, covering {len(yearly_vol)} years")
    else:
        logger.warning("Missing Year / Sales_Volume columns, cannot perform annual sales aggregation")
        print("Missing Year / Sales_Volume columns, cannot perform annual sales aggregation.")

    print("\n=== Annual Average Price & Revenue Trend (if columns exist) ===")
    if {"Year", "Sales_Volume", "Price_USD"}.issubset(cols):
        logger.debug("Performing annual price and revenue analysis...")
        df_rev = df.copy()
        df_rev["Revenue_USD"] = df_rev["Price_USD"] * df_rev["Sales_Volume"]
        yearly_price_rev = (
            df_rev.groupby("Year")
            .agg(
                Total_Sales_Volume=("Sales_Volume", "sum"),
                Total_Revenue_USD=("Revenue_USD", "sum"),
                Avg_Price_USD=("Price_USD", "mean"),
            )
            .reset_index()
            .sort_values("Year")
        )
        yearly_price_rev["Weighted_ASP_USD"] = (
            yearly_price_rev["Total_Revenue_USD"]
            / yearly_price_rev["Total_Sales_Volume"].clip(lower=1)
        ).round(2)
        print(yearly_price_rev)
        logger.info(f"Annual price and revenue analysis completed")
    else:
        logger.warning("Missing Year / Sales_Volume / Price_USD columns, cannot perform annual price and revenue analysis")
        print("Missing Year / Sales_Volume / Price_USD columns, cannot perform annual price and revenue analysis.")
    
    logger.info("Trend analysis completed")


def analyze_mix(df: pd.DataFrame) -> None:
    """
    Model structure, regional structure and other distribution analysis.
    Based on actual columns: Model, Region, Sales_Volume, Price_USD.
    """
    logger.info("Starting structural analysis...")
    cols = set(df.columns)

    print("\n=== Model Sales Structure (Sales_Volume) ===")
    if {"Model", "Sales_Volume"}.issubset(cols):
        logger.debug("Performing model sales structure analysis...")
        model_units = (
            df.groupby("Model")["Sales_Volume"]
            .sum()
            .reset_index()
            .sort_values("Sales_Volume", ascending=False)
        )
        model_units["share_%"] = (
            model_units["Sales_Volume"] / model_units["Sales_Volume"].sum() * 100
        ).round(2)
        print(model_units.head(20))
        logger.info(f"Model sales structure analysis completed, total {len(model_units)} models")
    else:
        logger.warning("Missing Model / Sales_Volume columns, cannot perform model structure analysis")
        print("Missing Model / Sales_Volume columns, cannot perform model structure analysis.")

    print("\n=== Regional Sales Structure (Sales_Volume) ===")
    if {"Region", "Sales_Volume"}.issubset(cols):
        logger.debug("Performing regional sales structure analysis...")
        region_units = (
            df.groupby("Region")["Sales_Volume"]
            .sum()
            .reset_index()
            .sort_values("Sales_Volume", ascending=False)
        )
        region_units["share_%"] = (
            region_units["Sales_Volume"] / region_units["Sales_Volume"].sum() * 100
        ).round(2)
        print(region_units)
        logger.info(f"Regional sales structure analysis completed, total {len(region_units)} regions")
    else:
        logger.warning("Missing Region / Sales_Volume columns, cannot perform regional structure analysis")
        print("Missing Region / Sales_Volume columns, cannot perform regional structure analysis.")
    
    logger.info("Structural analysis completed")



def analyze_revenue(df: pd.DataFrame) -> None:
    """
    Revenue and per-vehicle price analysis.
    Based on actual columns: Price_USD (per-vehicle price), Sales_Volume (sales volume).
    """
    logger.info("Starting revenue and price analysis...")
    cols = set(df.columns)

    print("\n=== Revenue/Price Analysis ===")
    if not {"Price_USD", "Sales_Volume"}.issubset(cols):
        logger.warning("Missing Price_USD / Sales_Volume columns, cannot perform revenue and per-vehicle price analysis")
        print("Missing Price_USD / Sales_Volume columns, cannot perform revenue and per-vehicle price analysis.")
        return

    df_valid = df[df["Sales_Volume"] > 0].copy()
    logger.debug(f"Valid data rows after filtering: {len(df_valid)}")
    df_valid["Revenue_USD"] = df_valid["Price_USD"] * df_valid["Sales_Volume"]

    print("\nOverall per-vehicle price (Price_USD) distribution:")
    print(df_valid["Price_USD"].describe())

    print("\nOverall revenue (Revenue_USD) situation:")
    print(
        df_valid["Revenue_USD"].describe()
    )  # Overall order revenue distribution (each row is a combination: model/region/configuration)

    if "Model" in cols:
        logger.debug("Performing revenue analysis by model...")
        model_rev = (
            df_valid.groupby("Model")
            .agg(
                Total_Sales_Volume=("Sales_Volume", "sum"),
                Total_Revenue_USD=("Revenue_USD", "sum"),
                Avg_Price_USD=("Price_USD", "mean"),
            )
            .reset_index()
            .sort_values("Total_Revenue_USD", ascending=False)
        )
        model_rev["Weighted_ASP_USD"] = (
            model_rev["Total_Revenue_USD"]
            / model_rev["Total_Sales_Volume"].clip(lower=1)
        ).round(2)
        print("\nSales volume, revenue and weighted ASP by model:")
        print(model_rev.head(20))
        logger.info(f"Revenue analysis by model completed, total {len(model_rev)} models")

    if "Region" in cols:
        logger.debug("Performing revenue analysis by region...")
        region_rev = (
            df_valid.groupby("Region")
            .agg(
                Total_Sales_Volume=("Sales_Volume", "sum"),
                Total_Revenue_USD=("Revenue_USD", "sum"),
                Avg_Price_USD=("Price_USD", "mean"),
            )
            .reset_index()
            .sort_values("Total_Revenue_USD", ascending=False)
        )
        region_rev["Weighted_ASP_USD"] = (
            region_rev["Total_Revenue_USD"]
            / region_rev["Total_Sales_Volume"].clip(lower=1)
        ).round(2)
        print("\nSales volume, revenue and weighted ASP by region:")
        print(region_rev)
        logger.info(f"Revenue analysis by region completed, total {len(region_rev)} regions")

    if "Engine_Size_L" in cols:
        logger.debug("Performing price analysis by engine size...")
        print("\nAverage price by engine size range:")
        engine_price = (
            df_valid.groupby("Engine_Size_L")["Price_USD"]
            .mean()
            .reset_index()
            .sort_values("Engine_Size_L")
        )
        print(engine_price)
        logger.info(f"Price analysis by engine size completed")
    
    logger.info("Revenue and price analysis completed")


def _build_summary_for_ai(df: pd.DataFrame) -> dict:
    """
    Pre-aggregate key metrics into a compact JSON for GPT interpretation.
    Only pass structured numbers, not details, to reduce token cost.
    """
    logger.info("Starting to build AI report data summary...")
    summary: dict = {}
    cols = set(df.columns)

    # Annual trends
    if {"Year", "Sales_Volume"}.issubset(cols):
        yearly = (
            df.groupby("Year")["Sales_Volume"]
            .sum()
            .reset_index()
            .sort_values("Year")
        )
        yearly["YoY_growth_%"] = yearly["Sales_Volume"].pct_change() * 100
        summary["yearly_sales"] = yearly.round(2).to_dict(orient="records")

    # Regional performance
    if {"Region", "Sales_Volume", "Price_USD"}.issubset(cols):
        tmp = df.copy()
        tmp["Revenue_USD"] = tmp["Price_USD"] * tmp["Sales_Volume"]
        region_agg = (
            tmp.groupby("Region")
            .agg(
                Total_Sales_Volume=("Sales_Volume", "sum"),
                Total_Revenue_USD=("Revenue_USD", "sum"),
                Avg_Price_USD=("Price_USD", "mean"),
            )
            .reset_index()
        )
        region_agg["Weighted_ASP_USD"] = (
            region_agg["Total_Revenue_USD"]
            / region_agg["Total_Sales_Volume"].clip(lower=1)
        )
        summary["region_summary"] = region_agg.round(2).to_dict(orient="records")

    # Model performance
    if {"Model", "Sales_Volume", "Price_USD"}.issubset(cols):
        tmp = df.copy()
        tmp["Revenue_USD"] = tmp["Price_USD"] * tmp["Sales_Volume"]
        model_agg = (
            tmp.groupby("Model")
            .agg(
                Total_Sales_Volume=("Sales_Volume", "sum"),
                Total_Revenue_USD=("Revenue_USD", "sum"),
                Avg_Price_USD=("Price_USD", "mean"),
            )
            .reset_index()
        )
        model_agg["Weighted_ASP_USD"] = (
            model_agg["Total_Revenue_USD"]
            / model_agg["Total_Sales_Volume"].clip(lower=1)
        )
        # Only keep top and bottom few by sales and revenue to avoid too many models causing excessive tokens
        summary["model_top_by_volume"] = (
            model_agg.sort_values("Total_Sales_Volume", ascending=False)
            .head(10)
            .round(2)
            .to_dict(orient="records")
        )
        summary["model_bottom_by_volume"] = (
            model_agg.sort_values("Total_Sales_Volume", ascending=True)
            .head(5)
            .round(2)
            .to_dict(orient="records")
        )
        summary["model_top_by_revenue"] = (
            model_agg.sort_values("Total_Revenue_USD", ascending=False)
            .head(10)
            .round(2)
            .to_dict(orient="records")
        )

    # Relationship between price and engine size, mileage (high-level correlation, not strict causality)
    extra_insights: dict = {}
    if {"Price_USD", "Engine_Size_L"}.issubset(cols):
        engine_price = (
            df.groupby("Engine_Size_L")["Price_USD"]
            .mean()
            .reset_index()
            .sort_values("Engine_Size_L")
        )
        extra_insights["engine_size_vs_price"] = (
            engine_price.round(2).to_dict(orient="records")
        )
    if {"Price_USD", "Mileage_KM"}.issubset(cols):
        # Use sample correlation coefficient to prevent extreme value impact
        sample_df = df[["Price_USD", "Mileage_KM"]].dropna().sample(
            min(len(df), 5000), random_state=42
        )
        extra_insights["corr_price_mileage"] = (
            float(sample_df["Price_USD"].corr(sample_df["Mileage_KM"]))
            if len(sample_df) > 1
            else None
        )

    if extra_insights:
        summary["extra_numeric_insights"] = extra_insights

    logger.info(f"AI report data summary construction completed, containing {len(summary)} main dimensions")
    return summary



