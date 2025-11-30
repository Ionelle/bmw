import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

# Raw Excel data file path
DATA_FILE = Path(__file__).with_name("BMW sales data (2020-2024).xlsx")


# If you need to map "original column names -> standard column names", maintain the mapping here
# For example: {"year": "Year", "sales_volume": "Sales_Volume"}
COLUMN_RENAME_MAP: dict[str, str] = {}


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic column name cleaning and optional mapping:
    - Remove leading and trailing spaces
    - Apply mapping defined in COLUMN_RENAME_MAP (if any)
    """
    logger.debug(f"Starting to normalize column names, original columns: {list(df.columns)}")
    cleaned = df.copy()
    cleaned.columns = [str(c).strip() for c in cleaned.columns]

    if COLUMN_RENAME_MAP:
        logger.info(f"Applying column name mapping: {COLUMN_RENAME_MAP}")
        cleaned = cleaned.rename(columns=COLUMN_RENAME_MAP)
    
    logger.debug(f"Normalized column names: {list(cleaned.columns)}")
    return cleaned


def load_data() -> pd.DataFrame:
    """
    Load BMW 2020–2024 sales data from local Excel file and perform basic column name cleaning/mapping.
    """
    logger.info(f"Starting to load data file: {DATA_FILE}")
    
    if not DATA_FILE.exists():
        logger.error(f"Data file does not exist: {DATA_FILE}")
        raise FileNotFoundError(f"Data file not found: {DATA_FILE}")

    try:
        # Read the first worksheet by default, modify sheet_name if you need to specify
        logger.debug("Reading Excel file...")
        df = pd.read_excel(DATA_FILE)
        logger.info(f"Successfully read Excel file, original data shape: {df.shape}")
        
        df = _normalize_column_names(df)
        logger.info(f"Data loading completed, final data shape: {df.shape}")
        return df
        
    except Exception as e:
        logger.error(f"Error occurred while loading data file: {e}", exc_info=True)
        raise



