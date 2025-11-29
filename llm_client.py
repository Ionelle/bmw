import json

import pandas as pd

from analyzer import _build_summary_for_ai

try:
    # 需要先 `pip install openai`，并在环境变量中设置 OPENAI_API_KEY
    from openai import OpenAI

    _openai_client = OpenAI()
except Exception:
    _openai_client = None


def generate_ai_report(
    df: pd.DataFrame, output_file: str = "bmw_sales_ai_report.md"
) -> None:
    """
    调用 GPT-5 API，基于结构化数据自动生成一份英文高管可读的分析报告：
    - Executive Summary
    - Sales performance trend over time (by year / region)
    - Top / Underperforming models or markets
    - Key drivers of sales (price, segment, model type 等)
    - 1–2 条额外洞见（结合排量、里程等，以展示业务理解与创造力）
    - Recommendations
    """
    if _openai_client is None:
        print(
            "未能初始化 OpenAI 客户端，请确认：\n"
            "1) 已在当前 conda 环境中安装 openai：pip install openai\n"
            "2) 已设置 OPENAI_API_KEY 环境变量\n"
            "本次将跳过 GPT 报告生成。"
        )
        return

    summary = _build_summary_for_ai(df)
    summary_json = json.dumps(summary, ensure_ascii=False)

    system_prompt = (
        "You are a senior business analyst in the global automotive industry. "
        "You are excellent at turning complex quantitative data into concise, executive-ready insights. "
        "Write in clear, structured, business-oriented English suitable for non-technical senior leaders. "
        "Format all output as GitHub-Flavored Markdown with appropriate headings, bullet points, and tables."
    )

    user_prompt = f"""
Below is a JSON summary of BMW 2020–2024 sales data, already aggregated by year, region, model and other key dimensions:

{summary_json}

Using this JSON as your quantitative backbone, and incorporating the two pre-defined strategic insights described below, produce a structured business analysis report in English with the following sections (use these exact headings):

1. Executive Summary – 3–6 bullet points that capture the overall performance and key messages.
2. Sales Performance Over Time – describe sales and revenue trends by year and by region, highlight inflection points and years of acceleration/slowdown.
3. Top & Underperforming Models / Markets – name the best and worst performing models/regions and explain plausible reasons based on the data.
4. Key Sales Drivers – analyse key drivers such as price positioning, model mix, regional mix, engine size, etc. Do not claim strict causality, focus on business reasoning supported by data.
5. Strategic Insights & Recommendations – combine deep, narrative strategic insights with concrete, data-backed recommendations.

In section 5 (Strategic Insights & Recommendations), you MUST explicitly analyse and build around the following two core insights, treating them as hypotheses grounded in the same underlying BMW dataset:

- Core Insight 1 – High-end models' functional depreciation and quasi-fleet behaviour. Data pattern: there is extreme price dispersion for similar luxury nameplates across regions and usage profiles. For example:
  - Case A: 7 Series (2020, North America), automatic transmission, low mileage (~27,000 km), priced around USD 100,015.
  - Case B: 7 Series (2020, South America), manual transmission, very high mileage (~122,000 km), priced around USD 49,898.
  - Case C: i8 (2022, Europe), manual, diesel, very high mileage (~196,000 km), priced around USD 55,064.
  Use these examples to discuss how certain luxury configurations effectively behave like fleet/utility assets in specific markets, with accelerated functional depreciation versus list price positioning.

- Core Insight 2 – The colour premium and emotional demand in M performance models. Data pattern: performance models such as M3/M5 tend to appear more frequently in vivid, emotional colours than mainstream nameplates such as X1 or 3 Series, and this interacts with perceived value and price realisation. For example:
  - M5 (2022) in red maintains strong appeal even in manual-transmission configurations.
  - Grey 3 Series tend to cluster in more utilitarian/commuter contexts.
  Use this to argue how colour and visual specification act as emotional value drivers beyond pure performance specs, and how this should influence pricing, merchandising and stock mix decisions.

Requirements:
- The ENTIRE report must be written in English and formatted as Markdown (use Markdown headings, bullet points and tables where appropriate).
- For each of the 5 sections above, you MUST include at least one Markdown-formatted visual representation ("Chart") that you generate yourself from the JSON data (for example, a compact table, ranked list, or other structured view). Clearly label each with a bold title such as "**Chart – [short title]**" followed by the Markdown structure.
- For section 1 (Executive Summary), provide 3–6 bullet points that capture overall performance and key messages.
- For section 2 (Sales Performance Over Time), describe sales and revenue trends by year and by region, and highlight years of acceleration/slowdown or major turning points; include at least one chart that summarises the key comparison (e.g. year vs. volume/revenue).
- For section 3 (Top & Underperforming Models / Markets), name the best and worst performing models/regions and explain plausible reasons based on the data; include at least one chart highlighting rankings or performance gaps.
- For section 4 (Key Sales Drivers), analyse key drivers such as price positioning, model mix, regional mix, engine size, etc. Do not claim strict causality; focus on business reasoning supported by the data; include at least one chart that makes a key driver comparison explicit.
- For section 5 (Strategic Insights & Recommendations), you must (a) develop the two core insights above into a coherent strategic narrative, and (b) provide 3–5 specific, actionable business recommendations (e.g. which regions/models/price bands to prioritise or adjust, and how). You may use a short table or structured list as the chart for this section.
- Use clear section headings with the exact titles given above, and short paragraphs or bullet points where appropriate.
- Where possible, reference concrete numbers or directions of change (e.g. "YoY +X%", "ranked first among all regions"), but you do not need to repeat full raw tables.
"""

    try:
        response = _openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            # 降低温度以提高结构和论述的一致性（可重复性更好）
            temperature=0.2,
        )
        content = response.choices[0].message.content  # type: ignore[assignment]
    except Exception as e:
        print(f"调用 GPT-5 API 失败：{e}")
        return

    try:
        # 在报告末尾追加“图表附录”，对 chart_01 ~ chart_08 逐一做简要说明并给出文件路径
        chart_info = [
            (
                "chart_01_year_volume_yoy.png",
                "Annual total BMW sales volume and year-over-year (YoY) growth from 2020 to 2024.",
            ),
            (
                "chart_02_year_revenue_asp.png",
                "Annual total revenue and weighted average selling price (ASP) from 2020 to 2024.",
            ),
            (
                "chart_03_model_top10_volume.png",
                "Top 10 BMW models ranked by total sales volume over 2020–2024.",
            ),
            (
                "chart_04_model_top10_revenue.png",
                "Top 10 BMW models ranked by total revenue over 2020–2024.",
            ),
            (
                "chart_05_model_weighted_asp.png",
                "Weighted average selling price (ASP) by model, highlighting premium vs. entry segments.",
            ),
            (
                "chart_06_region_volume.png",
                "Total BMW sales volume by region, showing geographic scale differences.",
            ),
            (
                "chart_07_region_revenue.png",
                "Total BMW revenue by region, highlighting high-value markets.",
            ),
            (
                "chart_08_region_weighted_asp.png",
                "Weighted ASP by region, indicating relative price positioning across markets.",
            ),
        ]
        lines = []
        for fname, desc in chart_info:
            # 在附录中直接嵌入图片，并在图片前给出简要文字说明
            # Markdown 中图片使用相对路径，默认为与报告在同一目录下的 PNG 文件
            lines.append(
                f"### {fname}\n\n"
                f"{desc}\n\n"
                f"![{desc}]({fname})\n"
            )

        charts_section = (
            "\n\n---\n\n"
            "## Chart Appendix (chart_01–chart_08)\n"
            "The following charts have been generated to visually support the analysis above.\n"
            "Each chart is embedded directly below its brief description:\n\n"
            + "\n".join(lines)
        )
        content = f"{content}{charts_section}"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"AI 生成的分析报告已保存到: {output_file}")
    except Exception as e:
        print(f"写入报告文件失败：{e}")



