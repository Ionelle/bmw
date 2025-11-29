import logging
import sys
from data_loader import load_data
from analyzer import analyze_basic, analyze_trend, analyze_mix, analyze_revenue
from visualizer import plot_all_charts
from llm_client import generate_ai_report


def setup_logging() -> None:
    """配置日志系统"""
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
    编排完整工作流：
    1. 读取并清洗数据
    2. 打印基础与结构性分析
    3. 生成所有可视化图表
    4. 调用 LLM 生成 Markdown 报告
    """
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("开始BMW销售数据分析流程")
    logger.info("=" * 50)
    
    try:
        logger.info("步骤 1/5: 加载数据...")
        df = load_data()
        logger.info(f"数据加载成功，共 {len(df)} 行数据")

        logger.info("步骤 2/5: 执行基础分析...")
        analyze_basic(df)
        
        logger.info("步骤 3/5: 执行趋势分析...")
        analyze_trend(df)
        
        logger.info("步骤 4/5: 执行结构分析...")
        analyze_mix(df)
        
        logger.info("步骤 5/5: 执行收入分析...")
        analyze_revenue(df)

        logger.info("生成可视化图表...")
        plot_all_charts(df)
        logger.info("图表生成完成")

        logger.info("调用LLM生成分析报告...")
        generate_ai_report(df)
        
        logger.info("=" * 50)
        logger.info("所有分析流程执行完成")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"分析流程执行失败: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    setup_logging()
    main()



