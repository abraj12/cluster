"""
Data Loader Module.
Responsible for loading raw website traffic data into Apache Spark DataFrames,
validating input files, and providing initial schema and record inspection.
"""

import os
import logging
from pathlib import Path
from typing import Union
from pyspark.sql import SparkSession, DataFrame
from config import config

logger = logging.getLogger(__name__)


def load_raw_data(spark: SparkSession, file_path: Union[str, Path] = config.RAW_DATA_PATH) -> DataFrame:
    """
    Loads raw CSV website traffic dataset into a PySpark DataFrame.
    
    Args:
        spark: Active SparkSession.
        file_path: Path to raw dataset CSV file.
        
    Returns:
        DataFrame: PySpark DataFrame containing raw records.
        
    Raises:
        FileNotFoundError: If the raw dataset does not exist.
        ValueError: If the raw dataset is empty.
    """
    path_obj = Path(file_path)
    if not path_obj.exists():
        logger.error(f"Dataset file not found at: {path_obj.resolve()}")
        raise FileNotFoundError(f"Dataset file not found at: {path_obj.resolve()}")

    if path_obj.stat().st_size == 0:
        logger.error(f"Dataset file is empty at: {path_obj.resolve()}")
        raise ValueError(f"Dataset file is empty at: {path_obj.resolve()}")

    logger.info(f"Loading raw dataset from: {path_obj.resolve()}")
    df = (
        spark.read
        .option("header", "true")
        .option("inferSchema", "true")
        .option("quote", "\"")
        .option("escape", "\"")
        .csv(str(path_obj.resolve()))
    )

    row_count = df.count()
    col_count = len(df.columns)
    logger.info(f"Loaded {row_count} records and {col_count} columns.")

    if row_count == 0:
        raise ValueError(f"Dataset at {path_obj.resolve()} contains no data records.")

    return df


def load_processed_data(spark: SparkSession, file_path: Union[str, Path] = None) -> DataFrame:
    """
    Loads processed dataset from Parquet or CSV.
    """
    if file_path is None:
        if config.PROCESSED_DATA_PARQUET.exists():
            file_path = config.PROCESSED_DATA_PARQUET
        elif config.PROCESSED_DATA_CSV.exists():
            file_path = config.PROCESSED_DATA_CSV
        else:
            raise FileNotFoundError("No processed dataset found. Run preprocessing first.")

    path_obj = Path(file_path)
    if str(path_obj).endswith(".parquet"):
        return spark.read.parquet(str(path_obj.resolve()))
    else:
        return spark.read.option("header", "true").option("inferSchema", "true").csv(str(path_obj.resolve()))
