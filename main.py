from data_loader import load_data
from analyzer import analyze_basic, analyze_trend, analyze_mix, analyze_revenue
from visualizer import plot_all_charts
from llm_client import generate_ai_report


def main() -> None:
    """
    编排完整工作流：
    1. 读取并清洗数据
    2. 打印基础与结构性分析
    3. 生成所有可视化图表
    4. 调用 LLM 生成 Markdown 报告
    """
    df = load_data()

    analyze_basic(df)
    analyze_trend(df)
    analyze_mix(df)
    analyze_revenue(df)

    plot_all_charts(df)

    # 生成基于 GPT-5 的叙述性商业报告
    generate_ai_report(df)


if __name__ == "__main__":
    main()



