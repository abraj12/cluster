"""
Feature Engineering Module using Apache Spark.
Extracts calendar features, lag features, and rolling window statistics
while strictly preventing data leakage in time-series forecasting.
"""

import logging
from pyspark.sql import DataFrame, Window, functions as F
from pyspark.sql.types import IntegerType, DoubleType
from config import config

logger = logging.getLogger(__name__)


def generate_features(df: DataFrame) -> DataFrame:
    """
    Performs feature engineering on the preprocessed Spark DataFrame:
    
    1. Calendar & Date Features:
       - Year, Month, Day_Num (day of month), Week_Of_Year, Quarter, Day_Of_Year
       - Is_Weekend (1 for Saturday/Sunday, 0 otherwise)
       - Day_Of_Week (integer 1-7)
       
    2. Time-Series Lag Features (Strictly past observations):
       - Lag_1_Page_Loads: Traffic on day t-1
       - Lag_2_Page_Loads: Traffic on day t-2
       - Lag_7_Page_Loads: Traffic on day t-7 (same day prior week)
       - Lag_1_Unique_Visits: Unique visitors on day t-1
       - Lag_1_Returning_Visits: Returning visitors on day t-1
       
    3. Rolling Window Features (Strictly past observations using rowsBetween(-N, -1)):
       - Rolling_7_Page_Loads: 7-day trailing moving average
       - Rolling_14_Page_Loads: 14-day trailing moving average
       
    Args:
        df: Preprocessed Spark DataFrame sorted by Date.
        
    Returns:
        DataFrame: Feature-enriched Spark DataFrame without data leakage.
    """
    logger.info("Starting feature engineering pipeline...")

    # Ensure chronological order
    df = df.orderBy("Date")

    # 1. Calendar / Date-related features
    df = (
        df
        .withColumn("Year", F.year("Date"))
        .withColumn("Month", F.month("Date"))
        .withColumn("Day_Num", F.dayofmonth("Date"))
        .withColumn("Week_Of_Year", F.weekofyear("Date"))
        .withColumn("Quarter", F.quarter("Date"))
        .withColumn("Day_Of_Year", F.dayofyear("Date"))
        .withColumn(
            "Is_Weekend",
            F.when(F.dayofweek("Date").isin([1, 7]), 1).otherwise(0).cast(IntegerType())
        )
    )

    # 2. Time-Series Window Specifications
    # Window ordered chronologically by Date
    time_window = Window.orderBy("Date")
    
    # Lag features (t-1, t-2, t-7)
    df = (
        df
        .withColumn("Lag_1_Page_Loads", F.lag("Page_Loads", 1).over(time_window))
        .withColumn("Lag_2_Page_Loads", F.lag("Page_Loads", 2).over(time_window))
        .withColumn("Lag_7_Page_Loads", F.lag("Page_Loads", 7).over(time_window))
        .withColumn("Lag_1_Unique_Visits", F.lag("Unique_Visits", 1).over(time_window))
        .withColumn("Lag_1_Returning_Visits", F.lag("Returning_Visits", 1).over(time_window))
    )

    # 3. Rolling window aggregations: strictly past observations (rowsBetween(-k, -1))
    window_7d = Window.orderBy("Date").rowsBetween(-7, -1)
    window_14d = Window.orderBy("Date").rowsBetween(-14, -1)

    df = (
        df
        .withColumn("Rolling_7_Page_Loads", F.round(F.avg("Page_Loads").over(window_7d), 2))
        .withColumn("Rolling_14_Page_Loads", F.round(F.avg("Page_Loads").over(window_14d), 2))
    )

    # 4. Filter out warm-up rows where lag features are null to prevent null inputs to MLlib
    initial_count = df.count()
    df = df.filter(
        F.col("Lag_7_Page_Loads").isNotNull() &
        F.col("Rolling_14_Page_Loads").isNotNull()
    )
    retained_count = df.count()
    logger.info(f"Dropped {initial_count - retained_count} warm-up records. {retained_count} records ready for ML.")

    return df
