import base64
import json
import logging
import os

import pandas as pd

from analyzer import _build_summary_for_ai

logger = logging.getLogger(__name__)

try:
    # First run `pip install openai` and set OPENAI_API_KEY in environment variables
    from openai import OpenAI

    _openai_client = OpenAI()
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    _openai_client = None
    logger.warning(f"OpenAI client initialization failed: {e}")


def _image_to_data_url(image_path: str) -> str:
    """
    Convert local image to base64-encoded data URL
    """
    try:
        with open(image_path, "rb") as f:
            img_bytes = f.read()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/png;base64,{img_b64}"
    except Exception as e:
        logger.error(f"Failed to read image ({image_path}): {e}")
        raise


def _call_api_for_section(
    system_prompt: str, user_prompt: str, section_name: str, input_images: list = None
) -> str:
    """
    Call API to generate a single section content
    Supports passing images as references
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt
        section_name: Section name
        input_images: List of image file paths to be used as input
    """
    try:
        logger.info(f"Calling GPT-5 API to generate {section_name}...")
        
        # If there are image inputs, use vision API
        if input_images:
            logger.debug(f"Including {len(input_images)} images as input")
            
            # Build content list
            content = [
                {
                    "type": "input_text",
                    "text": f"{system_prompt}\n\n{user_prompt}"
                }
            ]
            
            # Add images
            for img_path in input_images:
                if os.path.exists(img_path):
                    data_url = _image_to_data_url(img_path)
                    content.append({
                        "type": "input_image",
                        "image_url": data_url
                    })
                    logger.debug(f"Added image: {img_path}")
                else:
                    logger.warning(f"Image does not exist, skipping: {img_path}")
            
            # Use responses.create API
            response = _openai_client.responses.create(
                model="gpt-5.1",
                input=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )
            content_text = response.output_text
        else:
            # Regular text API call
            response = _openai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            content_text = response.choices[0].message.content  # type: ignore[assignment]
        
        logger.info(f"✓ {section_name} API call successful")
        return content_text
    except Exception as e:
        logger.error(f"GPT-5 API call failed ({section_name}): {e}", exc_info=True)
        return f"\n\n## {section_name}\n\n_Generation failed: {e}_\n\n"


def _insert_charts_after_text(text: str, chart_files: list) -> str:
    """
    Insert charts after text
    """
    result = text.rstrip() + "\n\n"
    
    for fname, desc in chart_files:
        result += f"![{desc}]({fname})\n\n"
    
    return result


def generate_ai_report(
    df: pd.DataFrame, output_file: str = "bmw_sales_ai_report.md"
) -> None:
    """
    Call GPT-5 API in segments to generate report, each section called separately, and insert corresponding charts after text.
    """
    logger.info("Starting to generate AI report (segmented mode)...")
    
    if _openai_client is None:
        logger.error("OpenAI client not initialized, cannot generate report")
        print(
            "Failed to initialize OpenAI client, please confirm:\n"
            "1) openai is installed in the current conda environment: pip install openai\n"
            "2) OPENAI_API_KEY environment variable is set\n"
            "GPT report generation will be skipped this time."
        )
        return

    logger.debug("Building data summary...")
    summary = _build_summary_for_ai(df)
    summary_json = json.dumps(summary, ensure_ascii=False)
    logger.debug(f"Data summary size: {len(summary_json)} characters")

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
            "charts": [],  # Executive Summary usually doesn't need additional charts
            "input_images": []  # No image input needed
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
            ],
            "input_images": []
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
            ],
            "input_images": []
        },
        {
            "name": "Key Sales Drivers",
            "prompt": f"""
Below is a JSON summary of BMW 2020–2024 sales data:

{summary_json}

Please also refer to the attached charts showing:
1. Engine size vs average price relationship
2. Mileage vs price scatter plot

Write a **Key Sales Drivers** section that:
- Analyses key drivers such as price positioning, model mix, regional mix, engine size, etc.
- References the patterns visible in the attached charts (engine size correlation, mileage depreciation)
- Focuses on business reasoning supported by data (do not claim strict causality)
- Includes at least one Markdown-formatted table that makes a key driver comparison explicit

Use the heading "## 4. Key Sales Drivers" and format as Markdown.
""",
            "charts": [
                ("chart_05_model_weighted_asp.png", "Weighted average selling price (ASP) by model."),
                ("chart_08_region_weighted_asp.png", "Weighted ASP by region."),
                ("chart_13_engine_size_vs_price.png", "Average price by engine size."),
                ("chart_14_mileage_vs_price.png", "Mileage vs price scatter plot.")
            ],
            "input_images": [
                "chart_13_engine_size_vs_price.png",
                "chart_14_mileage_vs_price.png"
            ]  # Chapter 4 requires these two charts as visual input
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
            ],
            "input_images": []
        }
    ]

    # Generate complete report
    full_report = "# BMW Sales Analysis Report (2020–2024)\n\n"
    
    try:
        for section in sections_config:
            logger.info(f"Starting to generate section: {section['name']}")
            
            # Get images that this section needs as input (if any)
            input_images = section.get("input_images", [])
            
            # Call API to generate section content
            section_content = _call_api_for_section(
                system_prompt=system_prompt,
                user_prompt=section["prompt"],
                section_name=section["name"],
                input_images=input_images
            )
            
            # Insert corresponding charts after section content
            if section["charts"]:
                section_content = _insert_charts_after_text(
                    section_content, 
                    section["charts"]
                )
            
            full_report += section_content + "\n\n"
            logger.info(f"✓ Section {section['name']} completed and charts inserted")

        # Write to file
        logger.debug(f"Writing report file: {output_file}")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_report)
        logger.info(f"AI-generated analysis report successfully saved to: {output_file}")
        print(f"AI-generated analysis report saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        print(f"Report generation failed: {e}")



