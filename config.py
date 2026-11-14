"""
Configuration file for the Sales Data Analysis and Business Intelligence Project.
Centralizes all file paths, database settings, visualization color palettes, and constants.
"""

from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = BASE_DIR / "database"
CHARTS_DIR = BASE_DIR / "charts"
SQL_DIR = BASE_DIR / "sql"
REPORTS_DIR = BASE_DIR / "reports"
DASHBOARD_DIR = BASE_DIR / "dashboard"
TESTS_DIR = BASE_DIR / "tests"

# File Paths
RAW_DATA_FILE = RAW_DATA_DIR / "Sample_Superstore.csv"
PROCESSED_DATA_FILE = PROCESSED_DATA_DIR / "cleaned_sales_data.csv"
DATABASE_FILE = DATABASE_DIR / "sales.db"
SQL_QUERIES_FILE = SQL_DIR / "SQL_queries.sql"
REPORT_FILE = REPORTS_DIR / "business_report.md"

# Database Configuration
DB_TABLE_NAME = "sales"

# UI & Color Theme Palette (Modern Business Intelligence styling)
PALETTE = {
    "primary": "#1E3A8A",      # Deep Navy
    "secondary": "#0284C7",    # Ocean Blue
    "accent": "#0D9488",       # Teal
    "success": "#10B981",      # Emerald Green
    "warning": "#F59E0B",      # Amber
    "danger": "#EF4444",       # Crimson Red
    "neutral_dark": "#1F2937", # Dark Slate
    "neutral_light": "#F8FAFC",# Off-white
    "card_bg": "#FFFFFF",      # Card Background
    "border": "#E2E8F0",       # Border Grey
}

# Categorical Color Map for Charts
CATEGORY_COLORS = {
    "Technology": "#0284C7",   # Blue
    "Office Supplies": "#0D9488", # Teal
    "Furniture": "#F59E0B",    # Amber
}

REGION_COLORS = {
    "West": "#3B82F6",
    "East": "#10B981",
    "Central": "#F59E0B",
    "South": "#EC4899",
}

# Column Definitions
RAW_COLUMNS = [
    "Row ID", "Order ID", "Order Date", "Ship Date", "Ship Mode",
    "Customer ID", "Customer Name", "Segment", "Country/Region",
    "City", "State", "Postal Code", "Region", "Product ID",
    "Category", "Sub-Category", "Product Name", "Sales",
    "Quantity", "Discount", "Profit"
]

NUMERICAL_COLUMNS = ["Sales", "Quantity", "Discount", "Profit"]
DATE_COLUMNS = ["Order Date", "Ship Date"]
