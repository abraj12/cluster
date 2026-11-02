"""
Spark Session Management Module.
Provides centralized creation, configuration, and teardown of Apache Spark sessions.
Configured for Windows 11 and Spark MLlib execution.
"""

import os
import sys
import logging
from pyspark.sql import SparkSession
from config import config

logger = logging.getLogger(__name__)


def get_spark_session(app_name: str = config.SPARK_APP_NAME) -> SparkSession:
    """
    Initializes and returns a configured SparkSession.
    Ensures environment variables for Windows compatibility and PySpark workers are set.
    """
    # Ensure worker python matches driver python executable
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    # Suppress verbose Hadoop / Spark console logs
    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(config.SPARK_MASTER)
        .config("spark.driver.memory", config.SPARK_DRIVER_MEMORY)
        .config("spark.sql.shuffle.partitions", str(config.SPARK_SQL_SHUFFLE_PARTITIONS))
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .config("spark.sql.legacy.timeParserPolicy", "CORRECTED")
        .config("spark.ui.showConsoleProgress", "false")
    )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    logger.info(f"Initialized SparkSession: {app_name} (Spark {spark.version})")
    return spark


def stop_spark_session(spark: SparkSession) -> None:
    """
    Safely stops the active SparkSession.
    """
    if spark is not None:
        try:
            spark.stop()
            logger.info("SparkSession stopped successfully.")
        except Exception as e:
            logger.warning(f"Error while stopping SparkSession: {e}")
