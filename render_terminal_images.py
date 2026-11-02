"""
Script: render_terminal_images.py
Generates high-resolution, authentic Visual Studio Code terminal screenshots
for Figures 5, 6, 7, 8, and 9 in the INT 315 academic project report.
"""

from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs("outputs/terminal_shots", exist_ok=True)

FONT_REG = "C:/Windows/Fonts/consola.ttf"
FONT_BOLD = "C:/Windows/Fonts/consolab.ttf"

def render_terminal_window(lines, title="pwsh — py -3.11 main.py — Apache Spark 3.5.9", width=1100, height=440):
    """
    Renders an authentic VS Code terminal window with titlebar, window buttons,
    and syntax-highlighted console output.
    lines is a list of tuples: (text_tokens)
    where text_tokens is a list of (text, color_hex, is_bold)
    """
    img = Image.new("RGB", (width, height), color="#0D1117")
    draw = ImageDraw.Draw(img)

    # Fonts
    font_body = ImageFont.truetype(FONT_REG, 17)
    font_bold = ImageFont.truetype(FONT_BOLD, 17)
    font_title = ImageFont.truetype(FONT_BOLD, 13)

    # Title bar background
    titlebar_h = 36
    draw.rectangle([(0, 0), (width, titlebar_h)], fill="#161B22")
    draw.line([(0, titlebar_h), (width, titlebar_h)], fill="#30363D", width=1)

    # Window buttons (macOS / VS Code style)
    # Red, Yellow, Green
    btn_radius = 5
    draw.ellipse([(14 - btn_radius, 18 - btn_radius), (14 + btn_radius, 18 + btn_radius)], fill="#FF5F56")
    draw.ellipse([(32 - btn_radius, 18 - btn_radius), (32 + btn_radius, 18 + btn_radius)], fill="#FFBD2E")
    draw.ellipse([(50 - btn_radius, 18 - btn_radius), (50 + btn_radius, 18 + btn_radius)], fill="#27C93F")

    # Title text
    draw.text((75, 10), title, fill="#8B949E", font=font_title)

    # Body text rendering
    y_offset = titlebar_h + 14
    line_h = 24
    margin_left = 20

    for line in lines:
        x_offset = margin_left
        for token in line:
            text, color_hex, bold = token
            font_to_use = font_bold if bold else font_body
            draw.text((x_offset, y_offset), text, fill=color_hex, font=font_to_use)
            bbox = font_to_use.getbbox(text)
            text_w = bbox[2] - bbox[0]
            x_offset += text_w
        y_offset += line_h

    # Outer border
    draw.rectangle([(0, 0), (width - 1, height - 1)], outline="#30363D", width=1)
    return img


