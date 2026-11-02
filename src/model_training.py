"""
Machine Learning Model Training Module using Apache Spark MLlib.
Builds ML pipelines, performs chronological train-test splitting,
and trains Linear Regression and Random Forest Regression models.
"""

import logging
from pathlib import Path
from typing import Tuple, Dict, Any
from pyspark.sql import DataFrame, Window, functions as F
from pyspark.ml import Pipeline, PipelineModel
from pyspark.ml.feature import StringIndexer, OneHotEncoder, VectorAssembler, StandardScaler
from pyspark.ml.regression import LinearRegression, LinearRegressionModel, RandomForestRegressor, RandomForestRegressionModel
from config import config

logger = logging.getLogger(__name__)


def create_chronological_split(df: DataFrame, train_ratio: float = config.TRAIN_RATIO) -> Tuple[DataFrame, DataFrame]:
    """
    Performs chronological train/test split to prevent data leakage in time-series data.
    
    Args:
        df: Feature-engineered DataFrame.
        train_ratio: Proportion of earliest records allocated to training (default 0.8).
        
    Returns:
        Tuple[DataFrame, DataFrame]: (train_df, test_df)
    """
    logger.info(f"Performing chronological train-test split (Ratio: {train_ratio:.1%})...")
    
    # Add sequential row number ordered strictly by Date
    window_spec = Window.orderBy("Date")
    df_indexed = df.withColumn("time_index", F.row_number().over(window_spec))
    
    total_records = df_indexed.count()
    cutoff_index = int(total_records * train_ratio)
    
    train_df = df_indexed.filter(F.col("time_index") <= cutoff_index).drop("time_index")
    test_df = df_indexed.filter(F.col("time_index") > cutoff_index).drop("time_index")
    
    train_count = train_df.count()
    test_count = test_df.count()
    
    logger.info(f"Chronological split completed: {train_count} train rows ({train_count/total_records:.1%}), {test_count} test rows ({test_count/total_records:.1%}).")
    return train_df, test_df


def build_feature_pipeline() -> Pipeline:
    """
    Constructs the Spark ML feature transformation pipeline:
    - StringIndexer for categorical columns (with handleInvalid='keep')
    - OneHotEncoder for indexed categorical features
    - VectorAssembler combining encoded categories and numerical features
    - StandardScaler for feature normalization
    """
    stages = []
    
    # Categorical Indexing & Encoding
    indexed_col = "Day_Indexed"
    encoded_col = "Day_Vec"
    
    indexer = StringIndexer(inputCol="Day", outputCol=indexed_col, handleInvalid="keep")
    encoder = OneHotEncoder(inputCol=indexed_col, outputCol=encoded_col)
    stages.extend([indexer, encoder])
    
    # Assemble feature vector
    assembler_inputs = [encoded_col] + config.NUMERICAL_COLS
    assembler = VectorAssembler(inputCols=assembler_inputs, outputCol="assembled_features", handleInvalid="skip")
    stages.append(assembler)
    
    # Standard Scaler
    scaler = StandardScaler(inputCol="assembled_features", outputCol="features", withStd=True, withMean=True)
    stages.append(scaler)
    
    return Pipeline(stages=stages)


def train_models(train_df: DataFrame, test_df: DataFrame) -> Dict[str, Any]:
    """
    Fits feature pipeline, trains Linear Regression and Random Forest models,
    and returns models along with transformed datasets.
    
    Returns:
        Dict containing:
            - 'pipeline_model': Fitted PipelineModel
            - 'lr_model': Trained LinearRegressionModel
            - 'rf_model': Trained RandomForestRegressionModel
            - 'train_transformed': Transformed training DataFrame
            - 'test_transformed': Transformed test DataFrame
            - 'feature_names': List of feature names
    """
    logger.info("Fitting Spark ML Feature Pipeline...")
    pipeline = build_feature_pipeline()
    pipeline_model = pipeline.fit(train_df)
    
    # Transform train and test datasets
    train_transformed = pipeline_model.transform(train_df).cache()
    test_transformed = pipeline_model.transform(test_df).cache()
    
    # 1. Train Linear Regression Model
    logger.info("Training Model 1: Spark MLlib Linear Regression...")
    lr = LinearRegression(
        featuresCol="features",
        labelCol=config.TARGET_COL,
        maxIter=config.LR_MAX_ITER,
        regParam=config.LR_REG_PARAM,
        elasticNetParam=config.LR_ELASTIC_NET_PARAM,
        standardization=False  # Already standardized by StandardScaler stage
    )
    lr_model = lr.fit(train_transformed)
    logger.info("Linear Regression model training completed.")
    
    # 2. Train Random Forest Regressor Model
    logger.info("Training Model 2: Spark MLlib Random Forest Regression...")
    rf = RandomForestRegressor(
        featuresCol="features",
        labelCol=config.TARGET_COL,
        numTrees=config.RF_NUM_TREES,
        maxDepth=config.RF_MAX_DEPTH,
        seed=config.RF_SEED
    )
    rf_model = rf.fit(train_transformed)
    logger.info("Random Forest Regression model training completed.")
    
    # Save Pipeline and Models
    config.PIPELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    pipeline_model.write().overwrite().save(str(config.PIPELINE_PATH))
    logger.info(f"Saved feature pipeline model to: {config.PIPELINE_PATH}")
    
    config.LR_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    lr_model.write().overwrite().save(str(config.LR_MODEL_PATH))
    logger.info(f"Saved Linear Regression model to: {config.LR_MODEL_PATH}")
    
    config.RF_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    rf_model.write().overwrite().save(str(config.RF_MODEL_PATH))
    logger.info(f"Saved Random Forest model to: {config.RF_MODEL_PATH}")
    
    return {
        "pipeline_model": pipeline_model,
        "lr_model": lr_model,
        "rf_model": rf_model,
        "train_transformed": train_transformed,
        "test_transformed": test_transformed
    }


def load_saved_models() -> Dict[str, Any]:
    """
    Loads saved pipeline and regression models from disk.
    """
    logger.info("Loading saved models and feature pipeline from disk...")
    pipeline_model = PipelineModel.load(str(config.PIPELINE_PATH))
    lr_model = LinearRegressionModel.load(str(config.LR_MODEL_PATH))
    rf_model = RandomForestRegressionModel.load(str(config.RF_MODEL_PATH))
    return {
        "pipeline_model": pipeline_model,
        "lr_model": lr_model,
        "rf_model": rf_model
    }
