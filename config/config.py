"""
Configuration module for Website Traffic Prediction.
Centralizes all paths, model hyperparameters, feature definitions, and Spark settings.
"""

from pathlib import Path
import os
import sys

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data paths
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "dataset.csv"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
PROCESSED_DATA_CSV = PROCESSED_DATA_DIR / "cleaned_traffic_data.csv"
PROCESSED_DATA_PARQUET = PROCESSED_DATA_DIR / "cleaned_traffic_data.parquet"

# Models paths
MODELS_DIR = BASE_DIR / "models"
LR_MODEL_PATH = MODELS_DIR / "linear_regression"
RF_MODEL_PATH = MODELS_DIR / "random_forest"
PIPELINE_PATH = MODELS_DIR / "pipeline_model"

# Outputs paths
OUTPUTS_DIR = BASE_DIR / "outputs"
PREDICTIONS_PATH = OUTPUTS_DIR / "predictions.csv"
METRICS_PATH = OUTPUTS_DIR / "model_metrics.csv"
VISUALIZATIONS_DIR = OUTPUTS_DIR / "visualizations"

# Spark configuration
SPARK_APP_NAME = "WebsiteTrafficPrediction"
SPARK_MASTER = "local[*]"
SPARK_DRIVER_MEMORY = "4g"
SPARK_EXECUTOR_MEMORY = "2g"
SPARK_SQL_SHUFFLE_PARTITIONS = 4

# Python executable environment for PySpark
PYTHON_EXE = sys.executable

# Target and Column names
TARGET_COL = "Page_Loads"
RAW_TARGET_COL = "Page.Loads"
RAW_DATE_COL = "Date"

# Core raw column mappings for normalization
COLUMN_MAPPING = {
    "Row": "Row",
    "Day": "Day",
    "Day.Of.Week": "Day_Of_Week",
    "Date": "Date",
    "Page.Loads": "Page_Loads",
    "Unique.Visits": "Unique_Visits",
    "First.Time.Visits": "First_Time_Visits",
    "Returning.Visits": "Returning_Visits"
}

# Feature definitions
CATEGORICAL_COLS = ["Day"]

# Continuous numerical and engineered features used for model input
NUMERICAL_COLS = [
    "Day_Of_Week",
    "Year",
    "Month",
    "Day_Num",
    "Week_Of_Year",
    "Is_Weekend",
    "Quarter",
    "Day_Of_Year",
    "Lag_1_Page_Loads",
    "Lag_2_Page_Loads",
    "Lag_7_Page_Loads",
    "Rolling_7_Page_Loads",
    "Rolling_14_Page_Loads",
    "Lag_1_Unique_Visits",
    "Lag_1_Returning_Visits",
]

# Chronological Train-Test Split (Time-Series)
TRAIN_RATIO = 0.8
RANDOM_SEED = 42

# Model Hyperparameters
LR_REG_PARAM = 0.1
LR_ELASTIC_NET_PARAM = 0.2
LR_MAX_ITER = 100

RF_NUM_TREES = 50
RF_MAX_DEPTH = 8
RF_SEED = 42