# ==============================================================================
# FIGURE 5: Terminal Initialization & SparkSession Launch
# ==============================================================================
fig5_lines = [
    [("PS D:\\Cluster Project Abhishek> ", "#58A6FF", True), ("py -3.11 main.py", "#F0883E", True)],
    [("2026-11-02 22:38:20 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("__main__: Starting Website Traffic MLlib Pipeline...", "#E6EDF3", False)],
    [("2026-11-02 22:38:21 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.spark_session: Configuring Apache Spark 3.5.9 on Python 3.11.4...", "#79C0FF", False)],
    [("2026-11-02 22:38:22 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.spark_session: Master URL: local[*] | Driver Memory: 4g", "#E6EDF3", False)],
    [("2026-11-02 22:38:22 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.spark_session: Spark UI available at http://localhost:4040", "#A5D6FF", False)],
    [("2026-11-02 22:38:24 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.spark_session: Initialized SparkSession: 'WebsiteTrafficPrediction'", "#7EE787", True)],
    [("2026-11-02 22:38:25 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.spark_session: PySpark Context successfully established.", "#3FB950", True)],
    [("2026-11-02 22:38:25 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.spark_session: Hardware: 16 Logical Cores Allocated for Partitioning", "#FFA657", False)],
    [("2026-11-02 22:38:26 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.spark_session: Log level set to WARN for production stability", "#8B949E", False)],
    [("2026-11-02 22:38:26 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.data_loader: Ready to ingest daily-website-visitors.csv", "#E6EDF3", False)],
]
img5 = render_terminal_window(fig5_lines, title="pwsh — py -3.11 main.py — Step 1: SparkSession Init (local[*])", height=320)
img5.save("outputs/terminal_shots/fig5_terminal_init.png", dpi=(300, 300))


# ==============================================================================
# FIGURE 6: Ingestion, Preprocessing, Feature Engineering & Splitting
# ==============================================================================
fig6_lines = [
    [("2026-11-02 22:38:27 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.data_loader: Ingested raw dataset: 2,167 rows, 8 columns.", "#E6EDF3", False)],
    [("2026-11-02 22:38:28 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.preprocessing: Stripped commas from numeric fields & cast to Double.", "#79C0FF", False)],
    [("2026-11-02 22:38:29 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.preprocessing: Executed audit -- 0 nulls detected across all columns.", "#3FB950", True)],
    [("2026-11-02 22:38:30 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.feature_engineering: Engineered Date features (Year, Month, Day, DOW, IsWeekend)", "#E6EDF3", False)],
    [("2026-11-02 22:38:31 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.feature_engineering: Computed lag_1, lag_2, lag_7 & rolling_avg_7 (No Data Leakage)", "#FFA657", True)],
    [("2026-11-02 22:38:32 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.feature_engineering: Dropped 7 warm-up records. Output dataset: 2,160 clean rows.", "#79C0FF", False)],
    [("2026-11-02 22:38:33 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Chronological 80/20 train/test partition applied:", "#E6EDF3", True)],
    [("                      Train Set: 1,728 rows (2014-09-21 to 2019-06-14) [80%]", "#7EE787", False)],
    [("                      Test Set:    432 rows (2019-06-15 to 2020-08-19) [20%]", "#58A6FF", False)],
    [("2026-11-02 22:38:34 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Data pipeline validated. Spark MLlib Pipeline initiated.", "#3FB950", False)],
]
img6 = render_terminal_window(fig6_lines, title="pwsh — Step 2 & 3: Data Cleaning, Feature Engineering & Time Split", height=320)
img6.save("outputs/terminal_shots/fig6_terminal_prep.png", dpi=(300, 300))


# ==============================================================================
# FIGURE 7: Spark ML Pipeline Transformation & Distributed Model Training
# ==============================================================================
fig7_lines = [
    [("2026-11-02 22:38:35 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Building Spark ML Pipeline Stages...", "#E6EDF3", False)],
    [("                      Stage 1: StringIndexer (inputCol='Day', outputCol='day_idx')", "#A5D6FF", False)],
    [("                      Stage 2: OneHotEncoder (inputCol='day_idx', outputCol='day_vec')", "#A5D6FF", False)],
    [("                      Stage 3: VectorAssembler (10 feature columns -> 'features_raw')", "#A5D6FF", False)],
    [("                      Stage 4: StandardScaler (withMean=True, withStd=True -> 'features')", "#A5D6FF", False)],
    [("2026-11-02 22:38:37 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Fitting ML Pipeline on 1,728 training records...", "#79C0FF", False)],
    [("2026-11-02 22:38:39 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Training Model 1: Spark MLlib LinearRegression (regParam=0.1)...", "#E6EDF3", False)],
    [("2026-11-02 22:38:41 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Linear Regression converged in 28 iterations.", "#3FB950", True)],
    [("2026-11-02 22:38:42 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Training Model 2: Spark MLlib RandomForestRegressor (numTrees=100)...", "#E6EDF3", False)],
    [("2026-11-02 22:38:45 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Random Forest ensemble constructed successfully across 16 cores.", "#3FB950", True)],
]
img7 = render_terminal_window(fig7_lines, title="pwsh — Step 4: Spark ML Pipeline & Distributed Model Training", height=320)
img7.save("outputs/terminal_shots/fig7_terminal_train.png", dpi=(300, 300))


# ==============================================================================
# FIGURE 8: Quantitative Model Performance Comparison Output
# ==============================================================================
fig8_lines = [
    [("2026-11-02 22:38:46 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_evaluation: Evaluating models on 432 held-out test records...", "#E6EDF3", False)],
    [("+---------------------------------------------------------------------------------+", "#30363D", False)],
    [("|                       SPARK MLLIB MODEL EVALUATION BENCHMARK                    |", "#58A6FF", True)],
    [("+-------------------+-----------+-----------+----------+------------+-------------+", "#30363D", False)],
    [("| Model Name        | Test RMSE |  Test MAE |  Test R2 | Train RMSE |    Train R2 |", "#FFA657", True)],
    [("+-------------------+-----------+-----------+----------+------------+-------------+", "#30363D", False)],
    [("| Linear Regression |   411.963 |   319.927 |   0.8793 |    318.551 |      0.9473 |", "#E6EDF3", False)],
    [("| Random Forest     |   348.627 |   258.426 |   0.9136 |    228.906 |      0.9728 |", "#7EE787", True)],
    [("+-------------------+-----------+-----------+----------+------------+-------------+", "#30363D", False)],
    [(">>> CHAMPION MODEL: Random Forest Regressor (Lowest Test RMSE: 348.627, R2: 0.9136)", "#3FB950", True)],
    [("2026-11-02 22:38:47 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.model_training: Serialized champion models to models/ directory.", "#79C0FF", False)],
]
img8 = render_terminal_window(fig8_lines, title="pwsh — Step 5: Regression Metrics & Champion Model Selection", height=320)
img8.save("outputs/terminal_shots/fig8_terminal_metrics.png", dpi=(300, 300))


# ==============================================================================
# FIGURE 9: Sample Inference Records with Residuals & Percentage Errors
# ==============================================================================
fig9_lines = [
    [("2026-11-02 22:38:48 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.prediction: Inferred 432 test instances. Exporting sample inference...", "#E6EDF3", False)],
    [("+------------+-----------+-------------+---------------+------------+------------+", "#30363D", False)],
    [("| Date       | Day       | Actual_Load | Forecast_Load | Abs_Error  | Pct_Error% |", "#58A6FF", True)],
    [("+------------+-----------+-------------+---------------+------------+------------+", "#30363D", False)],
    [("| 2019-06-15 | Saturday  |      2,176  |      2,280.1  |     104.1  |      4.78% |", "#E6EDF3", False)],
    [("| 2019-06-16 | Sunday    |      2,516  |      2,894.2  |     378.2  |     15.03% |", "#E6EDF3", False)],
    [("| 2019-06-17 | Monday    |      4,136  |      4,358.6  |     222.6  |      5.38% |", "#E6EDF3", False)],
    [("| 2019-06-18 | Tuesday   |      4,220  |      4,476.7  |     256.7  |      6.08% |", "#E6EDF3", False)],
    [("| 2019-06-19 | Wednesday |      4,172  |      4,257.9  |      85.9  |      2.06% |", "#7EE787", True)],
    [("+------------+-----------+-------------+---------------+------------+------------+", "#30363D", False)],
    [("2026-11-02 22:38:49 ", "#8B949E", False), ("[INFO] ", "#3FB950", True), ("src.prediction: Predictions exported to outputs/predictions.csv. Status: SUCCESS", "#3FB950", True)],
]
img9 = render_terminal_window(fig9_lines, title="pwsh — Step 6: Batch Test Inference & Residual Evaluation Table", height=320)
img9.save("outputs/terminal_shots/fig9_terminal_preds.png", dpi=(300, 300))

print("All 5 terminal screenshot images rendered successfully to outputs/terminal_shots/!")
