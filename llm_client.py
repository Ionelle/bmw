import json
import logging

import pandas as pd

from analyzer import _build_summary_for_ai

logger = logging.getLogger(__name__)

try:
    # 需要先 `pip install openai`，并在环境变量中设置 OPENAI_API_KEY
    from openai import OpenAI

    _openai_client = OpenAI()
    logger.info("OpenAI 客户端初始化成功")
except Exception as e:
    _openai_client = None
    logger.warning(f"OpenAI 客户端初始化失败: {e}")


def _call_api_for_section(
    system_prompt: str, user_prompt: str, section_name: str
) -> str:
    """
    调用 API 生成单个章节内容
    """
    try:
        logger.info(f"正在调用 GPT-5 API 生成 {section_name}...")
        response = _openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content  # type: ignore[assignment]
        logger.info(f"✓ {section_name} API 调用成功")
        return content
    except Exception as e:
        logger.error(f"调用 GPT-5 API 失败 ({section_name}): {e}", exc_info=True)
        return f"\n\n## {section_name}\n\n_生成失败: {e}_\n\n"


def _insert_charts_after_text(text: str, chart_files: list) -> str:
    """
    在文本后插入图表
    """
    result = text.rstrip() + "\n\n"
    
    for fname, desc in chart_files:
        result += f"![{desc}]({fname})\n\n"
    
    return result


