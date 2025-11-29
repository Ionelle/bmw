"""
保留的兼容入口脚本。

核心逻辑已拆分为以下模块：
- data_loader.py: 负责数据读取和清洗（列名规范化与可选映射）
- analyzer.py: 负责计算统计指标（YoY, ASP 等）
- visualizer.py: 负责生成 matplotlib / seaborn 图表
- llm_client.py: 封装与 OpenAI 的交互逻辑并生成 Markdown 报告
- main.py: 编排整个工作流

推荐直接运行 main.py：
    python main.py
"""

from main import main


if __name__ == "__main__":
    main()

