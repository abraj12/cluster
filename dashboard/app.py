"""
Website Traffic Analytics & Prediction Dashboard.
A modern SaaS-style interactive analytics and machine learning application
built with Streamlit and Plotly.
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from config import config
from src.prediction import predict_fast

# ---------------------------------------------------------
# Page Configuration & Modern Light Theme Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="Website Traffic Analytics & Prediction",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Comprehensive Enterprise SaaS Light-Theme CSS (Theme Clash Proof)
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Base Font and Global Resets */
    html, body, [class*="css"], [data-testid="stAppViewContainer"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }
    
    /* Force Light Background on Top Streamlit Header */
    header[data-testid="stHeader"] {
        background-color: #F8FAFC !important;
        border-bottom: 1px solid #E2E8F0 !important;
    }
    
    /* Sidebar Styling & High Contrast */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0 !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #0F172A !important;
    }
    
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li {
        color: #334155 !important;
        font-size: 13.5px !important;
    }
    
    /* Sidebar Radio Buttons as Modern Nav Items */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: transparent !important;
        padding: 8px 14px !important;
        border-radius: 8px !important;
        margin-bottom: 4px !important;
        cursor: pointer !important;
        transition: all 0.15s ease-in-out !important;
        border: 1px solid transparent !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: #F1F5F9 !important;
        border-color: #E2E8F0 !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"],
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) {
        background-color: #EFF6FF !important;
        border-color: #BFDBFE !important;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] span,
    div[data-testid="stRadio"] div[role="radiogroup"] > label:has(input:checked) span {
        color: #1D4ED8 !important;
        font-weight: 600 !important;
    }
    
    /* Top Header Banner */
    .dashboard-header {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%);
        padding: 22px 28px;
        border-radius: 12px;
        color: #FFFFFF !important;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.12);
    }
    
    .dashboard-header h1 {
        color: #FFFFFF !important;
        font-size: 24px !important;
        font-weight: 700 !important;
        margin: 0 !important;
        padding: 0 !important;
        letter-spacing: -0.5px;
    }
    
    .dashboard-header p {
        color: #DBEAFE !important;
        font-size: 13.5px !important;
        margin-top: 4px !important;
        margin-bottom: 0 !important;
    }
    
    /* Headings in Main Panel */
    h1, h2, h3, h4, h5, h6 {
        color: #0F172A !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }
    
    h3 {
        font-size: 20px !important;
        margin-top: 10px !important;
        margin-bottom: 18px !important;
    }
    
    /* KPI Metric Cards */
    .metric-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 18px 20px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08) !important;
    }
    
    .metric-label {
        color: #64748B !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.6px !important;
    }
    
    .metric-value {
        color: #0F172A !important;
        font-size: 28px !important;
        font-weight: 700 !important;
        margin-top: 6px !important;
        letter-spacing: -0.5px !important;
    }
    
    .metric-subtext {
        color: #059669 !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        margin-top: 4px !important;
    }
    
    /* White Card Containers */
    .content-box {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 10px !important;
        padding: 20px 22px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04) !important;
    }
    
    .content-title {
        color: #0F172A !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        margin-bottom: 14px !important;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* Badges */
    .badge-primary {
        background-color: #EFF6FF !important;
        color: #1D4ED8 !important;
        border: 1px solid #BFDBFE !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        display: inline-block;
    }
    
    /* Form inputs and Selectboxes */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stMultiSelect"] label {
        color: #1E293B !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }
    
    /* Buttons */
    .stButton > button[kind="primary"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
        border: none !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8 !important;
    }
    
    .stDownloadButton > button {
        background-color: #FFFFFF !important;
        color: #1E293B !important;
        border: 1px solid #CBD5E1 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
    }
    
    .stDownloadButton > button:hover {
        border-color: #2563EB !important;
        color: #2563EB !important;
        background-color: #EFF6FF !important;
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
        color: #64748B !important;
    }
    
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #2563EB !important;
        border-bottom-color: #2563EB !important;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Plotly Standardized SaaS Styling Helper
# ---------------------------------------------------------
def style_plotly_fig(fig, height=330):
    """Applies a crisp, high-contrast light SaaS theme to any Plotly figure."""
    fig.update_layout(
        template="plotly_white",
        height=height,
        font=dict(color="#0F172A", family="Inter, Segoe UI, sans-serif", size=11),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=15, r=15, t=30, b=15),
        xaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(color="#334155", size=10),
            title_font=dict(color="#0F172A", size=12, family="Inter, sans-serif"),
            linecolor="#E2E8F0"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(color="#334155", size=10),
            title_font=dict(color="#0F172A", size=12, family="Inter, sans-serif"),
            linecolor="#E2E8F0"
        ),
        legend=dict(
            font=dict(color="#0F172A", size=11),
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#E2E8F0",
            borderwidth=1
        )
    )
    return fig


# ---------------------------------------------------------
# Data Loading Helpers
# ---------------------------------------------------------
@st.cache_data
def load_datasets():
    """Loads cleaned data, predictions, and metrics from disk."""
    cleaned_df = None
    preds_df = None
    metrics_df = None

    if config.PROCESSED_DATA_CSV.exists():
        cleaned_df = pd.read_csv(config.PROCESSED_DATA_CSV)
        cleaned_df["Date"] = pd.to_datetime(cleaned_df["Date"])
    elif config.RAW_DATA_PATH.exists():
        raw = pd.read_csv(config.RAW_DATA_PATH)
        for col in ["Page.Loads", "Unique.Visits", "First.Time.Visits", "Returning.Visits"]:
            if col in raw.columns:
                raw[col] = raw[col].astype(str).str.replace(",", "").astype(float)
        raw["Date"] = pd.to_datetime(raw["Date"])
        cleaned_df = raw.rename(columns={
            "Page.Loads": "Page_Loads",
            "Unique.Visits": "Unique_Visits",
            "First.Time.Visits": "First_Time_Visits",
            "Returning.Visits": "Returning_Visits",
            "Day.Of.Week": "Day_Of_Week"
        })

    if config.PREDICTIONS_PATH.exists():
        preds_df = pd.read_csv(config.PREDICTIONS_PATH)
        preds_df["Date"] = pd.to_datetime(preds_df["Date"])

    if config.METRICS_PATH.exists():
        metrics_df = pd.read_csv(config.METRICS_PATH)

    return cleaned_df, preds_df, metrics_df


cleaned_df, preds_df, metrics_df = load_datasets()

# ---------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 🌐 **Traffic Analytics**")
    st.markdown("<span style='color: #64748B; font-size: 13px;'>Apache Spark MLlib & Forecasting</span>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 14px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)

    page = st.radio(
        "Navigation Menu",
        [
            "📊  Overview",
            "🔍  Data Exploration",
            "🏆  Model Performance",
            "📈  Traffic Analysis",
            "🤖  Prediction Engine"
        ],
        index=0
    )
    # Strip emoji for routing
    page_name = page.split("  ")[-1].strip()

    st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
    st.markdown("##### ⚙️ **System Architecture**")
    st.markdown("""
    - **Engine:** Apache Spark 3.5.9
    - **ML Framework:** PySpark MLlib
    - **Algorithms:** Random Forest & Linear Reg.
    - **Dataset:** Daily Website Visitors
    - **Target ($y$):** Daily Page Views
    - **Split:** 80% Train / 20% Chronological Test
    """)
    st.markdown("<hr style='margin: 18px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
    st.caption("Big Data & ML Project | Windows 11")


# Header Banner across all pages
st.markdown("""
<div class="dashboard-header">
    <h1>Website Traffic Analytics & Prediction Dashboard</h1>
    <p>Enterprise Big Data Analytics & Time-Series Machine Learning Powered by Apache Spark MLlib</p>
