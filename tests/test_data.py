"""
Automated Test Suite for Sales Analytics & Business Intelligence System.
Validates data ingestion, cleaning rules, SQL database operations,
EDA mathematical consistency, and static chart generation.
"""

import sys
import unittest
import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config
from src.data_cleaning import DataCleaner
from src.sql_analysis import SQLManager
from src.exploratory_analysis import ExploratoryAnalyzer
from src.visualizations import Visualizer
from src.insights import BusinessInsightsEngine


class TestSalesDataPipeline(unittest.TestCase):
    """Unit and Integration Tests for the Sales Analytics System."""

    @classmethod
    def setUpClass(cls):
        """Prepare cleaned dataset and database once for tests."""
        cls.cleaner = DataCleaner()
        cls.df_clean = cls.cleaner.run_pipeline()
        cls.sql_mgr = SQLManager()
        cls.sql_mgr.build_database(force_rebuild=False)
        cls.analyzer = ExploratoryAnalyzer()
        cls.eda = cls.analyzer.run_full_eda()

    def test_01_raw_data_loaded(self):
        """Test that raw dataset exists and loads with positive row count."""
        self.assertTrue(config.RAW_DATA_FILE.exists(), "Raw dataset file must exist.")
        df_raw = self.cleaner.load_raw_data()
        self.assertGreater(len(df_raw), 0, "Raw dataset must not be empty.")

    def test_02_data_cleaning_no_null_postal_codes(self):
        """Test that missing postal codes were properly imputed."""
        self.assertEqual(
            self.df_clean["Postal Code"].isnull().sum(),
            0,
            "Postal Code column should contain zero null values post-cleaning."
        )

    def test_03_datetime_types_and_chronology(self):
        """Test that dates are parsed and Ship Date is always >= Order Date."""
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(self.df_clean["Order Date"]),
            "Order Date must be datetime type."
        )
        self.assertTrue(
            pd.api.types.is_datetime64_any_dtype(self.df_clean["Ship Date"]),
            "Ship Date must be datetime type."
        )
        invalid_dates = (self.df_clean["Ship Date"] < self.df_clean["Order Date"]).sum()
        self.assertEqual(invalid_dates, 0, "Ship Date should never precede Order Date.")

    def test_04_feature_engineering_columns_exist(self):
        """Test that engineered features are present in cleaned DataFrame."""
        expected_cols = [
            "Order Year", "Order Month", "Order Year Month", "Order Quarter",
            "Shipping Days", "Profit Margin", "Unit Price", "Discount Band",
            "Is Loss", "Is High Value"
        ]
        for col in expected_cols:
            self.assertIn(col, self.df_clean.columns, f"Engineered column '{col}' missing.")

    def test_05_numerical_integrity(self):
        """Test valid numerical domains (Sales > 0, Quantity > 0, Discount >= 0)."""
        self.assertTrue((self.df_clean["Sales"] > 0).all(), "All Sales values must be > 0.")
        self.assertTrue((self.df_clean["Quantity"] > 0).all(), "All Quantities must be > 0.")
        self.assertTrue((self.df_clean["Discount"] >= 0).all(), "Discounts must be >= 0.")
        self.assertTrue((self.df_clean["Discount"] <= 1.0).all(), "Discounts must be <= 1.0.")

    def test_06_sqlite_database_created(self):
        """Test SQLite database file exists and contains the sales table."""
        self.assertTrue(config.DATABASE_FILE.exists(), "SQLite database file must exist.")
        with sqlite3.connect(config.DATABASE_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM sales;")
            count = cursor.fetchone()[0]
            self.assertEqual(count, len(self.df_clean), "Row count in DB must match cleaned dataset.")

    def test_07_sql_kpi_query_execution(self):
        """Test Query 1 execution and match against Pandas calculations."""
        kpi_df = self.sql_mgr.run_query("""
            SELECT 
                ROUND(SUM(Sales), 2) AS Total_Sales,
                ROUND(SUM(Profit), 2) AS Total_Profit,
                COUNT(DISTINCT Order_ID) AS Total_Orders
            FROM sales;
        """)
        db_sales = float(kpi_df["Total_Sales"].iloc[0])
        db_profit = float(kpi_df["Total_Profit"].iloc[0])
        db_orders = int(kpi_df["Total_Orders"].iloc[0])

        pd_sales = round(float(self.df_clean["Sales"].sum()), 2)
        pd_profit = round(float(self.df_clean["Profit"].sum()), 2)
        pd_orders = int(self.df_clean["Order ID"].nunique())

        self.assertAlmostEqual(db_sales, pd_sales, places=1)
        self.assertAlmostEqual(db_profit, pd_profit, places=1)
        self.assertEqual(db_orders, pd_orders)

    def test_08_all_22_sql_queries_execute_without_error(self):
        """Test that every query in SQL_queries.sql parses and executes."""
        queries = self.sql_mgr.parse_sql_file()
        self.assertGreaterEqual(len(queries), 20, "Must have at least 20 queries.")
        for q in queries:
            df_result = self.sql_mgr.run_query(q["sql"])
            self.assertIsInstance(df_result, pd.DataFrame)

    def test_09_kpi_math_consistency(self):
        """Test that Profit Margin = (Profit / Sales) * 100."""
        kpi = self.eda["kpis"]
        expected_margin = round((kpi["total_profit"] / kpi["total_sales"]) * 100, 2)
        self.assertAlmostEqual(kpi["profit_margin"], expected_margin, places=2)

    def test_10_charts_generated_on_disk(self):
        """Test that required static charts were created on disk."""
        expected_files = [
            "sales_by_region.png",
            "monthly_sales_trend.png",
            "revenue_by_category.png",
            "top_10_products.png",
            "bottom_10_products.png",
            "customer_segment_analysis.png",
            "discount_vs_profit.png",
            "yearly_growth.png"
        ]
        for fname in expected_files:
            fpath = config.CHARTS_DIR / fname
            self.assertTrue(fpath.exists(), f"Chart file '{fname}' must exist in {config.CHARTS_DIR}")

    def test_11_business_report_generated(self):
        """Test that the executive Markdown report exists and has substantial content."""
        self.assertTrue(config.REPORT_FILE.exists(), "Report markdown file must exist.")
        content = config.REPORT_FILE.read_text(encoding="utf-8")
        self.assertIn("Executive Business Intelligence & Sales Performance Report", content)
        self.assertIn("Tables", content)


if __name__ == "__main__":
    unittest.main()
