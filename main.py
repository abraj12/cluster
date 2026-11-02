"""
Main Pipeline Execution Script.
Executes the end-to-end Big Data & Machine Learning workflow:
1. Initializes Apache Spark session.
2. Loads raw dataset from data/raw/dataset.csv.
3. Cleans, normalizes, and preprocesses data.
4. Performs feature engineering (calendar, lag, rolling features).
5. Trains Linear Regression and Random Forest Regression via Spark MLlib.
6. Evaluates models using RMSE, MAE, and R².
7. Identifies the best-performing model.
8. Generates batch predictions and saves them to outputs/predictions.csv.
9. Exports metrics to outputs/model_metrics.csv.
10. Saves trained models to models/ directory.
11. Generates publication-ready visualizations in outputs/visualizations/.
12. Gracefully stops the Spark session.
"""

import sys
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("MainPipeline")

# Import project modules
from config import config
from src.spark_session import get_spark_session, stop_spark_session
from src.data_loader import load_raw_data
from src.preprocessing import preprocess_data, save_processed_data
from src.feature_engineering import generate_features
from src.model_training import create_chronological_split, train_models
from src.model_evaluation import evaluate_models
from src.prediction import generate_batch_predictions
from src.visualization import generate_all_visualizations


def run_pipeline():
    logger.info("=" * 75)
    logger.info("   WEBSITE TRAFFIC PREDICTION PIPELINE - APACHE SPARK & MLlib")
    logger.info("=" * 75)
    
    spark = None
    try:
        # Step 1: Initialize Spark
        logger.info("\n--- STEP 1: INITIALIZING APACHE SPARK SESSION ---")
        spark = get_spark_session()
        logger.info(f"Apache Spark Session created (Version: {spark.version})")

        # Step 2: Load Raw Data
        logger.info("\n--- STEP 2: LOADING RAW DATASET ---")
        raw_df = load_raw_data(spark, config.RAW_DATA_PATH)
        raw_count = raw_df.count()
        raw_cols = raw_df.columns
        logger.info(f"Loaded raw records: {raw_count}, Columns: {raw_cols}")

        # Step 3: Data Preprocessing
        logger.info("\n--- STEP 3: PREPROCESSING & DATA CLEANING ---")
        cleaned_df = preprocess_data(raw_df)
        save_processed_data(cleaned_df, config.PROCESSED_DATA_CSV)
        cleaned_count = cleaned_df.count()
        logger.info(f"Cleaned dataset rows: {cleaned_count}")

        # Step 4: Feature Engineering
        logger.info("\n--- STEP 4: FEATURE ENGINEERING (CALENDAR, LAG & ROLLING) ---")
        feature_df = generate_features(cleaned_df).cache()
        feature_count = feature_df.count()
        logger.info(f"Engineered feature dataset rows: {feature_count}")
        logger.info(f"Engineered columns: {feature_df.columns}")

        # Step 5: Chronological Train-Test Split
        logger.info("\n--- STEP 5: CHRONOLOGICAL TRAIN-TEST SPLITTING ---")
        train_df, test_df = create_chronological_split(feature_df, config.TRAIN_RATIO)

        # Step 6: Train MLlib Regression Models
        logger.info("\n--- STEP 6: MODEL TRAINING (LINEAR REGRESSION & RANDOM FOREST) ---")
        training_artifacts = train_models(train_df, test_df)
        lr_model = training_artifacts["lr_model"]
        rf_model = training_artifacts["rf_model"]
        train_transformed = training_artifacts["train_transformed"]
        test_transformed = training_artifacts["test_transformed"]

        # Step 7: Model Evaluation
        logger.info("\n--- STEP 7: MODEL EVALUATION (RMSE, MAE, R²) ---")
        metrics_df, best_model_name, detailed_eval = evaluate_models(
            lr_model, rf_model, train_transformed, test_transformed
        )
        
        print("\n" + "=" * 60)
        print("          MODEL PERFORMANCE COMPARISON TABLE")
        print("=" * 60)
        print(metrics_df.to_string(index=False))
        print("=" * 60)
        print(f"--> BEST MODEL SELECTED: {best_model_name}")
        print("=" * 60 + "\n")

        # Step 8: Generate Batch Predictions Using Best Model
        logger.info("\n--- STEP 8: GENERATING PREDICTIONS & RESIDUALS ---")
        best_model = rf_model if best_model_name == "Random Forest" else lr_model
        preds_df = generate_batch_predictions(best_model, test_transformed, config.PREDICTIONS_PATH)
        logger.info(f"Generated {len(preds_df)} predictions. First 5 sample predictions:")
        print(preds_df.head())

        # Step 9: Generate Visualizations
        logger.info("\n--- STEP 9: GENERATING PUBLICATION VISUALIZATIONS ---")
        generate_all_visualizations(
            processed_df=cleaned_df.toPandas(),
            predictions_df=preds_df,
            metrics_df=metrics_df,
            output_dir=config.VISUALIZATIONS_DIR
        )

        logger.info("\n" + "=" * 75)
        logger.info("   PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
        logger.info(f"   Processed Dataset:  {config.PROCESSED_DATA_CSV}")
        logger.info(f"   Saved Models:       {config.MODELS_DIR}")
        logger.info(f"   Model Metrics:      {config.METRICS_PATH}")
        logger.info(f"   Predictions:        {config.PREDICTIONS_PATH}")
        logger.info(f"   Visualizations:     {config.VISUALIZATIONS_DIR}")
        logger.info("=" * 75)

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}", exc_info=True)
        raise e
    finally:
        # Step 10: Clean Spark Teardown
        if spark is not None:
            logger.info("\n--- STEP 10: STOPPING SPARK SESSION ---")
            stop_spark_session(spark)


if __name__ == "__main__":
    run_pipeline()
