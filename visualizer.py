import logging
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)


def plot_all_charts(df: pd.DataFrame) -> None:
    """
    生成图表并保存到当前目录：
      1. 年度总销量 + YoY 增长（双轴）
      2. 年度总收入 + 加权 ASP
      3. 车型销量 Top 10
      4. 车型收入 Top 10
      5. 车型加权 ASP
      6. 区域销量
      7. 区域收入
      8. 区域加权 ASP
      9. 年份 × 区域销量热力图
     12. 价格分布直方图 + KDE
     13. 发动机排量 vs 平均价格
     14. 里程数 vs 价格 散点图
    """
    logger.info("开始生成所有图表...")
    sns.set(style="whitegrid", font_scale=1.1)
    
    chart_count = 0

    # 图1：年度总销量 + YoY 增长
    if {"Year", "Sales_Volume"}.issubset(df.columns):
        logger.debug("生成图表1: 年度总销量 + YoY 增长")
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
            logger.info("✓ 图表1生成成功: chart_01_year_volume_yoy.png")
        except Exception as e:
            logger.error(f"生成图表1失败: {e}", exc_info=True)

    # 为后续收入/ASP 分析预先算好 Revenue
    df_rev = df.copy()
    if {"Price_USD", "Sales_Volume"}.issubset(df_rev.columns):
        df_rev["Revenue_USD"] = df_rev["Price_USD"] * df_rev["Sales_Volume"]

    # 图2：年度总收入 + 加权 ASP
    if {"Year", "Sales_Volume", "Price_USD"}.issubset(df.columns):
        logger.debug("生成图表2: 年度总收入 + 加权 ASP")
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
            logger.info("✓ 图表2生成成功: chart_02_year_revenue_asp.png")
        except Exception as e:
            logger.error(f"生成图表2失败: {e}", exc_info=True)

    # 车型聚合：为图3–5 准备
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

    # 图3：车型销量 Top 10
    if model_agg is not None:
        logger.debug("生成图表3: 车型销量 Top 10")
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
            logger.info("✓ 图表3生成成功: chart_03_model_top10_volume.png")
        except Exception as e:
            logger.error(f"生成图表3失败: {e}", exc_info=True)

    # 图4：车型收入 Top 10
    if model_agg is not None:
        logger.debug("生成图表4: 车型收入 Top 10")
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
            logger.info("✓ 图表4生成成功: chart_04_model_top10_revenue.png")
        except Exception as e:
            logger.error(f"生成图表4失败: {e}", exc_info=True)

    # 图5：车型加权 ASP
    if model_agg is not None:
        logger.debug("生成图表5: 车型加权 ASP")
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
            logger.info("✓ 图表5生成成功: chart_05_model_weighted_asp.png")
        except Exception as e:
            logger.error(f"生成图表5失败: {e}", exc_info=True)

    # 区域聚合：为图6–8、图9 准备
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

    # 图6：区域销量
    if region_agg is not None:
        logger.debug("生成图表6: 区域销量")
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
            logger.info("✓ 图表6生成成功: chart_06_region_volume.png")
        except Exception as e:
            logger.error(f"生成图表6失败: {e}", exc_info=True)

    # 图7：区域收入
    if region_agg is not None:
        logger.debug("生成图表7: 区域收入")
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
            logger.info("✓ 图表7生成成功: chart_07_region_revenue.png")
        except Exception as e:
            logger.error(f"生成图表7失败: {e}", exc_info=True)

    # 图8：区域加权 ASP
    if region_agg is not None:
        logger.debug("生成图表8: 区域加权 ASP")
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
            logger.info("✓ 图表8生成成功: chart_08_region_weighted_asp.png")
        except Exception as e:
            logger.error(f"生成图表8失败: {e}", exc_info=True)

    # 图9：年份 × 区域销量热力图
    if {"Year", "Region", "Sales_Volume"}.issubset(df.columns):
        logger.debug("生成图表9: 年份×区域销量热力图")
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
            logger.info("✓ 图表9生成成功: chart_09_year_region_heatmap.png")
        except Exception as e:
            logger.error(f"生成图表9失败: {e}", exc_info=True)

    # 图12：价格分布直方图 + KDE
    if "Price_USD" in df.columns:
        logger.debug("生成图表12: 价格分布直方图 + KDE")
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
            logger.info("✓ 图表12生成成功: chart_12_price_distribution.png")
        except Exception as e:
            logger.error(f"生成图表12失败: {e}", exc_info=True)

    # 图13：发动机排量 vs 平均价格
    if {"Engine_Size_L", "Price_USD"}.issubset(df.columns):
        logger.debug("生成图表13: 发动机排量 vs 平均价格")
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
            logger.info("✓ 图表13生成成功: chart_13_engine_size_vs_price.png")
        except Exception as e:
            logger.error(f"生成图表13失败: {e}", exc_info=True)

    # 图14：里程数 vs 价格 散点图
    if {"Mileage_KM", "Price_USD"}.issubset(df.columns):
        logger.debug("生成图表14: 里程数 vs 价格散点图")
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
            logger.info("✓ 图表14生成成功: chart_14_mileage_vs_price.png")
        except Exception as e:
            logger.error(f"生成图表14失败: {e}", exc_info=True)
    
    logger.info(f"所有图表生成完成，共成功生成 {chart_count} 个图表")



