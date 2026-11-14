"""
SALES ANALYTICS & BUSINESS INTELLIGENCE DASHBOARD
Modern interactive enterprise BI dashboard built with Streamlit & Plotly.
Inspired by executive Power BI and Tableau architectures.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from src.data_cleaning import DataCleaner
from src.visualizations import Visualizer

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SALES ANALYTICS & BUSINESS INTELLIGENCE",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- MODERN ENTERPRISE BI CSS (Power BI / Tableau Inspired Theme) ---
st.markdown("""
<style>
    /* Global Page Styling */
    .stApp {
        background-color: #F8FAFC;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    }
    
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Force columns to stretch to equal height */
    div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        justify-content: stretch !important;
    }
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        height: 100% !important;
    }
    div[data-testid="column"] > div[data-testid="stVerticalBlock"] > div {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        height: 100% !important;
    }

    /* Executive Title Banner */
    .dashboard-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 55%, #0284C7 100%);
        padding: 16px 24px;
        border-radius: 10px;
        color: white;
        margin-bottom: 18px;
        box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.12), 0 2px 4px -1px rgba(15, 23, 42, 0.08);
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
    }
    .dashboard-header-text h1 {
        margin: 0;
        font-size: 22px;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #FFFFFF !important;
        line-height: 1.2;
    }
    .dashboard-header-text p {
        margin: 3px 0 0 0;
        font-size: 12.5px;
        color: #BAE6FD;
        font-weight: 400;
    }
    .header-badge {
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11.5px;
        font-weight: 600;
        color: #F8FAFC;
        white-space: nowrap;
    }

    /* KPI Metric Cards - Equal Height, Single Line Numbers */
    .kpi-container {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        background: #FFFFFF;
        border-radius: 8px;
        padding: 12px 14px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px 0 rgba(0, 0, 0, 0.04);
        border: 1px solid #E2E8F0;
        border-left: 4px solid #0284C7;
        box-sizing: border-box;
        height: 100%;
        min-height: 106px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .kpi-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.2;
    }
    .kpi-value {
        font-size: clamp(16px, 1.2vw, 21px);
        font-weight: 700;
        color: #0F172A;
        white-space: nowrap !important;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.25;
        margin: 4px 0 2px 0;
        letter-spacing: -0.01em;
    }
    .kpi-subtext {
        font-size: 10.5px;
        font-weight: 600;
        color: #10B981;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        line-height: 1.2;
        margin-top: auto;
    }

    /* KPI Accent Variations */
    .kpi-profit { border-left-color: #10B981; }
    .kpi-margin { border-left-color: #8B5CF6; }
    .kpi-orders { border-left-color: #3B82F6; }
    .kpi-customers { border-left-color: #F59E0B; }
    .kpi-aov { border-left-color: #0D9488; }

    /* Chart Containers */
    .chart-box {
        background: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        padding: 10px 14px 6px 14px;
        margin-bottom: 16px;
    }

    /* Section Subheaders */
    .section-title {
        font-size: 16px;
        font-weight: 700;
        color: #0F172A;
        margin-top: 14px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Sidebar Navigation Enhancement */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 4px;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] > label {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 6px;
        padding: 8px 12px;
        margin-bottom: 2px;
        transition: all 0.15s ease;
        cursor: pointer;
        font-size: 13px;
        font-weight: 500;
        color: #334155;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
        background-color: #F1F5F9;
        border-color: #CBD5E1;
        color: #0284C7;
    }

    /* Recommendation & Finding Cards */
    .rec-card {
        background: #FFFFFF;
        border-radius: 8px;
        padding: 14px 18px;
        border-left: 4px solid #0284C7;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        border-top: 1px solid #E2E8F0;
        border-right: 1px solid #E2E8F0;
        border-bottom: 1px solid #E2E8F0;
        margin-bottom: 12px;
    }
    .rec-title {
        font-size: 14px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .rec-body {
        font-size: 12.5px;
        color: #334155;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


# --- DATA CACHING & INGESTION ---
@st.cache_data(show_spinner=False)
def load_and_prepare_data() -> pd.DataFrame:
    """Loads cleaned data or triggers pipeline if missing."""
    if not config.PROCESSED_DATA_FILE.exists():
        cleaner = DataCleaner()
        df = cleaner.run_pipeline()
    else:
        df = pd.read_csv(config.PROCESSED_DATA_FILE)

    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Ship Date"] = pd.to_datetime(df["Ship Date"])
    return df


df_raw = load_and_prepare_data()

# --- SIDEBAR: NAVIGATION & FILTERS ---
st.sidebar.markdown("""
<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
    <span style="font-size: 28px;">📊</span>
    <div>
        <div style="font-size: 16px; font-weight: 700; color: #0F172A; line-height: 1.1;">BI Analytics</div>
        <div style="font-size: 11px; color: #64748B;">Superstore Intelligence</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("**Select View:**")
pages = [
    "1. Executive Overview",
    "2. Sales Analysis",
    "3. Product Analysis",
    "4. Customer Analysis",
    "5. Profitability Analysis",
    "6. Business Insights"
]
selected_page = st.sidebar.radio("Navigate Views:", pages, label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='font-size: 13px; font-weight: 700; color: #0F172A; margin-bottom: 6px;'>🎯 Interactive Filters</div>", unsafe_allow_html=True)

# Reset Filters Button
if st.sidebar.button("🔄 Reset All Filters", use_container_width=True):
    for key in list(st.session_state.keys()):
        if key.startswith("filter_"):
            del st.session_state[key]
    st.rerun()

# 1. Date Range Filter
min_date = df_raw["Order Date"].min().date()
max_date = df_raw["Order Date"].max().date()
date_range = st.sidebar.date_input(
    "Order Date Range:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    key="filter_date"
)

# 2. Region Filter
all_regions = sorted(df_raw["Region"].unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Region(s):",
    options=all_regions,
    default=all_regions,
    key="filter_region"
)

# Dynamic state cascade
if selected_regions:
    available_states = sorted(df_raw[df_raw["Region"].isin(selected_regions)]["State"].unique().tolist())
else:
    available_states = sorted(df_raw["State"].unique().tolist())

# 3. State Filter
selected_states = st.sidebar.multiselect(
    "State(s):",
    options=available_states,
    default=[],
    help="Leave blank to include all states in selected regions",
    key="filter_state"
)

# 4. Category Filter
all_categories = sorted(df_raw["Category"].unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Category:",
    options=all_categories,
    default=all_categories,
    key="filter_category"
)

# Dynamic sub-category cascade
if selected_categories:
    available_subcats = sorted(df_raw[df_raw["Category"].isin(selected_categories)]["Sub-Category"].unique().tolist())
else:
    available_subcats = sorted(df_raw["Sub-Category"].unique().tolist())

# 5. Sub-Category Filter
selected_subcats = st.sidebar.multiselect(
    "Sub-Category:",
    options=available_subcats,
    default=[],
    help="Leave blank to include all sub-categories",
    key="filter_subcat"
)

# 6. Customer Segment Filter
all_segments = sorted(df_raw["Segment"].unique().tolist())
selected_segments = st.sidebar.multiselect(
    "Customer Segment:",
    options=all_segments,
    default=all_segments,
    key="filter_segment"
)

# --- APPLY FILTERING LOGIC ---
df_filtered = df_raw.copy()

# Filter by Date (handles both 2-element tuple and temporary 1-element tuple)
if isinstance(date_range, (tuple, list)):
    if len(date_range) == 2:
        start_d, end_d = date_range
        df_filtered = df_filtered[
            (df_filtered["Order Date"].dt.date >= start_d) &
            (df_filtered["Order Date"].dt.date <= end_d)
        ]
    elif len(date_range) == 1:
        start_d = date_range[0]
        df_filtered = df_filtered[df_filtered["Order Date"].dt.date >= start_d]

if selected_regions:
    df_filtered = df_filtered[df_filtered["Region"].isin(selected_regions)]

if selected_states:
    df_filtered = df_filtered[df_filtered["State"].isin(selected_states)]

if selected_categories:
    df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]

if selected_subcats:
    df_filtered = df_filtered[df_filtered["Sub-Category"].isin(selected_subcats)]

if selected_segments:
    df_filtered = df_filtered[df_filtered["Segment"].isin(selected_segments)]

# Handle Empty Filter
if df_filtered.empty:
    st.warning("⚠️ No records match the active filter criteria. Please adjust or reset filters.")
    if st.button("Reset Filters Now"):
        for key in list(st.session_state.keys()):
            if key.startswith("filter_"):
                del st.session_state[key]
        st.rerun()
    st.stop()

# Export Filtered Data
st.sidebar.markdown("---")
csv_data = df_filtered.to_csv(index=False).encode("utf-8")
st.sidebar.download_button(
    label="📥 Export Filtered CSV",
    data=csv_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
    use_container_width=True
)

# --- HEADER TITLE BANNER ---
st.markdown(f"""
<div class="dashboard-header">
    <div class="dashboard-header-text">
        <h1>SALES ANALYTICS & BUSINESS INTELLIGENCE</h1>
        <p>Enterprise Retail Performance Monitor • Retail Operations Dashboard</p>
    </div>
    <div class="header-badge">
        📋 {len(df_filtered):,} / {len(df_raw):,} Transactions Active
    </div>
</div>
""", unsafe_allow_html=True)


# --- DYNAMIC KPI CARDS FUNCTION (Single line, equal height, tooltip) ---
def render_kpi_cards(df: pd.DataFrame):
    """Renders 6 modern BI KPI cards across columns with guaranteed equal height and no line wrapping."""
    tot_sales = df["Sales"].sum()
    tot_profit = df["Profit"].sum()
    tot_orders = df["Order ID"].nunique()
    tot_cust = df["Customer ID"].nunique()
    aov = tot_sales / tot_orders if tot_orders > 0 else 0.0
    margin = (tot_profit / tot_sales) * 100 if tot_sales > 0 else 0.0

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f"""
        <div class="kpi-container" title="Gross Sales: ${tot_sales:,.2f}">
            <div class="kpi-label">Total Revenue</div>
            <div class="kpi-value">${tot_sales:,.0f}</div>
            <div class="kpi-subtext">Gross Sales Volume</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        profit_color = "#10B981" if tot_profit >= 0 else "#EF4444"
        profit_text = "Net Gain" if tot_profit >= 0 else "Net Loss"
        st.markdown(f"""
        <div class="kpi-container kpi-profit" title="Net Operating Profit: ${tot_profit:,.2f}">
            <div class="kpi-label">Total Profit</div>
            <div class="kpi-value" style="color: {profit_color};">${tot_profit:,.0f}</div>
            <div class="kpi-subtext" style="color: {profit_color};">{profit_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        margin_color = "#10B981" if margin >= 12 else "#F59E0B" if margin >= 0 else "#EF4444"
        st.markdown(f"""
        <div class="kpi-container kpi-margin" title="Profit Margin: {margin:.2f}%">
            <div class="kpi-label">Profit Margin</div>
            <div class="kpi-value" style="color: {margin_color};">{margin:.1f}%</div>
            <div class="kpi-subtext">Operating Return</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="kpi-container kpi-orders" title="Unique Invoices: {tot_orders:,}">
            <div class="kpi-label">Total Orders</div>
            <div class="kpi-value">{tot_orders:,}</div>
            <div class="kpi-subtext">Unique Invoices</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class="kpi-container kpi-customers" title="Unique Customers: {tot_cust:,}">
            <div class="kpi-label">Customers</div>
            <div class="kpi-value">{tot_cust:,}</div>
            <div class="kpi-subtext">Distinct Clients</div>
        </div>
        """, unsafe_allow_html=True)
    with c6:
        st.markdown(f"""
        <div class="kpi-container kpi-aov" title="Average Order Value: ${aov:,.2f}">
            <div class="kpi-label">Avg Order Value</div>
            <div class="kpi-value">${aov:,.0f}</div>
            <div class="kpi-subtext">Basket Size</div>
        </div>
        """, unsafe_allow_html=True)


# =====================================================================
# PAGE 1: EXECUTIVE OVERVIEW
# =====================================================================
if selected_page == "1. Executive Overview":
    st.markdown("<div class='section-title'>📌 Executive Summary & Operational Health</div>", unsafe_allow_html=True)
    render_kpi_cards(df_filtered)

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns([1.6, 1.0])

    with col_left:
        st.plotly_chart(Visualizer.plotly_revenue_profit_trend(df_filtered), use_container_width=True)

    with col_right:
        st.plotly_chart(Visualizer.plotly_sales_by_region(df_filtered), use_container_width=True)

    col_bot1, col_bot2 = st.columns([1.2, 1.0])
    with col_bot1:
        st.plotly_chart(Visualizer.plotly_category_profitability(df_filtered), use_container_width=True)
    with col_bot2:
        st.plotly_chart(Visualizer.plotly_customer_segments(df_filtered), use_container_width=True)


# =====================================================================
# PAGE 2: SALES ANALYSIS
# =====================================================================
elif selected_page == "2. Sales Analysis":
    st.markdown("<div class='section-title'>📈 Sales Dynamics & Multi-Dimensional Breakdown</div>", unsafe_allow_html=True)
    render_kpi_cards(df_filtered)

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Temporal Sales Trends", "Geographic & Category Drilldown"])

    with tab1:
        st.plotly_chart(Visualizer.plotly_revenue_profit_trend(df_filtered), use_container_width=True)

        yr = df_filtered.groupby("Order Year").agg(
            Revenue=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Units=("Quantity", "sum")
        ).reset_index()
        yr["Margin_%"] = ((yr["Profit"] / yr["Revenue"]) * 100).round(2)
        yr["YoY_Growth_%"] = (yr["Revenue"].pct_change() * 100).round(2).fillna(0.0)

        st.markdown("#### Annual Performance Comparison")
        st.dataframe(
            yr.style.format({
                "Revenue": "${:,.2f}",
                "Profit": "${:,.2f}",
                "Orders": "{:,}",
                "Units": "{:,}",
                "Margin_%": "{:.2f}%",
                "YoY_Growth_%": "{:+.2f}%"
            }),
            use_container_width=True
        )

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(Visualizer.plotly_subcategory_performance(df_filtered), use_container_width=True)
        with c2:
            st.plotly_chart(Visualizer.plotly_state_performance(df_filtered), use_container_width=True)


# =====================================================================
# PAGE 3: PRODUCT ANALYSIS
# =====================================================================
elif selected_page == "3. Product Analysis":
    st.markdown("<div class='section-title'>📦 Product Portfolio & Profitability Diagnostics</div>", unsafe_allow_html=True)
    render_kpi_cards(df_filtered)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(Visualizer.plotly_top_products(df_filtered, n=10), use_container_width=True)
    with col2:
        st.plotly_chart(Visualizer.plotly_bottom_products(df_filtered, n=10), use_container_width=True)

    st.markdown("#### Product Sub-Category Performance Matrix")
    subcat_matrix = df_filtered.groupby(["Category", "Sub-Category"]).agg(
        Revenue=("Sales", "sum"),
        Profit=("Profit", "sum"),
        Quantity=("Quantity", "sum"),
        Orders=("Order ID", "nunique"),
        Avg_Discount=("Discount", "mean")
    ).reset_index()
    subcat_matrix["Margin_%"] = ((subcat_matrix["Profit"] / subcat_matrix["Revenue"]) * 100).round(2)
    subcat_matrix["Avg_Discount_%"] = (subcat_matrix["Avg_Discount"] * 100).round(2)
    subcat_matrix = subcat_matrix.sort_values(by="Profit", ascending=False)

    st.dataframe(
        subcat_matrix.style.format({
            "Revenue": "${:,.2f}",
            "Profit": "${:,.2f}",
            "Quantity": "{:,}",
            "Orders": "{:,}",
            "Margin_%": "{:.2f}%",
            "Avg_Discount_%": "{:.1f}%"
        }),
        use_container_width=True
    )


# =====================================================================
# PAGE 4: CUSTOMER ANALYSIS
# =====================================================================
elif selected_page == "4. Customer Analysis":
    st.markdown("<div class='section-title'>👥 Customer Segmentation & Lifetime Spend</div>", unsafe_allow_html=True)
    render_kpi_cards(df_filtered)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1.0, 1.2])

    with col1:
        st.plotly_chart(Visualizer.plotly_customer_segments(df_filtered), use_container_width=True)

    with col2:
        seg_table = df_filtered.groupby("Segment").agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Customer_Count=("Customer ID", "nunique"),
            Order_Count=("Order ID", "nunique")
        ).reset_index()
        seg_table["Margin_%"] = ((seg_table["Total_Profit"] / seg_table["Total_Sales"]) * 100).round(2)
        seg_table["AOV"] = (seg_table["Total_Sales"] / seg_table["Order_Count"]).round(2)
        seg_table["Revenue_Share_%"] = ((seg_table["Total_Sales"] / seg_table["Total_Sales"].sum()) * 100).round(2)

        st.markdown("#### Segment Contribution Matrix")
        st.dataframe(
            seg_table.style.format({
                "Total_Sales": "${:,.2f}",
                "Total_Profit": "${:,.2f}",
                "Customer_Count": "{:,}",
                "Order_Count": "{:,}",
                "Margin_%": "{:.2f}%",
                "AOV": "${:,.2f}",
                "Revenue_Share_%": "{:.1f}%"
            }),
            use_container_width=True
        )

    st.markdown("#### Top 10 High-Value Enterprise Accounts")
    top_cust = df_filtered.groupby(["Customer ID", "Customer Name", "Segment"]).agg(
        Total_Spend=("Sales", "sum"),
        Total_Profit=("Profit", "sum"),
        Orders_Placed=("Order ID", "nunique"),
        Total_Items=("Quantity", "sum")
    ).reset_index()
    top_cust["Profit_Margin_%"] = ((top_cust["Total_Profit"] / top_cust["Total_Spend"]) * 100).round(2)
    top_cust = top_cust.sort_values(by="Total_Spend", ascending=False).head(10)

    st.dataframe(
        top_cust.style.format({
            "Total_Spend": "${:,.2f}",
            "Total_Profit": "${:,.2f}",
            "Orders_Placed": "{:,}",
            "Total_Items": "{:,}",
            "Profit_Margin_%": "{:.2f}%"
        }),
        use_container_width=True
    )


# =====================================================================
# PAGE 5: PROFITABILITY ANALYSIS
# =====================================================================
elif selected_page == "5. Profitability Analysis":
    st.markdown("<div class='section-title'>🎯 Profit Margins & Discount Sensitivity Audit</div>", unsafe_allow_html=True)
    render_kpi_cards(df_filtered)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        st.plotly_chart(Visualizer.plotly_discount_impact(df_filtered), use_container_width=True)

    with c2:
        st.plotly_chart(Visualizer.plotly_subcategory_performance(df_filtered), use_container_width=True)

    st.markdown("#### Realized Financials by Discount Tier")
    disc_summary = df_filtered.groupby("Discount Band").agg(
        Transactions=("Order ID", "count"),
        Gross_Sales=("Sales", "sum"),
        Net_Profit=("Profit", "sum"),
        Avg_Profit_Per_Order=("Profit", "mean")
    ).reset_index()
    disc_summary["Margin_%"] = ((disc_summary["Net_Profit"] / disc_summary["Gross_Sales"]) * 100).round(2)
    order_map = {"No Discount (0%)": 0, "Low (1-20%)": 1, "Moderate (21-40%)": 2, "High (>40%)": 3}
    disc_summary["rank"] = disc_summary["Discount Band"].map(order_map)
    disc_summary = disc_summary.sort_values(by="rank").drop(columns=["rank"])

    st.dataframe(
        disc_summary.style.format({
            "Transactions": "{:,}",
            "Gross_Sales": "${:,.2f}",
            "Net_Profit": "${:,.2f}",
            "Avg_Profit_Per_Order": "${:,.2f}",
            "Margin_%": "{:.2f}%"
        }),
        use_container_width=True
    )


# =====================================================================
# PAGE 6: BUSINESS INSIGHTS & STRATEGIC RECOMMENDATIONS
# =====================================================================
elif selected_page == "6. Business Insights":
    st.markdown("<div class='section-title'>💡 Automated Commercial Insights & Strategic Roadmap</div>", unsafe_allow_html=True)
    render_kpi_cards(df_filtered)

    st.markdown("<br>", unsafe_allow_html=True)

    # Calculate dynamic metrics for current selection
    tot_sales = df_filtered["Sales"].sum()
    tot_profit = df_filtered["Profit"].sum()
    sub_perf = df_filtered.groupby("Sub-Category")["Profit"].sum()
    loss_subs = sub_perf[sub_perf < 0]
    loss_subs_str = ", ".join([f"{k} (-${abs(v):,.0f})" for k, v in loss_subs.items()]) if not loss_subs.empty else "None"

    reg_perf = df_filtered.groupby("Region").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    reg_perf["Margin"] = (reg_perf["Profit"] / reg_perf["Sales"]) * 100
    top_reg = reg_perf.sort_values(by="Sales", ascending=False).index[0]
    worst_reg = reg_perf.sort_values(by="Margin").index[0]

    col_ins1, col_ins2 = st.columns(2)

    with col_ins1:
        st.markdown(f"""
        <div class="rec-card" style="border-left-color: #1E3A8A;">
            <div class="rec-title">📌 Key Commercial Findings</div>
            <div class="rec-body">
                • <b>Revenue Anchor:</b> <code>{top_reg}</code> is the largest regional market with ${reg_perf.loc[top_reg, 'Sales']:,.2f} in sales.<br>
                • <b>Margin Variance:</b> <code>{worst_reg}</code> exhibits the lowest profit margin ({reg_perf.loc[worst_reg, 'Margin']:.1f}%) due to steep promotional discounting.<br>
                • <b>Profit Leakage:</b> Unprofitable sub-categories in current selection: <b>{loss_subs_str}</b>.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="rec-card" style="border-left-color: #EF4444;">
            <div class="rec-title">⚠️ Weak-Performing Areas & Risks</div>
            <div class="rec-body">
                • <b>Deep Discount Trap:</b> Discounts over 20% reliably produce negative operating margins. Discounts >40% destroy capital (-83% margin).<br>
                • <b>Bulky Freight Subsidies:</b> Tables and Bookcases incur high shipping costs that are not recovered in product prices.<br>
                • <b>Regional Concentration:</b> Heavy loss concentration in Texas, Ohio, Pennsylvania, and Illinois.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_ins2:
        st.markdown("""
        <div class="rec-card" style="border-left-color: #10B981;">
            <div class="rec-title">💡 Revenue Growth Opportunities</div>
            <div class="rec-body">
                • <b>Technology Expansion:</b> Technology is the highest-margin category (17.4%). Expanding copier, phone, and computer accessories offers immediate top-line expansion.<br>
                • <b>Bundle Cross-Selling:</b> Bundle low-margin furniture items with high-margin office supplies or tech warranty services.<br>
                • <b>Corporate Account Growth:</b> Corporate segment accounts for 30%+ of volume with higher average order values.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="rec-card" style="border-left-color: #F59E0B;">
            <div class="rec-title">🎯 Profitability Recommendations</div>
            <div class="rec-body">
                • <b>Set 15% Discount Cap:</b> Require VP authorization for enterprise discounts above 20%.<br>
                • <b>Unbundle Shipping on Furniture:</b> Pass freight charges directly to customers on bulky SKUs.<br>
                • <b>Reallocate Regional Budgets:</b> Scale back promotional subsidies in Texas/Illinois and invest in California/New York.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### Interactive Profitability Simulator")
    st.info("Simulate the bottom-line financial impact of implementing a 20% discount cap across all transactions.")

    high_disc_rows = df_filtered[df_filtered["Discount"] > 0.20]
    high_disc_current_profit = high_disc_rows["Profit"].sum()
    estimated_recovered = abs(min(0.0, high_disc_current_profit)) * 0.75

    s1, s2, s3 = st.columns(3)
    s1.metric("Discounted Orders > 20%", f"{len(high_disc_rows):,}")
    s2.metric("Current Profit in Capped Tier", f"${high_disc_current_profit:,.2f}")
    s3.metric("Estimated Recovered Annual Profit", f"+${estimated_recovered:,.2f}", delta="Estimated Profit Gain")
