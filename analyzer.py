import logging
import pandas as pd

logger = logging.getLogger(__name__)


def analyze_basic(df: pd.DataFrame) -> None:
    """
    基础结构与质量检查。
    """
    logger.info("开始基础分析...")
    logger.debug(f"数据形状: {df.shape[0]} 行 × {df.shape[1]} 列")
    
    print("=== 基础信息 ===")
    print(f"行数 × 列数: {df.shape[0]} × {df.shape[1]}")
    print("\n列名：")
    print(list(df.columns))
    
    missing_values = df.isna().sum()
    total_missing = missing_values.sum()
    if total_missing > 0:
        logger.warning(f"发现 {total_missing} 个缺失值")
    else:
        logger.info("数据完整，无缺失值")
    
    print("\n前 5 行：")
    print(df.head())
    print("\n缺失值统计：")
    print(missing_values)
    print("\n描述性统计：")
    print(df.describe(include="all"))
    
    logger.info("基础分析完成")


def analyze_trend(df: pd.DataFrame) -> None:
    """
    年度销量与价格趋势分析（结合实际列：Year, Price_USD, Sales_Volume）。
    """
    logger.info("开始趋势分析...")
    cols = set(df.columns)

    print("\n=== 年度销量趋势（Sales_Volume）===")
    if {"Year", "Sales_Volume"}.issubset(cols):
        logger.debug("执行年度销量聚合...")
        yearly_vol = (
            df.groupby("Year")["Sales_Volume"]
            .sum()
            .reset_index()
            .sort_values("Year")
        )
        yearly_vol.rename(columns={"Sales_Volume": "Total_Sales_Volume"}, inplace=True)
        # 计算同比增长率
        yearly_vol["YoY_growth_%"] = (
            yearly_vol["Total_Sales_Volume"].pct_change() * 100
        ).round(2)
        print(yearly_vol)
        logger.info(f"年度销量趋势分析完成，覆盖 {len(yearly_vol)} 个年份")
    else:
        logger.warning("缺少 Year / Sales_Volume 列，无法做年度销量聚合")
        print("缺少 Year / Sales_Volume 列，无法做年度销量聚合。")

    print("\n=== 年度平均价格 & 收入趋势（如列存在）===")
    if {"Year", "Sales_Volume", "Price_USD"}.issubset(cols):
        logger.debug("执行年度价格和收入分析...")
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
        logger.info(f"年度价格和收入分析完成")
    else:
        logger.warning("缺少 Year / Sales_Volume / Price_USD 列，无法做年度价格与收入分析")
        print("缺少 Year / Sales_Volume / Price_USD 列，无法做年度价格与收入分析。")
    
    logger.info("趋势分析完成")


def analyze_mix(df: pd.DataFrame) -> None:
    """
    车型结构、区域结构等分布分析。
    基于实际列：Model, Region, Sales_Volume, Price_USD。
    """
    logger.info("开始结构分析...")
    cols = set(df.columns)

    print("\n=== 车型销量结构（Sales_Volume）===")
    if {"Model", "Sales_Volume"}.issubset(cols):
        logger.debug("执行车型销量结构分析...")
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
        logger.info(f"车型销量结构分析完成，共 {len(model_units)} 个车型")
    else:
        logger.warning("缺少 Model / Sales_Volume 列，无法做车型结构分析")
        print("缺少 Model / Sales_Volume 列，无法做车型结构分析。")

    print("\n=== 区域销量结构（Sales_Volume）===")
    if {"Region", "Sales_Volume"}.issubset(cols):
        logger.debug("执行区域销量结构分析...")
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
        logger.info(f"区域销量结构分析完成，共 {len(region_units)} 个区域")
    else:
        logger.warning("缺少 Region / Sales_Volume 列，无法做区域结构分析")
        print("缺少 Region / Sales_Volume 列，无法做区域结构分析。")
    
    logger.info("结构分析完成")



def analyze_revenue(df: pd.DataFrame) -> None:
    """
    收入与单车价格分析。
    基于实际列：Price_USD（单车价格）、Sales_Volume（销量）。
    """
    logger.info("开始收入和价格分析...")
    cols = set(df.columns)

    print("\n=== 收入/价格分析 ===")
    if not {"Price_USD", "Sales_Volume"}.issubset(cols):
        logger.warning("缺少 Price_USD / Sales_Volume 列，无法做收入与单车价格分析")
        print("缺少 Price_USD / Sales_Volume 列，无法做收入与单车价格分析。")
        return

    df_valid = df[df["Sales_Volume"] > 0].copy()
    logger.debug(f"过滤后有效数据行数: {len(df_valid)}")
    df_valid["Revenue_USD"] = df_valid["Price_USD"] * df_valid["Sales_Volume"]

    print("\n整体单车价格（Price_USD）分布：")
    print(df_valid["Price_USD"].describe())

    print("\n整体收入（Revenue_USD）情况：")
    print(
        df_valid["Revenue_USD"].describe()
    )  # 总体订单收入分布（每一行是一个组合：车型/区域/配置）

    if "Model" in cols:
        logger.debug("执行按车型的收入分析...")
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
        print("\n按车型的销量、收入和加权 ASP：")
        print(model_rev.head(20))
        logger.info(f"按车型收入分析完成，共 {len(model_rev)} 个车型")

    if "Region" in cols:
        logger.debug("执行按区域的收入分析...")
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
        print("\n按区域的销量、收入和加权 ASP：")
        print(region_rev)
        logger.info(f"按区域收入分析完成，共 {len(region_rev)} 个区域")

    if "Engine_Size_L" in cols:
        logger.debug("执行按发动机排量的价格分析...")
        print("\n按发动机排量区间的平均价格：")
        engine_price = (
            df_valid.groupby("Engine_Size_L")["Price_USD"]
            .mean()
            .reset_index()
            .sort_values("Engine_Size_L")
        )
        print(engine_price)
        logger.info(f"按发动机排量价格分析完成")
    
    logger.info("收入和价格分析完成")


def _build_summary_for_ai(df: pd.DataFrame) -> dict:
    """
    将关键指标预聚合为一个紧凑的 JSON，用于喂给 GPT 做解读。
    只传结构化数字，不传明细，降低 token 成本。
    """
    logger.info("开始构建AI报告数据摘要...")
    summary: dict = {}
    cols = set(df.columns)

    # 年度趋势
    if {"Year", "Sales_Volume"}.issubset(cols):
        yearly = (
            df.groupby("Year")["Sales_Volume"]
            .sum()
            .reset_index()
            .sort_values("Year")
        )
        yearly["YoY_growth_%"] = yearly["Sales_Volume"].pct_change() * 100
        summary["yearly_sales"] = yearly.round(2).to_dict(orient="records")

    # 区域表现
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

    # 车型表现
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
        # 只保留销量和收入前后若干，避免车型过多导致 token 过大
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

    # 价格与排量、里程的关系（高层相关性，不做严格因果）
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
        # 为防止极值影响，使用样本相关系数
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

    logger.info(f"AI报告数据摘要构建完成，包含 {len(summary)} 个主要维度")
    return summary



