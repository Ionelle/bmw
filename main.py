import logging
import sys
from data_loader import load_data
from analyzer import analyze_basic, analyze_trend, analyze_mix, analyze_revenue
from visualizer import plot_all_charts
from llm_client import generate_ai_report


def setup_logging() -> None:
    """Configure logging system"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bmw_analysis.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main() -> None:
    """
    Orchestrate complete workflow:
    1. Load and clean data
    2. Print basic and structural analysis
    3. Generate all visualization charts
    4. Call LLM to generate Markdown report
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("Starting BMW sales data analysis workflow")
    logger.info("=" * 50)
    
    try:
        logger.info("Step 1/5: Loading data...")
        df = load_data()
        logger.info(f"Data loaded successfully, total {len(df)} rows")

        logger.info("Step 2/5: Performing basic analysis...")
        analyze_basic(df)
        
        logger.info("Step 3/5: Performing trend analysis...")
        analyze_trend(df)
        
        logger.info("Step 4/5: Performing structural analysis...")
        analyze_mix(df)
        
        logger.info("Step 5/5: Performing revenue analysis...")
        analyze_revenue(df)

        logger.info("Generating visualization charts...")
        plot_all_charts(df)
        logger.info("Chart generation completed")

        logger.info("Calling LLM to generate analysis report...")
        generate_ai_report(df)
        
        logger.info("=" * 50)
        logger.info("All analysis workflows completed successfully")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Analysis workflow execution failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    setup_logging()
    main()