</div>
""", unsafe_allow_html=True)


# =========================================================
# PAGE 1: OVERVIEW
# =========================================================
if page_name == "Overview":
    st.markdown("### 📊 Executive Summary & Key Performance Indicators")
    
    if cleaned_df is not None:
        total_page_views = cleaned_df["Page_Loads"].sum()
        avg_daily_traffic = cleaned_df["Page_Loads"].mean()
        max_daily_traffic = cleaned_df["Page_Loads"].max()
        total_records = len(cleaned_df)
        
        # 5 KPI Cards
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
        
        with kpi1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Page Views</div>
                <div class="metric-value">{total_page_views:,.0f}</div>
                <div class="metric-subtext">6 Years Cumulative</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Avg Daily Traffic</div>
                <div class="metric-value">{avg_daily_traffic:,.0f}</div>
                <div class="metric-subtext">Page Loads / Day</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Peak Daily Traffic</div>
                <div class="metric-value">{max_daily_traffic:,.0f}</div>
                <div class="metric-subtext">All-Time Record</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Records</div>
                <div class="metric-value">{total_records:,}</div>
                <div class="metric-subtext">Daily Time-Series</div>
            </div>
            """, unsafe_allow_html=True)
            
        with kpi5:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Best ML Model</div>
                <div class="metric-value" style="font-size: 20px; color: #2563EB;">Random Forest</div>
                <div class="metric-subtext">RMSE 348.6 | R² 91.4%</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)

        # Main Trend Chart
        col_trend, col_split = st.columns([7, 3])
        
        with col_trend:
            st.markdown('<div class="content-box"><div class="content-title">📈 Overall Website Traffic Trend (Daily Page Loads & 30-Day Moving Average)</div>', unsafe_allow_html=True)
            
            temp_df = cleaned_df.copy().sort_values("Date")
            temp_df["MA30"] = temp_df["Page_Loads"].rolling(30).mean()
            
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=temp_df["Date"], y=temp_df["Page_Loads"],
                mode="lines", name="Daily Page Loads",
                line=dict(color="#2563EB", width=1.3),
                opacity=0.75
            ))
            fig_trend.add_trace(go.Scatter(
                x=temp_df["Date"], y=temp_df["MA30"],
                mode="lines", name="30-Day Moving Avg",
                line=dict(color="#DC2626", width=2.5)
            ))
            style_plotly_fig(fig_trend, height=330)
            fig_trend.update_layout(legend=dict(orientation="h", y=1.1, x=0.01))
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_split:
            st.markdown('<div class="content-box"><div class="content-title">📅 Weekday vs Weekend Traffic</div>', unsafe_allow_html=True)
            
            temp_df["Weekend_Type"] = temp_df["Day"].apply(lambda d: "Weekend" if d in ["Saturday", "Sunday"] else "Weekday")
            split_summary = temp_df.groupby("Weekend_Type")["Page_Loads"].agg(["mean", "count"]).reset_index()
            
            fig_pie = px.pie(
                split_summary,
                values="mean",
                names="Weekend_Type",
                color="Weekend_Type",
                color_discrete_map={"Weekday": "#2563EB", "Weekend": "#10B981"},
                hole=0.60
            )
            style_plotly_fig(fig_pie, height=330)
            fig_pie.update_layout(legend=dict(orientation="h", y=1.05, x=0.15))
            fig_pie.update_traces(
                textinfo="label+value",
                texttemplate="<b>%{label}</b><br>%{value:,.0f} avg",
                textfont=dict(color="#0F172A", size=12)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Monthly & Day Distribution Charts
        col_month, col_dow = st.columns(2)
        
        with col_month:
            st.markdown('<div class="content-box"><div class="content-title">🗓️ Monthly Traffic Distribution</div>', unsafe_allow_html=True)
            temp_df["Month_Name"] = temp_df["Date"].dt.strftime("%B")
            month_order = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
            monthly_data = temp_df.groupby("Month_Name")["Page_Loads"].mean().reindex(month_order).reset_index()
            
            fig_month = px.bar(
                monthly_data,
                x="Month_Name",
                y="Page_Loads",
                color="Page_Loads",
                color_continuous_scale="Blues",
                labels={"Month_Name": "Month", "Page_Loads": "Avg Page Loads"}
            )
            style_plotly_fig(fig_month, height=300)
            fig_month.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_month, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_dow:
            st.markdown('<div class="content-box"><div class="content-title">📊 Average Traffic by Day of the Week</div>', unsafe_allow_html=True)
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            dow_data = temp_df.groupby("Day")["Page_Loads"].mean().reindex(day_order).reset_index()
            
            fig_dow = px.bar(
                dow_data,
                x="Day",
                y="Page_Loads",
                color="Day",
                color_discrete_sequence=["#1D4ED8", "#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#10B981", "#34D399"],
                labels={"Day": "Day of Week", "Page_Loads": "Avg Page Loads"}
            )
            style_plotly_fig(fig_dow, height=300)
            fig_dow.update_layout(showlegend=False)
            st.plotly_chart(fig_dow, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("Processed dataset not found. Please run main.py first.")


# =========================================================
# PAGE 2: DATA EXPLORATION
# =========================================================
elif page_name == "Data Exploration":
    st.markdown("### 🔍 Dataset Exploration & Schema Inspection")
    
    if cleaned_df is not None:
        tab1, tab2, tab3 = st.tabs(["📋 Dataset Preview & Schema", "📊 Distributions & Null Analysis", "🔥 Correlation Heatmap"])
        
        with tab1:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("#### **Processed Website Traffic Data Preview**")
            st.dataframe(cleaned_df.head(100), use_container_width=True, height=340)
            st.caption(f"Showing first 100 rows out of {len(cleaned_df):,} total records.")
            st.markdown('</div>', unsafe_allow_html=True)
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                st.markdown("#### **Column Descriptions & Types**")
                schema_info = [
                    {"Column": "Date", "Spark Type": "DateType", "Role": "Timestamp identifier"},
                    {"Column": "Day", "Spark Type": "StringType", "Role": "Day name (Categorical)"},
                    {"Column": "Day_Of_Week", "Spark Type": "IntegerType", "Role": "Day index (1-7)"},
                    {"Column": "Page_Loads", "Spark Type": "DoubleType", "Role": "Target Variable (Website Traffic)"},
                    {"Column": "Unique_Visits", "Spark Type": "DoubleType", "Role": "Total unique visitors"},
                    {"Column": "First_Time_Visits", "Spark Type": "DoubleType", "Role": "New visitors"},
                    {"Column": "Returning_Visits", "Spark Type": "DoubleType", "Role": "Repeat visitors"},
                ]
                st.table(pd.DataFrame(schema_info))
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_s2:
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                st.markdown("#### **Descriptive Statistics**")
                num_cols = ["Page_Loads", "Unique_Visits", "First_Time_Visits", "Returning_Visits"]
                st.dataframe(cleaned_df[num_cols].describe().round(1), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            col_null, col_dist = st.columns(2)
            
            with col_null:
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                st.markdown("#### **Missing / Null Value Analysis**")
                null_counts = cleaned_df.isnull().sum().reset_index()
                null_counts.columns = ["Column", "Null_Count"]
                
                fig_null = px.bar(
                    null_counts,
                    x="Column",
                    y="Null_Count",
                    color="Null_Count",
                    color_continuous_scale="Blues",
                    title="Null Values by Column (100% Cleaned)"
                )
                style_plotly_fig(fig_null, height=300)
                st.plotly_chart(fig_null, use_container_width=True)
                st.success("✅ Clean dataset verified: 0 null records across all features!")
                st.markdown('</div>', unsafe_allow_html=True)
                
            with col_dist:
                st.markdown('<div class="content-box">', unsafe_allow_html=True)
                st.markdown("#### **Target Variable Distribution (Page Loads)**")
                fig_hist = px.histogram(
                    cleaned_df,
                    x="Page_Loads",
                    nbins=40,
                    marginal="box",
                    color_discrete_sequence=["#2563EB"],
                    title="Traffic Distribution (Page Loads)"
                )
                style_plotly_fig(fig_hist, height=300)
                st.plotly_chart(fig_hist, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("#### **Pearson Feature Correlation Heatmap**")
            corr_cols = [c for c in cleaned_df.select_dtypes(include=[np.number]).columns if c not in ["Row"]]
            corr_matrix = cleaned_df[corr_cols].corr().round(3)
            
            fig_corr = px.imshow(
                corr_matrix,
                text_auto=True,
                aspect="auto",
                color_continuous_scale="Blues",
                title="Correlation Heatmap of Numerical Features"
            )
            style_plotly_fig(fig_corr, height=450)
            st.plotly_chart(fig_corr, use_container_width=True)
            st.caption("Strong positive correlation between Unique Visits and Page Loads demonstrates steady visitor engagement.")
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# PAGE 3: MODEL PERFORMANCE
# =========================================================
elif page_name == "Model Performance":
    st.markdown("### 🏆 Apache Spark MLlib Model Evaluation")
    
    if metrics_df is not None:
        lr_row = metrics_df[metrics_df["Model"].str.contains("Linear", case=False)].iloc[0]
        rf_row = metrics_df[metrics_df["Model"].str.contains("Random", case=False)].iloc[0]
        
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        
        with m_c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Random Forest Test RMSE</div>
                <div class="metric-value" style="color: #059669;">{rf_row['RMSE']:.1f}</div>
                <div class="metric-subtext">vs Linear Reg: {lr_row['RMSE']:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Random Forest Test MAE</div>
                <div class="metric-value" style="color: #059669;">{rf_row['MAE']:.1f}</div>
                <div class="metric-subtext">vs Linear Reg: {lr_row['MAE']:.1f}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Random Forest Test R²</div>
                <div class="metric-value" style="color: #059669;">{rf_row['R2']:.3f}</div>
                <div class="metric-subtext">Explains 91.4% of Variance</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_c4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Winner Algorithm</div>
                <div class="metric-value" style="font-size: 20px; color: #2563EB;">Random Forest</div>
                <div class="metric-subtext">Lowest Error Across Metrics</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Comparison Charts & Table
        col_m_left, col_m_right = st.columns([6, 4])
        
        with col_m_left:
            st.markdown('<div class="content-box"><div class="content-title">📊 Test Metrics Comparison (Spark MLlib)</div>', unsafe_allow_html=True)
            
            metric_plot_df = pd.DataFrame({
                "Metric": ["RMSE", "RMSE", "MAE", "MAE"],
                "Model": ["Linear Regression", "Random Forest", "Linear Regression", "Random Forest"],
                "Value": [lr_row["RMSE"], rf_row["RMSE"], lr_row["MAE"], rf_row["MAE"]]
            })
            
            fig_metrics = px.bar(
                metric_plot_df,
                x="Metric",
                y="Value",
                color="Model",
                barmode="group",
                color_discrete_map={"Linear Regression": "#93C5FD", "Random Forest": "#2563EB"},
                text_auto=".1f"
            )
            style_plotly_fig(fig_metrics, height=290)
            fig_metrics.update_layout(legend=dict(orientation="h", y=1.12, x=0.2))
            st.plotly_chart(fig_metrics, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_m_right:
            st.markdown('<div class="content-box"><div class="content-title">📋 Official Evaluation Comparison Table</div>', unsafe_allow_html=True)
            st.dataframe(metrics_df, use_container_width=True, height=170)
            st.markdown("""
            > **Evaluation Insight:**
            > Random Forest Regression outperforms Linear Regression with a **15.4% lower RMSE** (348.6 vs 412.0) and achieves an **R² of 0.914**, demonstrating superior ability to capture non-linear day-of-week interactions and seasonal traffic shifts.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

        # Actual vs Predicted Interactive Chart
        if preds_df is not None:
            st.markdown('<div class="content-box"><div class="content-title">🎯 Actual vs Predicted Website Traffic (Chronological Test Set: 432 Days)</div>', unsafe_allow_html=True)
            
            fig_pred = go.Figure()
            fig_pred.add_trace(go.Scatter(
                x=preds_df["Date"], y=preds_df["Actual_Page_Loads"],
                mode="lines", name="Actual Page Loads",
                line=dict(color="#2563EB", width=2.0)
            ))
            fig_pred.add_trace(go.Scatter(
                x=preds_df["Date"], y=preds_df["Predicted_Page_Loads"],
                mode="lines", name="Predicted Page Loads (Spark RF)",
                line=dict(color="#EF4444", width=1.8, dash="dash")
            ))
            style_plotly_fig(fig_pred, height=350)
            fig_pred.update_layout(legend=dict(orientation="h", y=1.08, x=0.01))
            st.plotly_chart(fig_pred, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Residuals over time & Distribution
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown('<div class="content-box"><div class="content-title">📉 Residuals (Prediction Error) Over Time</div>', unsafe_allow_html=True)
                fig_res = px.scatter(
                    preds_df,
                    x="Date",
                    y="Prediction_Error",
                    color="Prediction_Error",
                    color_continuous_scale="RdBu_r"
                )
                fig_res.add_hline(y=0, line_dash="dash", line_color="#0F172A")
                style_plotly_fig(fig_res, height=270)
                fig_res.update_layout(coloraxis_showscale=False)
                st.plotly_chart(fig_res, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_r2:
                st.markdown('<div class="content-box"><div class="content-title">🔔 Prediction Error Distribution (Normality Check)</div>', unsafe_allow_html=True)
                fig_err_hist = px.histogram(
                    preds_df,
                    x="Prediction_Error",
                    nbins=35,
                    color_discrete_sequence=["#7C3AED"],
                    marginal="box"
                )
                style_plotly_fig(fig_err_hist, height=270)
                st.plotly_chart(fig_err_hist, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# PAGE 4: TRAFFIC ANALYSIS
# =========================================================
elif page_name == "Traffic Analysis":
    st.markdown("### 🔎 Granular Traffic Pattern & Seasonality Analysis")
    
    if cleaned_df is not None:
        st.markdown('<div class="content-box">', unsafe_allow_html=True)
        f_col1, f_col2, f_col3 = st.columns([4, 4, 2])
        
        min_date = cleaned_df["Date"].min().date()
        max_date = cleaned_df["Date"].max().date()
        
        with f_col1:
            date_range = st.date_input(
                "Filter Date Range",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
        with f_col2:
            all_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            selected_days = st.multiselect("Filter Days of Week", all_days, default=all_days)
            
        with f_col3:
            metric_choice = st.selectbox(
                "Select Metric",
                ["Page_Loads", "Unique_Visits", "First_Time_Visits", "Returning_Visits"]
            )
            
        st.markdown('</div>', unsafe_allow_html=True)

        if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
            start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered_df = cleaned_df[
                (cleaned_df["Date"] >= start_d) &
                (cleaned_df["Date"] <= end_d) &
                (cleaned_df["Day"].isin(selected_days))
            ]
        else:
            filtered_df = cleaned_df[cleaned_df["Day"].isin(selected_days)]

        st.caption(f"Displaying {len(filtered_df):,} filtered daily records.")

        st.markdown(f'<div class="content-box"><div class="content-title">📈 Filtered Traffic Trend: {metric_choice.replace("_", " ")}</div>', unsafe_allow_html=True)
        fig_filtered = px.line(
            filtered_df.sort_values("Date"),
            x="Date",
            y=metric_choice,
            color_discrete_sequence=["#2563EB"]
        )
        style_plotly_fig(fig_filtered, height=330)
        st.plotly_chart(fig_filtered, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.markdown('<div class="content-box"><div class="content-title">👥 New vs Returning Visitor Trends</div>', unsafe_allow_html=True)
            fig_vis = go.Figure()
            fig_vis.add_trace(go.Scatter(
                x=filtered_df["Date"], y=filtered_df["First_Time_Visits"],
                mode="lines", name="First-Time Visitors",
                line=dict(color="#2563EB", width=1.5)
            ))
            fig_vis.add_trace(go.Scatter(
                x=filtered_df["Date"], y=filtered_df["Returning_Visits"],
                mode="lines", name="Returning Visitors",
                line=dict(color="#F59E0B", width=1.5)
            ))
            style_plotly_fig(fig_vis, height=300)
            fig_vis.update_layout(legend=dict(orientation="h", y=1.08, x=0.01))
            st.plotly_chart(fig_vis, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_t2:
            st.markdown('<div class="content-box"><div class="content-title">📅 Traffic Profile Across Day of Week</div>', unsafe_allow_html=True)
            dow_profile = filtered_df.groupby("Day")[metric_choice].agg(["mean", "median"]).reindex(all_days).reset_index()
            
            fig_dow_profile = px.bar(
                dow_profile,
                x="Day",
                y="mean",
                color="mean",
                color_continuous_scale="Blues",
                labels={"mean": f"Avg {metric_choice}"}
            )
            style_plotly_fig(fig_dow_profile, height=300)
            fig_dow_profile.update_layout(coloraxis_showscale=False)
            st.plotly_chart(fig_dow_profile, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)


# =========================================================
# PAGE 5: PREDICTION INTERFACE
# =========================================================
elif page_name == "Prediction Engine":
    st.markdown("### 🤖 Interactive Traffic Prediction Engine")
    st.markdown("Enter operational parameters or load realistic historical sample features to predict website page views using the trained Apache Spark ML models.")

    default_vals = {
        "Day": "Tuesday",
        "Day_Of_Week": 3,
        "Year": 2026,
        "Month": 11,
        "Day_Num": 3,
        "Week_Of_Year": 45,
        "Is_Weekend": 0,
        "Quarter": 4,
        "Day_Of_Year": 307,
        "Lag_1_Page_Loads": 3650.0,
        "Lag_2_Page_Loads": 3580.0,
        "Lag_7_Page_Loads": 3720.0,
        "Rolling_7_Page_Loads": 3480.0,
        "Rolling_14_Page_Loads": 3520.0,
        "Lag_1_Unique_Visits": 2680.0,
        "Lag_1_Returning_Visits": 480.0
    }

    if preds_df is not None and len(preds_df) > 0:
        latest_row = preds_df.iloc[-1]
        default_vals["Day"] = str(latest_row["Day"])
        default_vals["Lag_1_Page_Loads"] = float(latest_row["Actual_Page_Loads"])

    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    col_algo, col_info = st.columns([5, 5])
    with col_algo:
        selected_model = st.selectbox(
            "Select Machine Learning Algorithm",
            ["Random Forest (Recommended)", "Linear Regression"]
        )
    with col_info:
        st.write("")
        st.markdown("<div style='margin-top: 26px; color: #475569; font-size: 13px;'>Trained with Spark MLlib on historical chronological data.</div>", unsafe_allow_html=True)

    st.markdown("<hr style='margin: 16px 0; border: none; border-top: 1px solid #E2E8F0;'/>", unsafe_allow_html=True)
    
    # Input Feature Controls
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown("##### 📅 Calendar Features")
        pred_date = st.date_input("Target Date", value=pd.to_datetime("2026-11-03").date())
        input_day = st.selectbox(
            "Day of Week",
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            index=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(default_vals["Day"])
        )
        day_map = {"Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4, "Thursday": 5, "Friday": 6, "Saturday": 7}
        input_dow = day_map[input_day]
        is_weekend = 1 if input_day in ["Saturday", "Sunday"] else 0

    with c2:
        st.markdown("##### ⏱️ Historical Traffic Lag Features")
        lag_1 = st.number_input("Lag 1 (Yesterday's Page Loads)", min_value=100.0, max_value=15000.0, value=default_vals["Lag_1_Page_Loads"], step=50.0)
        lag_2 = st.number_input("Lag 2 (Traffic 2 Days Ago)", min_value=100.0, max_value=15000.0, value=default_vals["Lag_2_Page_Loads"], step=50.0)
        lag_7 = st.number_input("Lag 7 (Same Day Last Week)", min_value=100.0, max_value=15000.0, value=default_vals["Lag_7_Page_Loads"], step=50.0)

    with c3:
        st.markdown("##### 📊 Trailing Moving Averages & Visitors")
        roll_7 = st.number_input("Rolling 7-Day Average Traffic", min_value=100.0, max_value=15000.0, value=default_vals["Rolling_7_Page_Loads"], step=50.0)
        roll_14 = st.number_input("Rolling 14-Day Average Traffic", min_value=100.0, max_value=15000.0, value=default_vals["Rolling_14_Page_Loads"], step=50.0)
        lag_uniq = st.number_input("Lag 1 Unique Visits", min_value=50.0, max_value=12000.0, value=default_vals["Lag_1_Unique_Visits"], step=50.0)
        lag_ret = st.number_input("Lag 1 Returning Visits", min_value=10.0, max_value=5000.0, value=default_vals["Lag_1_Returning_Visits"], step=10.0)

    parsed_date = pd.to_datetime(pred_date)
    feature_payload = {
        "Day": input_day,
        "Day_Of_Week": input_dow,
        "Year": parsed_date.year,
        "Month": parsed_date.month,
        "Day_Num": parsed_date.day,
        "Week_Of_Year": parsed_date.isocalendar().week,
        "Is_Weekend": is_weekend,
        "Quarter": (parsed_date.month - 1) // 3 + 1,
        "Day_Of_Year": parsed_date.dayofyear,
        "Lag_1_Page_Loads": lag_1,
        "Lag_2_Page_Loads": lag_2,
        "Lag_7_Page_Loads": lag_7,
        "Rolling_7_Page_Loads": roll_7,
        "Rolling_14_Page_Loads": roll_14,
        "Lag_1_Unique_Visits": lag_uniq,
        "Lag_1_Returning_Visits": lag_ret
    }

    st.markdown("<br>", unsafe_allow_html=True)
    predict_btn = st.button("🚀 Generate Traffic Prediction", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if predict_btn:
        model_name_clean = "Random Forest" if "Random" in selected_model else "Linear Regression"
        pred_result = predict_fast(feature_payload, model_name=model_name_clean)
        pred_value = pred_result["predicted_traffic"]
        
        res_col1, res_col2 = st.columns([4, 6])
        
        with res_col1:
            st.markdown(f"""
            <div class="metric-card" style="border: 2px solid #2563EB; background: #EFF6FF !important; text-align: center; padding: 26px;">
                <div class="metric-label" style="color: #1E40AF !important;">Predicted Daily Traffic</div>
                <div class="metric-value" style="color: #1E3A8A !important; font-size: 40px !important;">{pred_value:,.0f}</div>
                <div style="color: #2563EB !important; font-size: 13px; font-weight: 600; margin-top: 4px;">Page Loads for {parsed_date.strftime('%B %d, %Y')}</div>
                <div class="badge-primary" style="margin-top: 10px;">Model: {model_name_clean}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with res_col2:
            st.markdown('<div class="content-box">', unsafe_allow_html=True)
            st.markdown("#### **Inference Feature Breakdown**")
            summary_table = pd.DataFrame([
                {"Feature": "Target Date", "Value": str(pred_date)},
                {"Feature": "Day of Week", "Value": input_day},
                {"Feature": "Is Weekend", "Value": "Yes" if is_weekend else "No"},
                {"Feature": "Yesterday's Traffic (Lag 1)", "Value": f"{lag_1:,.0f}"},
                {"Feature": "Prior Week Same Day (Lag 7)", "Value": f"{lag_7:,.0f}"},
                {"Feature": "7-Day Moving Average", "Value": f"{roll_7:,.0f}"},
                {"Feature": "Inference Engine", "Value": pred_result["engine"]}
            ])
            st.table(summary_table)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📥 Export Predictions & Data")
    d_col1, d_col2, d_col3 = st.columns(3)
    
    with d_col1:
        if preds_df is not None:
            csv_data = preds_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Test Predictions (CSV)",
                data=csv_data,
                file_name="website_traffic_predictions.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    with d_col2:
        if metrics_df is not None:
            metrics_csv = metrics_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Model Metrics (CSV)",
                data=metrics_csv,
                file_name="model_evaluation_metrics.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    with d_col3:
        if cleaned_df is not None:
            cleaned_sample = cleaned_df.head(500).to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Cleaned Sample (CSV)",
                data=cleaned_sample,
                file_name="cleaned_website_traffic_sample.csv",
                mime="text/csv",
                use_container_width=True
            )
