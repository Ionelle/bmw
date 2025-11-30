"""
Preserved compatibility entry script.

Core logic has been split into the following modules:
- data_loader.py: Handles data loading and cleaning (column name normalization and optional mapping)
- analyzer.py: Handles statistical metric calculations (YoY, ASP, etc.)
- visualizer.py: Generates matplotlib / seaborn charts
- llm_client.py: Encapsulates OpenAI interaction logic and generates Markdown reports
- main.py: Orchestrates the entire workflow

Recommended to run main.py directly:
    python main.py
"""

from main import main


if __name__ == "__main__":
    main()

