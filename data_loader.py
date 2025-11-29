import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# 原始 Excel 数据文件路径
DATA_FILE = Path(__file__).with_name("BMW sales data (2020-2024).xlsx")


# 如需做「原始列名 -> 标准列名」映射，可以在这里维护映射关系
# 例如：{"year": "Year", "sales_volume": "Sales_Volume"}
COLUMN_RENAME_MAP: dict[str, str] = {}


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    对列名做基础清洗与可选映射：
    - 去除首尾空格
    - 应用 COLUMN_RENAME_MAP 中定义的映射（如果有）
    """
    logger.debug(f"开始标准化列名，原始列: {list(df.columns)}")
    cleaned = df.copy()
    cleaned.columns = [str(c).strip() for c in cleaned.columns]

    if COLUMN_RENAME_MAP:
        logger.info(f"应用列名映射: {COLUMN_RENAME_MAP}")
        cleaned = cleaned.rename(columns=COLUMN_RENAME_MAP)
    
    logger.debug(f"标准化后的列名: {list(cleaned.columns)}")
    return cleaned


def load_data() -> pd.DataFrame:
    """
    从本地 Excel 文件读取 BMW 2020–2024 销量数据，并做基础列名清洗/映射。
    """
    logger.info(f"开始加载数据文件: {DATA_FILE}")
    
    if not DATA_FILE.exists():
        logger.error(f"数据文件不存在: {DATA_FILE}")
        raise FileNotFoundError(f"找不到数据文件: {DATA_FILE}")

    try:
        # 默认读取第一个工作表，如需指定请修改 sheet_name
        logger.debug("正在读取Excel文件...")
        df = pd.read_excel(DATA_FILE)
        logger.info(f"成功读取Excel文件，原始数据形状: {df.shape}")
        
        df = _normalize_column_names(df)
        logger.info(f"数据加载完成，最终数据形状: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"加载数据文件时出错: {e}", exc_info=True)
        raise



