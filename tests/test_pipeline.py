"""
Unit and Integration Tests for Website Traffic Prediction Pipeline.
Validates SparkSession initialization, data loading, preprocessing,
feature engineering, chronological train-test split, and outputs.
"""

import pytest
from pathlib import Path
import pandas as pd
from config import config
from src.spark_session import get_spark_session, stop_spark_session
from src.data_loader import load_raw_data
from src.preprocessing import preprocess_data
from src.feature_engineering import generate_features
from src.model_training import create_chronological_split


@pytest.fixture(scope="session")
def spark():
    """Session-scoped SparkSession fixture for testing."""
    session = get_spark_session(app_name="TestWebsiteTrafficPipeline")
    yield session
    stop_spark_session(session)


def test_raw_data_file_exists():
    """Verify raw dataset exists and is non-empty."""
    assert config.RAW_DATA_PATH.exists(), f"Raw dataset not found at {config.RAW_DATA_PATH}"
    assert config.RAW_DATA_PATH.stat().st_size > 0, "Raw dataset file is empty"


def test_spark_session_initialization(spark):
    """Verify SparkSession initializes with active SparkContext."""
    assert spark is not None
    assert spark.version.startswith("3.")


def test_data_loader(spark):
    """Verify load_raw_data loads records with required columns."""
    df = load_raw_data(spark, config.RAW_DATA_PATH)
    count = df.count()
    assert count > 2000, f"Expected >2000 records, got {count}"
    assert "Page.Loads" in df.columns or "Page_Loads" in df.columns
    assert "Date" in df.columns


def test_preprocessing_pipeline(spark):
    """Verify preprocessing correctly converts formatted numeric columns and dates."""
    raw_df = load_raw_data(spark, config.RAW_DATA_PATH)
    cleaned_df = preprocess_data(raw_df)
    
    assert "Page_Loads" in cleaned_df.columns
    assert "Unique_Visits" in cleaned_df.columns
    assert "Date" in cleaned_df.columns
    
    # Verify no nulls in Page_Loads
    null_count = cleaned_df.filter(cleaned_df.Page_Loads.isNull()).count()
    assert null_count == 0, f"Found {null_count} nulls in target column Page_Loads"
    
    # Verify Page_Loads are positive
    invalid_count = cleaned_df.filter(cleaned_df.Page_Loads <= 0).count()
    assert invalid_count == 0, f"Found {invalid_count} non-positive Page_Loads"


def test_feature_engineering(spark):
    """Verify feature engineering produces calendar, lag, and rolling features."""
    raw_df = load_raw_data(spark, config.RAW_DATA_PATH)
    cleaned_df = preprocess_data(raw_df)
    features_df = generate_features(cleaned_df)
    
    expected_cols = [
        "Year", "Month", "Day_Num", "Week_Of_Year", "Is_Weekend",
        "Lag_1_Page_Loads", "Lag_2_Page_Loads", "Lag_7_Page_Loads",
        "Rolling_7_Page_Loads", "Rolling_14_Page_Loads"
    ]
    for col in expected_cols:
        assert col in features_df.columns, f"Missing engineered feature: {col}"
        
    # Check that warm-up nulls are dropped
    null_lag7 = features_df.filter(features_df.Lag_7_Page_Loads.isNull()).count()
    assert null_lag7 == 0, "Features DataFrame contains unhandled nulls in Lag_7_Page_Loads"


def test_chronological_split(spark):
    """Verify chronological split divides dataset into chronological sets without overlap."""
    raw_df = load_raw_data(spark, config.RAW_DATA_PATH)
    cleaned_df = preprocess_data(raw_df)
    features_df = generate_features(cleaned_df)
    
    train_df, test_df = create_chronological_split(features_df, train_ratio=0.8)
    
    max_train_date = train_df.agg({"Date": "max"}).collect()[0][0]
    min_test_date = test_df.agg({"Date": "min"}).collect()[0][0]
    
    assert max_train_date < min_test_date, (
        f"Chronological violation! Max train date ({max_train_date}) is not strictly before Min test date ({min_test_date})"
    )


def test_outputs_and_visualizations_exist():
    """Verify output artifacts and visualizations were generated."""
    assert config.METRICS_PATH.exists(), f"Missing {config.METRICS_PATH}"
    assert config.PREDICTIONS_PATH.exists(), f"Missing {config.PREDICTIONS_PATH}"
    
    metrics_df = pd.read_csv(config.METRICS_PATH)
    assert len(metrics_df) == 2, "Expected 2 models in metrics CSV"
    assert "RMSE" in metrics_df.columns
    assert "R2" in metrics_df.columns
    
    preds_df = pd.read_csv(config.PREDICTIONS_PATH)
    assert len(preds_df) > 0, "Predictions CSV is empty"
    assert "Actual_Page_Loads" in preds_df.columns
    assert "Predicted_Page_Loads" in preds_df.columns
    
    viz_files = list(config.VISUALIZATIONS_DIR.glob("*.png"))
    assert len(viz_files) >= 10, f"Expected at least 10 visualization charts, found {len(viz_files)}"
