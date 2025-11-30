import logging
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


def plot_all_charts(df: pd.DataFrame) -> None:
    """
    Generate charts and save to current directory:
      1. Annual total sales + YoY growth (dual axis)
      2. Annual total revenue + weighted ASP
      3. Top 10 models by sales volume
      4. Top 10 models by revenue
      5. Weighted ASP by model
      6. Sales volume by region
      7. Revenue by region
      8. Weighted ASP by region
      9. Year × Region sales volume heatmap
     12. Price distribution histogram + KDE
     13. Engine size vs average price
     14. Mileage vs price scatter plot
    """
    logger.info("Starting to generate all charts...")
    sns.set(style="whitegrid", font_scale=1.1)
    
    chart_count = 0

    # Chart 1: Annual total sales + YoY growth
    if {"Year", "Sales_Volume"}.issubset(df.columns):
        logger.debug("Generating chart 1: Annual total sales + YoY growth")
        try:
            yearly = (
                df.groupby("Year")["Sales_Volume"]
                .sum()
                .reset_index()
                .sort_values("Year")
            )
            yearly["YoY_growth_%"] = yearly["Sales_Volume"].pct_change() * 100

            fig, ax1 = plt.subplots(figsize=(8, 4))
            ax1.bar(yearly["Year"], yearly["Sales_Volume"], color="#4C72B0", alpha=0.7)
            ax1.set_ylabel("Total Sales Volume")

            ax2 = ax1.twinx()
            ax2.plot(
                yearly["Year"],
                yearly["YoY_growth_%"],
                color="#DD8452",
                marker="o",
            )
            ax2.set_ylabel("YoY Growth (%)")
            plt.title("BMW Global Sales Volume & YoY Growth (2020–2024)")
            plt.tight_layout()
            plt.savefig("chart_01_year_volume_yoy.png")
            plt.close(fig)
            chart_count += 1
            logger.info("✓ Chart 1 generated successfully: chart_01_year_volume_yoy.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 1: {e}", exc_info=True)

    # Pre-calculate Revenue for subsequent revenue/ASP analysis
    df_rev = df.copy()
    if {"Price_USD", "Sales_Volume"}.issubset(df_rev.columns):
        df_rev["Revenue_USD"] = df_rev["Price_USD"] * df_rev["Sales_Volume"]

    # Chart 2: Annual total revenue + weighted ASP
    if {"Year", "Sales_Volume", "Price_USD"}.issubset(df.columns):
        logger.debug("Generating chart 2: Annual total revenue + weighted ASP")
        try:
            yearly_rev = (
                df_rev.groupby("Year")
                .agg(
                    Total_Sales_Volume=("Sales_Volume", "sum"),
                    Total_Revenue_USD=("Revenue_USD", "sum"),
                )
                .reset_index()
                .sort_values("Year")
            )
            yearly_rev["Weighted_ASP_USD"] = (
                yearly_rev["Total_Revenue_USD"]
                / yearly_rev["Total_Sales_Volume"].clip(lower=1)
            )

            fig, ax1 = plt.subplots(figsize=(8, 4))
            ax1.bar(
                yearly_rev["Year"],
                yearly_rev["Total_Revenue_USD"] / 1e9,
                color="#55A868",
                alpha=0.7,
            )
            ax1.set_ylabel("Total Revenue (billion USD)")

            ax2 = ax1.twinx()
            ax2.plot(
                yearly_rev["Year"],
                yearly_rev["Weighted_ASP_USD"],
                color="#C44E52",
                marker="o",
            )
            ax2.set_ylabel("Weighted ASP (USD)")
            plt.title("BMW Revenue & Weighted ASP (2020–2024)")
            plt.tight_layout()
            plt.savefig("chart_02_year_revenue_asp.png")
            plt.close(fig)
            chart_count += 1
            logger.info("✓ Chart 2 generated successfully: chart_02_year_revenue_asp.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 2: {e}", exc_info=True)

    # Model aggregation: prepare for charts 3–5
    model_agg = None
    if {"Model", "Sales_Volume", "Price_USD"}.issubset(df.columns):
        model_agg = (
            df_rev.groupby("Model")
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

    # Chart 3: Top 10 models by sales volume
    if model_agg is not None:
        logger.debug("Generating chart 3: Top 10 models by sales volume")
        try:
            top_models_by_vol = model_agg.sort_values(
                "Total_Sales_Volume", ascending=False
            ).head(10)
            plt.figure(figsize=(8, 4))
            sns.barplot(
                data=top_models_by_vol,
                x="Total_Sales_Volume",
                y="Model",
                palette="Blues_r",
            )
            plt.title("Top 10 Models by Sales Volume")
            plt.xlabel("Total Sales Volume")
            plt.ylabel("Model")
            plt.tight_layout()
            plt.savefig("chart_03_model_top10_volume.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 3 generated successfully: chart_03_model_top10_volume.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 3: {e}", exc_info=True)

    # Chart 4: Top 10 models by revenue
    if model_agg is not None:
        logger.debug("Generating chart 4: Top 10 models by revenue")
        try:
            top_models_by_rev = model_agg.sort_values(
                "Total_Revenue_USD", ascending=False
            ).head(10)
            plt.figure(figsize=(8, 4))
            sns.barplot(
                data=top_models_by_rev,
                x="Total_Revenue_USD",
                y="Model",
                palette="Greens_r",
            )
            plt.title("Top 10 Models by Revenue")
            plt.xlabel("Total Revenue (USD)")
            plt.ylabel("Model")
            plt.tight_layout()
            plt.savefig("chart_04_model_top10_revenue.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 4 generated successfully: chart_04_model_top10_revenue.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 4: {e}", exc_info=True)

    # Chart 5: Weighted ASP by model
    if model_agg is not None:
        logger.debug("Generating chart 5: Weighted ASP by model")
        try:
            plt.figure(figsize=(8, 4))
            sns.barplot(
                data=model_agg.sort_values("Weighted_ASP_USD", ascending=False),
                x="Weighted_ASP_USD",
                y="Model",
                palette="Purples_r",
            )
            plt.title("Weighted ASP by Model")
            plt.xlabel("Weighted ASP (USD)")
            plt.ylabel("Model")
            plt.tight_layout()
            plt.savefig("chart_05_model_weighted_asp.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 5 generated successfully: chart_05_model_weighted_asp.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 5: {e}", exc_info=True)

    # Regional aggregation: prepare for charts 6–8 and chart 9
    region_agg = None
    if {"Region", "Sales_Volume", "Price_USD"}.issubset(df.columns):
        region_agg = (
            df_rev.groupby("Region")
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

    # Chart 6: Sales volume by region
    if region_agg is not None:
        logger.debug("Generating chart 6: Sales volume by region")
        try:
            plt.figure(figsize=(7, 4))
            sns.barplot(
                data=region_agg.sort_values("Total_Sales_Volume", ascending=False),
                x="Region",
                y="Total_Sales_Volume",
                palette="Blues",
            )
            plt.title("Total Sales Volume by Region")
            plt.xlabel("Region")
            plt.ylabel("Total Sales Volume")
            plt.tight_layout()
            plt.savefig("chart_06_region_volume.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 6 generated successfully: chart_06_region_volume.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 6: {e}", exc_info=True)

    # Chart 7: Revenue by region
    if region_agg is not None:
        logger.debug("Generating chart 7: Revenue by region")
        try:
            plt.figure(figsize=(7, 4))
            sns.barplot(
                data=region_agg.sort_values("Total_Revenue_USD", ascending=False),
                x="Region",
                y="Total_Revenue_USD",
                palette="Greens",
            )
            plt.title("Total Revenue by Region")
            plt.xlabel("Region")
            plt.ylabel("Total Revenue (USD)")
            plt.tight_layout()
            plt.savefig("chart_07_region_revenue.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 7 generated successfully: chart_07_region_revenue.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 7: {e}", exc_info=True)

    # Chart 8: Weighted ASP by region
    if region_agg is not None:
        logger.debug("Generating chart 8: Weighted ASP by region")
        try:
            plt.figure(figsize=(7, 4))
            sns.barplot(
                data=region_agg.sort_values("Weighted_ASP_USD", ascending=False),
                x="Region",
                y="Weighted_ASP_USD",
                palette="Oranges",
            )
            plt.title("Weighted ASP by Region")
            plt.xlabel("Region")
            plt.ylabel("Weighted ASP (USD)")
            plt.tight_layout()
            plt.savefig("chart_08_region_weighted_asp.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 8 generated successfully: chart_08_region_weighted_asp.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 8: {e}", exc_info=True)

    # Chart 9: Year × Region sales volume heatmap
    if {"Year", "Region", "Sales_Volume"}.issubset(df.columns):
        logger.debug("Generating chart 9: Year × Region sales volume heatmap")
        try:
            pivot = (
                df.groupby(["Year", "Region"])["Sales_Volume"]
                .sum()
                .reset_index()
                .pivot(index="Region", columns="Year", values="Sales_Volume")
            )
            plt.figure(figsize=(8, 4))
            sns.heatmap(
                pivot,
                annot=False,
                cmap="YlGnBu",
                fmt=".0f",
            )
            plt.title("Sales Volume Heatmap by Year & Region")
            plt.xlabel("Year")
            plt.ylabel("Region")
            plt.tight_layout()
            plt.savefig("chart_09_year_region_heatmap.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 9 generated successfully: chart_09_year_region_heatmap.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 9: {e}", exc_info=True)

    # Chart 12: Price distribution histogram + KDE
    if "Price_USD" in df.columns:
        logger.debug("Generating chart 12: Price distribution histogram + KDE")
        try:
            plt.figure(figsize=(7, 4))
            sns.histplot(
                df["Price_USD"],
                bins=40,
                kde=True,
                color="#4C72B0",
            )
            plt.title("Price Distribution (USD)")
            plt.xlabel("Price (USD)")
            plt.ylabel("Count")
            plt.tight_layout()
            plt.savefig("chart_12_price_distribution.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 12 generated successfully: chart_12_price_distribution.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 12: {e}", exc_info=True)

    # Chart 13: Engine size vs average price
    if {"Engine_Size_L", "Price_USD"}.issubset(df.columns):
        logger.debug("Generating chart 13: Engine size vs average price")
        try:
            engine_price = (
                df.groupby("Engine_Size_L")["Price_USD"]
                .mean()
                .reset_index()
                .sort_values("Engine_Size_L")
            )
            plt.figure(figsize=(8, 4))
            sns.lineplot(
                data=engine_price,
                x="Engine_Size_L",
                y="Price_USD",
                marker="o",
                color="#DD8452",
            )
            plt.title("Average Price by Engine Size")
            plt.xlabel("Engine Size (L)")
            plt.ylabel("Average Price (USD)")
            plt.tight_layout()
            plt.savefig("chart_13_engine_size_vs_price.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 13 generated successfully: chart_13_engine_size_vs_price.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 13: {e}", exc_info=True)

    # Chart 14: Mileage vs price scatter plot
    if {"Mileage_KM", "Price_USD"}.issubset(df.columns):
        logger.debug("Generating chart 14: Mileage vs price scatter plot")
        try:
            plt.figure(figsize=(8, 4))
            sns.scatterplot(
                data=df.sample(min(len(df), 5000), random_state=42),
                x="Mileage_KM",
                y="Price_USD",
                alpha=0.3,
            )
            plt.title("Mileage vs Price (Sampled)")
            plt.xlabel("Mileage (KM)")
            plt.ylabel("Price (USD)")
            plt.tight_layout()
            plt.savefig("chart_14_mileage_vs_price.png")
            plt.close()
            chart_count += 1
            logger.info("✓ Chart 14 generated successfully: chart_14_mileage_vs_price.png")
        except Exception as e:
            logger.error(f"Failed to generate chart 14: {e}", exc_info=True)
    
    logger.info(f"All charts generated successfully, total {chart_count} charts created")



