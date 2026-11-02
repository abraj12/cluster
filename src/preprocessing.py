"""
Data Preprocessing Module using Apache Spark.
Performs schema normalization, type casting, date parsing, comma stripping from numerical fields,
missing value imputation, duplicate removal, and chronological sorting.
"""

import logging
from pathlib import Path
from pyspark.sql import DataFrame, functions as F
from pyspark.sql.types import DoubleType, IntegerType, DateType
from config import config

logger = logging.getLogger(__name__)


def clean_number_column(col_name: str):
    """
    Strips commas and whitespace from numeric columns formatted as strings
    and casts them to DoubleType.
    """
    return F.regexp_replace(F.trim(F.col(col_name)), ",", "").cast(DoubleType())


def preprocess_data(df: DataFrame) -> DataFrame:
    """
    Executes the full Spark preprocessing pipeline:
    1. Standardizes column names (replacing dots with underscores).
    2. Strips formatting commas and casts metrics to DoubleType.
    3. Parses date column to Spark DateType.
    4. Handles nulls and missing values via imputation.
    5. Deduplicates records based on Date.
    6. Sorts chronologically.
    
    Args:
        df: Raw PySpark DataFrame.
        
    Returns:
        DataFrame: Cleaned PySpark DataFrame.
    """
    logger.info("Starting Spark data preprocessing...")

    # 1. Standardize column names
    for raw_col, std_col in config.COLUMN_MAPPING.items():
        if raw_col in df.columns and raw_col != std_col:
            df = df.withColumnRenamed(raw_col, std_col)

    # 2. Clean numeric columns containing commas (e.g. "2,146" -> 2146.0)
    numeric_traffic_cols = ["Page_Loads", "Unique_Visits", "First_Time_Visits", "Returning_Visits"]
    for col_name in numeric_traffic_cols:
        if col_name in df.columns:
            df = df.withColumn(col_name, clean_number_column(col_name))

    # Clean Day_Of_Week and Row if present
    if "Day_Of_Week" in df.columns:
        df = df.withColumn("Day_Of_Week", F.col("Day_Of_Week").cast(IntegerType()))
    if "Row" in df.columns:
        df = df.withColumn("Row", F.col("Row").cast(IntegerType()))

    # 3. Parse Date column (dataset uses M/d/yyyy e.g. 9/14/2014)
    if "Date" in df.columns:
        df = df.withColumn(
            "Parsed_Date",
            F.coalesce(
                F.to_date(F.col("Date"), "M/d/yyyy"),
                F.to_date(F.col("Date"), "yyyy-MM-dd"),
                F.to_date(F.col("Date"), "MM/dd/yyyy")
            )
        )
        df = df.drop("Date").withColumnRenamed("Parsed_Date", "Date")

    # 4. Check & Impute Missing Values
    null_counts = {col_name: df.filter(F.col(col_name).isNull()).count() for col_name in df.columns}
    logger.info(f"Null counts by column: {null_counts}")

    # Numerical imputation with mean if any missing
    for col_name in numeric_traffic_cols:
        if col_name in df.columns and null_counts.get(col_name, 0) > 0:
            mean_val = df.select(F.mean(col_name)).collect()[0][0] or 0.0
            df = df.fillna({col_name: mean_val})
            logger.info(f"Imputed {null_counts[col_name]} nulls in {col_name} with mean {mean_val:.2f}")

    # Categorical imputation
    if "Day" in df.columns and null_counts.get("Day", 0) > 0:
        df = df.fillna({"Day": "Unknown"})

    # 5. Remove duplicates based on Date
    initial_count = df.count()
    if "Date" in df.columns:
        df = df.dropDuplicates(["Date"])
    else:
        df = df.dropDuplicates()
    dedup_count = df.count()
    if initial_count - dedup_count > 0:
        logger.info(f"Removed {initial_count - dedup_count} duplicate records.")

    # 6. Filter out invalid rows (e.g. non-positive target variable)
    if "Page_Loads" in df.columns:
        df = df.filter(F.col("Page_Loads").isNotNull() & (F.col("Page_Loads") > 0))

    # 7. Sort chronologically to preserve time-series ordering
    if "Date" in df.columns:
        df = df.orderBy("Date")

    final_count = df.count()
    logger.info(f"Preprocessing completed successfully. Retained {final_count} clean records.")
    return df


def save_processed_data(df: DataFrame, output_csv: Path = config.PROCESSED_DATA_CSV) -> None:
    """
    Saves cleaned PySpark DataFrame as a single CSV for easy dashboard and reporting access,
    and also exports as parquet if available.
    """
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    
    # Export cleanly to CSV via pandas for robust single-file local storage
    pdf = df.toPandas()
    pdf.to_csv(str(output_csv), index=False)
    logger.info(f"Saved processed dataset to: {output_csv}")
