"""
Visualization Module for Website Traffic Analysis and Model Performance.
Generates publication-quality charts using Matplotlib and Seaborn,
saving all artifacts to outputs/visualizations/.
"""

import logging
from pathlib import Path
from typing import Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from config import config

logger = logging.getLogger(__name__)

# Configure aesthetic visual standards
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
PRIMARY_COLOR = "#2563EB"
SECONDARY_COLOR = "#10B981"
ACCENT_COLOR = "#F59E0B"
ERROR_COLOR = "#EF4444"
TEXT_COLOR = "#1F2937"
GRID_COLOR = "#E5E7EB"

plt.rcParams.update({
    "font.sans-serif": ["Segoe UI", "DejaVu Sans", "Helvetica", "Arial"],
    "axes.edgecolor": "#D1D5DB",
    "axes.linewidth": 1.0,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "grid.linestyle": "--",
    "grid.alpha": 0.7,
    "figure.autolayout": True
})


def generate_all_visualizations(
    processed_df: Optional[pd.DataFrame] = None,
    predictions_df: Optional[pd.DataFrame] = None,
    metrics_df: Optional[pd.DataFrame] = None,
    output_dir: Path = config.VISUALIZATIONS_DIR
) -> None:
    """
    Generates and saves the complete suite of analytical and ML evaluation plots.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Generating visualizations to: {output_dir}")

    # Load data from disk if not provided
    if processed_df is None and config.PROCESSED_DATA_CSV.exists():
        processed_df = pd.read_csv(config.PROCESSED_DATA_CSV)
    if predictions_df is None and config.PREDICTIONS_PATH.exists():
        predictions_df = pd.read_csv(config.PREDICTIONS_PATH)
    if metrics_df is None and config.METRICS_PATH.exists():
        metrics_df = pd.read_csv(config.METRICS_PATH)

    if processed_df is not None:
        processed_df["Date"] = pd.to_datetime(processed_df["Date"])
        _plot_daily_traffic(processed_df, output_dir)
        _plot_monthly_trend(processed_df, output_dir)
        _plot_day_of_week_traffic(processed_df, output_dir)
        _plot_traffic_distribution(processed_df, output_dir)
        _plot_correlation_heatmap(processed_df, output_dir)
        _plot_visitor_breakdown(processed_df, output_dir)

    if metrics_df is not None:
        _plot_model_metrics_comparison(metrics_df, output_dir)

    if predictions_df is not None:
        predictions_df["Date"] = pd.to_datetime(predictions_df["Date"])
        _plot_actual_vs_predicted(predictions_df, output_dir)
        _plot_prediction_errors(predictions_df, output_dir)
        _plot_error_distribution(predictions_df, output_dir)

    logger.info("All visualizations generated successfully.")


def _plot_daily_traffic(df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
    ax.plot(df["Date"], df["Page_Loads"], color=PRIMARY_COLOR, linewidth=1.5, label="Daily Page Views")
    
    # 30-day moving average
    ma30 = df["Page_Loads"].rolling(30).mean()
    ax.plot(df["Date"], ma30, color="#DC2626", linewidth=2.0, linestyle="--", label="30-Day Moving Average")
    
    ax.set_title("Historical Daily Website Traffic (Page Loads)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11, fontweight="medium")
    ax.set_ylabel("Page Loads", fontsize=11, fontweight="medium")
    ax.legend(frameon=True, facecolor="white", edgecolor=GRID_COLOR)
    fig.savefig(output_dir / "01_daily_website_traffic.png", bbox_inches="tight")
    plt.close(fig)


def _plot_monthly_trend(df: pd.DataFrame, output_dir: Path) -> None:
    temp_df = df.copy()
    temp_df["YearMonth"] = temp_df["Date"].dt.to_period("M").astype(str)
    monthly_avg = temp_df.groupby("YearMonth")["Page_Loads"].mean().reset_index()

    fig, ax = plt.subplots(figsize=(14, 5), dpi=300)
    ax.plot(monthly_avg["YearMonth"], monthly_avg["Page_Loads"], marker="o", color=PRIMARY_COLOR, linewidth=2, markersize=5)
    ax.fill_between(monthly_avg["YearMonth"], monthly_avg["Page_Loads"], alpha=0.15, color=PRIMARY_COLOR)
    
    ax.set_title("Monthly Average Website Traffic Trend", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Year-Month", fontsize=11, fontweight="medium")
    ax.set_ylabel("Average Daily Page Loads", fontsize=11, fontweight="medium")
    ax.tick_params(axis="x", rotation=45)
    
    # Show subset of ticks if many
    ticks = range(0, len(monthly_avg), max(1, len(monthly_avg) // 12))
    ax.set_xticks(ticks)
    ax.set_xticklabels([monthly_avg["YearMonth"].iloc[i] for i in ticks], rotation=45)
    
    fig.savefig(output_dir / "02_monthly_traffic_trend.png", bbox_inches="tight")
    plt.close(fig)


def _plot_day_of_week_traffic(df: pd.DataFrame, output_dir: Path) -> None:
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    
    avg_by_day = df.groupby("Day")["Page_Loads"].agg(["mean", "std"]).reindex(day_order).reset_index()
    colors = [PRIMARY_COLOR if d not in ["Saturday", "Sunday"] else SECONDARY_COLOR for d in avg_by_day["Day"]]
    
    bars = ax.bar(avg_by_day["Day"], avg_by_day["mean"], color=colors, edgecolor="#1E40AF", alpha=0.85, width=0.6)
    
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval + 50, f"{int(yval):,}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title("Average Website Traffic by Day of the Week", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Day of Week", fontsize=11, fontweight="medium")
    ax.set_ylabel("Average Page Loads", fontsize=11, fontweight="medium")
    ax.set_ylim(0, max(avg_by_day["mean"]) * 1.15)
    
    fig.savefig(output_dir / "03_traffic_by_day_of_week.png", bbox_inches="tight")
    plt.close(fig)


def _plot_traffic_distribution(df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    sns.histplot(df["Page_Loads"], kde=True, color=PRIMARY_COLOR, ax=ax, bins=40, line_kws={"linewidth": 2})
    
    mean_val = df["Page_Loads"].mean()
    median_val = df["Page_Loads"].median()
    ax.axvline(mean_val, color=ERROR_COLOR, linestyle="--", linewidth=2, label=f"Mean: {mean_val:,.0f}")
    ax.axvline(median_val, color=ACCENT_COLOR, linestyle="-.", linewidth=2, label=f"Median: {median_val:,.0f}")
    
    ax.set_title("Distribution of Website Traffic (Page Loads)", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Page Loads", fontsize=11, fontweight="medium")
    ax.set_ylabel("Frequency", fontsize=11, fontweight="medium")
    ax.legend(frameon=True, facecolor="white")
    fig.savefig(output_dir / "04_traffic_distribution.png", bbox_inches="tight")
    plt.close(fig)


def _plot_correlation_heatmap(df: pd.DataFrame, output_dir: Path) -> None:
    numeric_cols = [c for c in df.select_dtypes(include=[np.number]).columns if c not in ["Row", "Parsed_Date"]]
    if len(numeric_cols) < 2:
        return
    
    corr = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues", ax=ax, cbar_kws={"label": "Pearson Correlation"}, square=True)
    ax.set_title("Feature Correlation Heatmap", fontsize=14, fontweight="bold", pad=12)
    fig.savefig(output_dir / "05_correlation_heatmap.png", bbox_inches="tight")
    plt.close(fig)


def _plot_visitor_breakdown(df: pd.DataFrame, output_dir: Path) -> None:
    if "First_Time_Visits" in df.columns and "Returning_Visits" in df.columns:
        fig, ax = plt.subplots(figsize=(12, 5), dpi=300)
        ax.plot(df["Date"], df["First_Time_Visits"], color=PRIMARY_COLOR, alpha=0.8, label="First-Time Visits")
        ax.plot(df["Date"], df["Returning_Visits"], color=ACCENT_COLOR, alpha=0.9, label="Returning Visits")
        ax.set_title("First-Time vs Returning Website Visitors Over Time", fontsize=14, fontweight="bold", pad=12)
        ax.set_xlabel("Date", fontsize=11, fontweight="medium")
        ax.set_ylabel("Visits Count", fontsize=11, fontweight="medium")
        ax.legend(frameon=True, facecolor="white")
        fig.savefig(output_dir / "06_visitor_breakdown_trend.png", bbox_inches="tight")
        plt.close(fig)


def _plot_model_metrics_comparison(metrics_df: pd.DataFrame, output_dir: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), dpi=300)
    models = metrics_df["Model"]
    
    # 1. RMSE Comparison
    bars1 = axes[0].bar(models, metrics_df["RMSE"], color=[PRIMARY_COLOR, SECONDARY_COLOR], width=0.5)
    axes[0].set_title("Test RMSE (Lower is Better)", fontweight="bold")
    axes[0].set_ylabel("RMSE")
    for b in bars1:
        axes[0].text(b.get_x() + b.get_width()/2, b.get_height() + 5, f"{b.get_height():.1f}", ha="center", fontweight="bold")

    # 2. MAE Comparison
    bars2 = axes[1].bar(models, metrics_df["MAE"], color=[PRIMARY_COLOR, SECONDARY_COLOR], width=0.5)
    axes[1].set_title("Test MAE (Lower is Better)", fontweight="bold")
    axes[1].set_ylabel("MAE")
    for b in bars2:
        axes[1].text(b.get_x() + b.get_width()/2, b.get_height() + 5, f"{b.get_height():.1f}", ha="center", fontweight="bold")

    # 3. R² Comparison
    bars3 = axes[2].bar(models, metrics_df["R2"], color=[PRIMARY_COLOR, SECONDARY_COLOR], width=0.5)
    axes[2].set_title("Test R² (Higher is Better)", fontweight="bold")
    axes[2].set_ylabel("R-Squared")
    axes[2].set_ylim(0, 1.05)
    for b in bars3:
        axes[2].text(b.get_x() + b.get_width()/2, b.get_height() + 0.02, f"{b.get_height():.3f}", ha="center", fontweight="bold")

    plt.suptitle("Linear Regression vs Random Forest Model Evaluation", fontsize=14, fontweight="bold", y=1.03)
    fig.savefig(output_dir / "07_model_metrics_comparison.png", bbox_inches="tight")
    plt.close(fig)


def _plot_actual_vs_predicted(preds_df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 5.5), dpi=300)
    ax.plot(preds_df["Date"], preds_df["Actual_Page_Loads"], label="Actual Traffic", color=PRIMARY_COLOR, linewidth=1.8)
    ax.plot(preds_df["Date"], preds_df["Predicted_Page_Loads"], label="Predicted Traffic", color="#DC2626", linestyle="--", linewidth=1.6)
    
    ax.set_title("Actual vs Predicted Website Traffic on Chronological Test Set", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11, fontweight="medium")
    ax.set_ylabel("Page Loads", fontsize=11, fontweight="medium")
    ax.legend(frameon=True, facecolor="white")
    fig.savefig(output_dir / "08_actual_vs_predicted_traffic.png", bbox_inches="tight")
    plt.close(fig)


def _plot_prediction_errors(preds_df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(14, 4.5), dpi=300)
    ax.plot(preds_df["Date"], preds_df["Prediction_Error"], color="#7C3AED", linewidth=1.2, label="Residual (Pred - Actual)")
    ax.axhline(0, color="black", linestyle="-", linewidth=1.0, alpha=0.7)
    
    ax.set_title("Prediction Error (Residuals) Over Time", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Date", fontsize=11, fontweight="medium")
    ax.set_ylabel("Residual Error", fontsize=11, fontweight="medium")
    ax.legend(frameon=True, facecolor="white")
    fig.savefig(output_dir / "09_prediction_residuals_over_time.png", bbox_inches="tight")
    plt.close(fig)


def _plot_error_distribution(preds_df: pd.DataFrame, output_dir: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
    sns.histplot(preds_df["Prediction_Error"], kde=True, color="#7C3AED", ax=ax, bins=30)
    ax.axvline(0, color="black", linestyle="--", linewidth=1.5)
    
    mean_err = preds_df["Prediction_Error"].mean()
    ax.set_title(f"Residual Distribution (Mean Error: {mean_err:.1f})", fontsize=14, fontweight="bold", pad=12)
    ax.set_xlabel("Prediction Error (Page Loads)", fontsize=11, fontweight="medium")
    ax.set_ylabel("Count", fontsize=11, fontweight="medium")
    fig.savefig(output_dir / "10_residual_error_distribution.png", bbox_inches="tight")
    plt.close(fig)
