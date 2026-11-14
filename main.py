"""
SALES DATA ANALYSIS & BUSINESS INTELLIGENCE PIPELINE
Master Orchestrator Script.

Executes the complete end-to-end analytical workflow:
1. Ingests raw Superstore sales dataset
2. Cleans, validates, and feature-engineers data
3. Exports processed dataset to CSV
4. Ingests processed data into SQLite database and executes 22 business SQL queries
5. Conducts Exploratory Data Analysis (EDA)
6. Generates 11 publication-grade static visualization charts (300 DPI)
7. Computes dynamic business insights & recommendations
8. Generates the executive Markdown Business Report
"""

import sys
import time
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import config
from src.data_cleaning import DataCleaner
from src.sql_analysis import SQLManager
from src.exploratory_analysis import ExploratoryAnalyzer
from src.visualizations import Visualizer
from src.insights import BusinessInsightsEngine

# Set up formatted console logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SalesPipeline")


def run_pipeline():
    start_time = time.time()
    print("\n" + "=" * 70)
    print("   SALES ANALYTICS & BUSINESS INTELLIGENCE - END-TO-END PIPELINE")
    print("=" * 70)

    # -------------------------------------------------------------
    # STEP 1 & 2: DATA LOADING & CLEANING
    # -------------------------------------------------------------
    logger.info(">>> STEP 1 & 2: Ingesting, Cleaning, and Feature Engineering...")
    cleaner = DataCleaner()
    df_clean = cleaner.run_pipeline()
    print(f"    ✔ Data cleaned: {len(df_clean):,} records, {len(df_clean.columns)} columns.")

    # -------------------------------------------------------------
    # STEP 3 & 4: SQL DATABASE CREATION & QUERY EXECUTION
    # -------------------------------------------------------------
    logger.info(">>> STEP 3 & 4: Ingesting into SQLite & Running 22 SQL Business Queries...")
    sql_mgr = SQLManager()
    sql_mgr.build_database(force_rebuild=True)
    sql_results = sql_mgr.execute_all_queries()
    print(f"    ✔ SQLite database created at: {config.DATABASE_FILE.name}")
    print(f"    ✔ Executed {len(sql_results)} production SQL business queries successfully.")

    # -------------------------------------------------------------
    # STEP 5: EXPLORATORY DATA ANALYSIS (EDA)
    # -------------------------------------------------------------
    logger.info(">>> STEP 5: Performing Exploratory Data Analysis...")
    analyzer = ExploratoryAnalyzer()
    eda_results = analyzer.run_full_eda()
    kpi = eda_results["kpis"]
    print(f"    ✔ Overall Revenue: ${kpi['total_sales']:,.2f}")
    print(f"    ✔ Net Profit:      ${kpi['total_profit']:,.2f} ({kpi['profit_margin']:.2f}% margin)")
    print(f"    ✔ Unique Orders:   {kpi['total_orders']:,} across {kpi['total_customers']:,} customers.")

    # -------------------------------------------------------------
    # STEP 6: VISUALIZATION GENERATION
    # -------------------------------------------------------------
    logger.info(">>> STEP 6: Generating Publication-Grade Visualizations...")
    vis = Visualizer()
    generated_charts = vis.generate_all_static_charts(df_clean)
    print(f"    ✔ Generated {len(generated_charts)} charts saved in: {config.CHARTS_DIR}")

    # -------------------------------------------------------------
    # STEP 7 & 8: BUSINESS INSIGHTS & EXECUTIVE REPORT
    # -------------------------------------------------------------
    logger.info(">>> STEP 7 & 8: Synthesizing Insights & Writing Business Report...")
    insights_engine = BusinessInsightsEngine()
    findings = insights_engine.generate_findings()
    report_path = insights_engine.build_markdown_report()
    print(f"    ✔ Business Report written to: {report_path.name}")
    print(f"    ✔ Profit leakage identified: {findings['category_insights']['loss_making_subcategories']}")

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 70)
    print(f"   PIPELINE EXECUTION COMPLETED SUCCESSFULLY IN {elapsed}s")
    print("=" * 70)
    print("\nNext steps to launch the interactive BI Dashboard:")
    print("   streamlit run dashboard/app.py\n")
    print("To run automated data validation tests:")
    print("   python -m unittest tests/test_data.py\n")


if __name__ == "__main__":
    run_pipeline()
