"""
Model Evaluation Module using Apache Spark MLlib.
Computes RMSE, MAE, and R-squared metrics on train and test datasets,
identifies the best performing model, and exports results to CSV.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Tuple
import pandas as pd
from pyspark.sql import DataFrame
from pyspark.ml.evaluation import RegressionEvaluator
from config import config

logger = logging.getLogger(__name__)


def evaluate_predictions(predictions_df: DataFrame, label_col: str = config.TARGET_COL, pred_col: str = "prediction") -> Dict[str, float]:
    """
    Computes RMSE, MAE, and R-squared metrics on a predictions DataFrame using Spark MLlib evaluators.
    """
    evaluator_rmse = RegressionEvaluator(labelCol=label_col, predictionCol=pred_col, metricName="rmse")
    evaluator_mae = RegressionEvaluator(labelCol=label_col, predictionCol=pred_col, metricName="mae")
    evaluator_r2 = RegressionEvaluator(labelCol=label_col, predictionCol=pred_col, metricName="r2")
    
    rmse = evaluator_rmse.evaluate(predictions_df)
    mae = evaluator_mae.evaluate(predictions_df)
    r2 = evaluator_r2.evaluate(predictions_df)
    
    return {
        "RMSE": round(rmse, 3),
        "MAE": round(mae, 3),
        "R2": round(r2, 4)
    }


def evaluate_models(
    lr_model,
    rf_model,
    train_transformed: DataFrame,
    test_transformed: DataFrame
) -> Tuple[pd.DataFrame, str, Dict[str, Any]]:
    """
    Evaluates Linear Regression and Random Forest models across train and test sets.
    
    Returns:
        Tuple:
            - metrics_df (pd.DataFrame): Comparison table of metrics.
            - best_model_name (str): Name of best performing model based on test RMSE.
            - detailed_results (Dict): All predictions and metrics dictionaries.
    """
    logger.info("Evaluating models on test and train sets using Spark MLlib evaluators...")
    
    # Generate predictions
    lr_train_preds = lr_model.transform(train_transformed)
    lr_test_preds = lr_model.transform(test_transformed)
    
    rf_train_preds = rf_model.transform(train_transformed)
    rf_test_preds = rf_model.transform(test_transformed)
    
    # Calculate metrics
    lr_train_metrics = evaluate_predictions(lr_train_preds)
    lr_test_metrics = evaluate_predictions(lr_test_preds)
    
    rf_train_metrics = evaluate_predictions(rf_train_preds)
    rf_test_metrics = evaluate_predictions(rf_test_preds)
    
    logger.info(f"Linear Regression Test Metrics: RMSE={lr_test_metrics['RMSE']}, MAE={lr_test_metrics['MAE']}, R2={lr_test_metrics['R2']}")
    logger.info(f"Random Forest Test Metrics:     RMSE={rf_test_metrics['RMSE']}, MAE={rf_test_metrics['MAE']}, R2={rf_test_metrics['R2']}")
    
    # Comparison table
    records = [
        {
            "Model": "Linear Regression",
            "RMSE": lr_test_metrics["RMSE"],
            "MAE": lr_test_metrics["MAE"],
            "R2": lr_test_metrics["R2"],
            "Train_RMSE": lr_train_metrics["RMSE"],
            "Train_MAE": lr_train_metrics["MAE"],
            "Train_R2": lr_train_metrics["R2"]
        },
        {
            "Model": "Random Forest",
            "RMSE": rf_test_metrics["RMSE"],
            "MAE": rf_test_metrics["MAE"],
            "R2": rf_test_metrics["R2"],
            "Train_RMSE": rf_train_metrics["RMSE"],
            "Train_MAE": rf_train_metrics["MAE"],
            "Train_R2": rf_train_metrics["R2"]
        }
    ]
    metrics_df = pd.DataFrame(records)
    
    # Select best model (lowest test RMSE and highest R2)
    if rf_test_metrics["RMSE"] <= lr_test_metrics["RMSE"]:
        best_model_name = "Random Forest"
    else:
        best_model_name = "Linear Regression"
        
    logger.info(f"--> Best Performing Model: {best_model_name} (Lowest Test RMSE: {min(lr_test_metrics['RMSE'], rf_test_metrics['RMSE'])})")
    
    # Save metrics to CSV
    config.METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(str(config.METRICS_PATH), index=False)
    logger.info(f"Saved evaluation metrics to: {config.METRICS_PATH}")
    
    detailed = {
        "lr_test_preds": lr_test_preds,
        "rf_test_preds": rf_test_preds,
        "lr_metrics": lr_test_metrics,
        "rf_metrics": rf_test_metrics
    }
    
    return metrics_df, best_model_name, detailed