def generate_ai_report(
    df: pd.DataFrame, output_file: str = "bmw_sales_ai_report.md"
) -> None:
    """
    分段调用 GPT-5 API 生成报告，每个章节单独调用，并在文本后插入对应图表。
    """
    logger.info("开始生成AI报告（分段模式）...")
    
    if _openai_client is None:
        logger.error("OpenAI 客户端未初始化，无法生成报告")
        print(
            "未能初始化 OpenAI 客户端，请确认：\n"
            "1) 已在当前 conda 环境中安装 openai：pip install openai\n"
            "2) 已设置 OPENAI_API_KEY 环境变量\n"
            "本次将跳过 GPT 报告生成。"
        )
        return

    logger.debug("构建数据摘要...")
    summary = _build_summary_for_ai(df)
    summary_json = json.dumps(summary, ensure_ascii=False)
    logger.debug(f"数据摘要大小: {len(summary_json)} 字符")

    system_prompt = (
        "You are a senior business analyst in the global automotive industry. "
        "You are excellent at turning complex quantitative data into concise, executive-ready insights. "
        "Write in clear, structured, business-oriented English suitable for non-technical senior leaders. "
        "Format all output as GitHub-Flavored Markdown with appropriate headings, bullet points, and tables."
    )

    # 定义5个章节及其对应的图表
    sections_config = [
        {
            "name": "Executive Summary",
            "prompt": f"""
Below is a JSON summary of BMW 2020–2024 sales data:

{summary_json}

Write an **Executive Summary** section with 3–6 bullet points that capture the overall performance and key messages.
Include at least one Markdown-formatted table or chart from the JSON data.
Use the heading "## 1. Executive Summary" and format as Markdown.
""",
            "charts": []  # Executive Summary 通常不需要额外图表
        },
        {
            "name": "Sales Performance Over Time",
            "prompt": f"""
Below is a JSON summary of BMW 2020–2024 sales data:

{summary_json}

Write a **Sales Performance Over Time** section that:
- Describes sales and revenue trends by year and by region
- Highlights inflection points and years of acceleration/slowdown
- Includes at least one Markdown-formatted table showing key year-over-year comparisons

Use the heading "## 2. Sales Performance Over Time" and format as Markdown.
""",
            "charts": [
                ("chart_01_year_volume_yoy.png", "Annual total BMW sales volume and year-over-year (YoY) growth from 2020 to 2024."),
                ("chart_02_year_revenue_asp.png", "Annual total revenue and weighted average selling price (ASP) from 2020 to 2024."),
                ("chart_09_year_region_heatmap.png", "Sales volume heatmap by year and region.")
            ]
        },
        {
            "name": "Top & Underperforming Models / Markets",
            "prompt": f"""
Below is a JSON summary of BMW 2020–2024 sales data:

{summary_json}

Write a **Top & Underperforming Models / Markets** section that:
- Names the best and worst performing models/regions
- Explains plausible reasons based on the data
- Includes at least one Markdown-formatted table highlighting rankings or performance gaps

Use the heading "## 3. Top & Underperforming Models / Markets" and format as Markdown.
""",
            "charts": [
                ("chart_03_model_top10_volume.png", "Top 10 BMW models ranked by total sales volume over 2020–2024."),
                ("chart_04_model_top10_revenue.png", "Top 10 BMW models ranked by total revenue over 2020–2024."),
                ("chart_06_region_volume.png", "Total BMW sales volume by region."),
                ("chart_07_region_revenue.png", "Total BMW revenue by region.")
            ]
        },
        {
            "name": "Key Sales Drivers",
            "prompt": f"""
Below is a JSON summary of BMW 2020–2024 sales data:

{summary_json}

Write a **Key Sales Drivers** section that:
- Analyses key drivers such as price positioning, model mix, regional mix, engine size, etc.
- Focuses on business reasoning supported by data (do not claim strict causality)
- Includes at least one Markdown-formatted table that makes a key driver comparison explicit

Use the heading "## 4. Key Sales Drivers" and format as Markdown.
""",
            "charts": [
                ("chart_05_model_weighted_asp.png", "Weighted average selling price (ASP) by model."),
                ("chart_08_region_weighted_asp.png", "Weighted ASP by region."),
                ("chart_13_engine_size_vs_price.png", "Average price by engine size."),
                ("chart_14_mileage_vs_price.png", "Mileage vs price scatter plot.")
            ]
        },
        {
            "name": "Strategic Insights & Recommendations",
            "prompt": f"""
Below is a JSON summary of BMW 2020–2024 sales data:

{summary_json}

Write a **Strategic Insights & Recommendations** section that MUST explicitly analyse the following two core insights:

**Core Insight 1 – High-end models' functional depreciation and quasi-fleet behaviour:**
- Data pattern: extreme price dispersion for similar luxury nameplates across regions and usage profiles.
- Examples:
  - 7 Series (2020, North America), automatic, low mileage (~27,000 km): USD 100,015
  - 7 Series (2020, South America), manual, high mileage (~122,000 km): USD 49,898
  - i8 (2022, Europe), manual diesel, very high mileage (~196,000 km): USD 55,064
- Discuss how certain luxury configurations behave like fleet/utility assets with accelerated depreciation.

**Core Insight 2 – The colour premium and emotional demand in M performance models:**
- Data pattern: M3/M5 appear more frequently in vivid colours vs mainstream models (X1, 3 Series)
- Examples:
  - M5 (2022) in red maintains strong appeal even with manual transmission
  - Grey 3 Series cluster in utilitarian contexts
- Argue how colour acts as an emotional value driver beyond specs.

Then provide 3–5 specific, actionable business recommendations (e.g. which regions/models/price bands to prioritise).
Include a Markdown table or structured list.

Use the heading "## 5. Strategic Insights & Recommendations" and format as Markdown.
""",
            "charts": [
                ("chart_12_price_distribution.png", "Price distribution showing dispersion across models and configurations.")
            ]
        }
    ]

    # 生成完整报告
    full_report = "# BMW Sales Analysis Report (2020–2024)\n\n"
    
    try:
        for section in sections_config:
            logger.info(f"开始生成章节: {section['name']}")
            
            # 调用 API 生成该章节内容
            section_content = _call_api_for_section(
                system_prompt=system_prompt,
                user_prompt=section["prompt"],
                section_name=section["name"]
            )
            
            # 在章节内容后插入对应图表
            if section["charts"]:
                section_content = _insert_charts_after_text(
                    section_content, 
                    section["charts"]
                )
            
            full_report += section_content + "\n\n"
            logger.info(f"✓ 章节 {section['name']} 已完成并插入图表")

        # 写入文件
        logger.debug(f"正在写入报告文件: {output_file}")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_report)
        logger.info(f"AI 生成的分析报告已成功保存到: {output_file}")
        print(f"AI 生成的分析报告已保存到: {output_file}")
        
    except Exception as e:
        logger.error(f"生成报告失败: {e}", exc_info=True)
        print(f"生成报告失败：{e}")



