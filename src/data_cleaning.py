"""
Data Cleaning and Feature Engineering Module.
Performs thorough data validation, missing value imputation, type casting,
and business feature engineering on retail sales data.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure root directory is on sys.path for config import
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class DataCleaner:
    """Handles raw data ingestion, validation, cleaning, and feature engineering."""

    def __init__(self, raw_path: Path = config.RAW_DATA_FILE, processed_path: Path = config.PROCESSED_DATA_FILE):
        self.raw_path = Path(raw_path)
        self.processed_path = Path(processed_path)

    def load_raw_data(self) -> pd.DataFrame:
        """
        Loads the dataset with encoding fallback (utf-8, windows-1252, latin1).
        If the raw dataset is missing, downloads it or creates a realistic fallback.
        """
        if not self.raw_path.exists():
            logger.warning(f"Raw data file not found at {self.raw_path}. Attempting download...")
            self._download_or_create_fallback()

        encodings = ["utf-8", "windows-1252", "latin1"]
        for enc in encodings:
            try:
                df = pd.read_csv(self.raw_path, encoding=enc)
                logger.info(f"Successfully loaded raw data with {enc} encoding. Shape: {df.shape}")
                return df
            except Exception:
                continue

        raise ValueError(f"Unable to read {self.raw_path} with standard encodings.")

    def _download_or_create_fallback(self):
        """Downloads the authentic Superstore dataset from public source or creates fallback."""
        import urllib.request
        url = "https://raw.githubusercontent.com/bernardkilonzo-rigor/dataviz/refs/heads/main/data/Sample%20-%20Superstore.csv"
        try:
            self.raw_path.parent.mkdir(parents=True, exist_ok=True)
            logger.info(f"Downloading authentic Superstore dataset from {url}...")
            urllib.request.urlretrieve(url, self.raw_path)
            logger.info("Download completed successfully.")
        except Exception as e:
            logger.error(f"Download failed: {e}. Generating realistic sample dataset fallback...")
            self._generate_realistic_fallback()

    def _generate_realistic_fallback(self):
        """Generates a realistic fallback dataset if offline."""
        np.random.seed(42)
        n = 1000
        categories = {
            "Technology": ["Phones", "Accessories", "Copiers", "Machines"],
            "Furniture": ["Chairs", "Tables", "Bookcases", "Furnishings"],
            "Office Supplies": ["Storage", "Binders", "Paper", "Art", "Appliances"]
        }
        regions = {"West": ["California", "Washington"], "East": ["New York", "Pennsylvania"],
                   "Central": ["Texas", "Illinois"], "South": ["Florida", "North Carolina"]}
        segments = ["Consumer", "Corporate", "Home Office"]

        records = []
        start_date = pd.to_datetime("2017-01-01")
        for i in range(1, n + 1):
            cat = np.random.choice(list(categories.keys()))
            subcat = np.random.choice(categories[cat])
            reg = np.random.choice(list(regions.keys()))
            state = np.random.choice(regions[reg])
            order_date = start_date + pd.Timedelta(days=int(np.random.randint(0, 1400)))
            ship_date = order_date + pd.Timedelta(days=int(np.random.randint(1, 7)))
            qty = int(np.random.randint(1, 10))
            price = float(np.random.uniform(10, 500))
            discount = float(np.random.choice([0.0, 0.1, 0.2, 0.3, 0.5, 0.7]))
            sales = round(qty * price * (1 - discount), 2)
            margin_rate = float(np.random.uniform(-0.3, 0.4) if discount > 0.3 else np.random.uniform(0.05, 0.35))
            profit = round(sales * margin_rate, 2)

            records.append({
                "Row ID": i,
                "Order ID": f"CA-2020-{100000 + i}",
                "Order Date": order_date.strftime("%d/%m/%Y"),
                "Ship Date": ship_date.strftime("%d/%m/%Y"),
                "Ship Mode": np.random.choice(["Standard Class", "Second Class", "First Class", "Same Day"]),
                "Customer ID": f"CUST-{np.random.randint(100, 300)}",
                "Customer Name": f"Customer {np.random.randint(100, 300)}",
                "Segment": np.random.choice(segments),
                "Country/Region": "United States",
                "City": "Sample City",
                "State": state,
                "Postal Code": "90001",
                "Region": reg,
                "Product ID": f"PROD-{cat[:3].upper()}-{1000 + i}",
                "Category": cat,
                "Sub-Category": subcat,
                "Product Name": f"{subcat} Model {np.random.randint(1, 50)}",
                "Sales": sales,
                "Quantity": qty,
                "Discount": discount,
                "Profit": profit
            })
        df_fallback = pd.DataFrame(records)
        df_fallback.to_csv(self.raw_path, index=False)
        logger.info(f"Created realistic fallback dataset at {self.raw_path} with {n} rows.")

    def inspect_data(self, df: pd.DataFrame) -> dict:
        """Inspects data structure, counts nulls, duplicates, and checks types."""
        inspection = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "column_names": list(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "data_types": {col: str(dtype) for col, dtype in df.dtypes.items()}
        }
        logger.info(f"Data Inspection Summary: {inspection['total_rows']} rows, "
                    f"{inspection['total_columns']} cols, "
                    f"{inspection['duplicate_rows']} duplicates, "
                    f"Total nulls: {sum(inspection['missing_values'].values())}")
        return inspection

    def clean_and_engineer(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Performs data cleaning, validation, and feature engineering.
        """
        df_clean = df.copy()

        # 1. Normalize column names (strip whitespace)
        df_clean.columns = [c.strip() for c in df_clean.columns]

        # Standardize Country/Region to Country
        if "Country/Region" in df_clean.columns:
            df_clean = df_clean.rename(columns={"Country/Region": "Country"})
        elif "Country" not in df_clean.columns:
            df_clean["Country"] = "United States"

        # 2. Check and remove duplicate rows
        initial_count = len(df_clean)
        df_clean = df_clean.drop_duplicates()
        removed_dupes = initial_count - len(df_clean)
        if removed_dupes > 0:
            logger.info(f"Removed {removed_dupes} duplicate rows.")

        # 3. Handle Missing Values
        # Postal Code has 11 nulls for Burlington, Vermont in standard Superstore
        if "Postal Code" in df_clean.columns:
            # Impute known postal code for Burlington, VT: 05401
            df_clean["Postal Code"] = df_clean["Postal Code"].fillna(5401.0)
            # Format as clean 5-digit string (e.g., 05401, 90001)
            df_clean["Postal Code"] = df_clean["Postal Code"].apply(
                lambda x: f"{int(float(x)):05d}" if pd.notnull(x) else "00000"
            )

        # 4. Correct Data Types & Date Parsing
        # Order Date & Ship Date are formatted DD/MM/YYYY or MM/DD/YYYY
        df_clean["Order Date"] = pd.to_datetime(df_clean["Order Date"], dayfirst=True)
        df_clean["Ship Date"] = pd.to_datetime(df_clean["Ship Date"], dayfirst=True)

        # Ensure Ship Date >= Order Date
        invalid_dates = df_clean["Ship Date"] < df_clean["Order Date"]
        if invalid_dates.sum() > 0:
            logger.warning(f"Found {invalid_dates.sum()} rows where Ship Date < Order Date. Correcting...")
            df_clean.loc[invalid_dates, "Ship Date"] = df_clean.loc[invalid_dates, "Order Date"]

        # Ensure correct numeric types
        df_clean["Sales"] = pd.to_numeric(df_clean["Sales"], errors="coerce").fillna(0.0)
        df_clean["Quantity"] = pd.to_numeric(df_clean["Quantity"], errors="coerce").fillna(1).astype(int)
        df_clean["Discount"] = pd.to_numeric(df_clean["Discount"], errors="coerce").fillna(0.0)
        df_clean["Profit"] = pd.to_numeric(df_clean["Profit"], errors="coerce").fillna(0.0)

        # Clean string columns: strip trailing/leading spaces
        str_cols = ["Order ID", "Ship Mode", "Customer ID", "Customer Name",
                    "Segment", "Country", "City", "State", "Region",
                    "Product ID", "Category", "Sub-Category", "Product Name"]
        for col in str_cols:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()

        # 5. Business Feature Engineering
        # Date parts
        df_clean["Order Year"] = df_clean["Order Date"].dt.year
        df_clean["Order Month"] = df_clean["Order Date"].dt.month
        df_clean["Order Month Name"] = df_clean["Order Date"].dt.strftime("%b")
        df_clean["Order Year Month"] = df_clean["Order Date"].dt.strftime("%Y-%m")
        df_clean["Order Quarter"] = df_clean["Order Date"].dt.year.astype(str) + "-Q" + df_clean["Order Date"].dt.quarter.astype(str)
        df_clean["Order Day of Week"] = df_clean["Order Date"].dt.day_name()

        # Shipping metrics
        df_clean["Shipping Days"] = (df_clean["Ship Date"] - df_clean["Order Date"]).dt.days

        # Financial metrics
        # Profit Margin (%) = (Profit / Sales) * 100
        # If Sales == 0, Profit Margin is 0.0
        df_clean["Profit Margin"] = np.where(
            df_clean["Sales"] > 0,
            (df_clean["Profit"] / df_clean["Sales"]) * 100,
            0.0
        ).round(2)

        # Unit Price = Sales / Quantity (post-discount average revenue per unit)
        df_clean["Unit Price"] = np.where(
            df_clean["Quantity"] > 0,
            df_clean["Sales"] / df_clean["Quantity"],
            0.0
        ).round(2)

        # Discount Band categorization
        def categorize_discount(disc):
            if disc == 0.0:
                return "No Discount (0%)"
            elif disc <= 0.20:
                return "Low (1-20%)"
            elif disc <= 0.40:
                return "Moderate (21-40%)"
            else:
                return "High (>40%)"

        df_clean["Discount Band"] = df_clean["Discount"].apply(categorize_discount)

        # Flags for business segmentation
        df_clean["Is Loss"] = df_clean["Profit"] < 0
        df_clean["Is High Value"] = df_clean["Sales"] >= 1000.0

        logger.info(f"Feature engineering completed. Final shape: {df_clean.shape}")
        return df_clean

    def save_processed_data(self, df: pd.DataFrame) -> Path:
        """Saves the cleaned dataset to the processed folder as CSV."""
        self.processed_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(self.processed_path, index=False)
        logger.info(f"Cleaned dataset successfully saved to: {self.processed_path}")
        return self.processed_path

    def run_pipeline(self) -> pd.DataFrame:
        """Executes the full data loading, inspection, cleaning, and export process."""
        logger.info("--- Starting Data Cleaning & Feature Engineering Pipeline ---")
        df_raw = self.load_raw_data()
        self.inspect_data(df_raw)
        df_clean = self.clean_and_engineer(df_raw)
        self.save_processed_data(df_clean)
        logger.info("--- Data Cleaning Pipeline Finished Successfully ---")
        return df_clean


if __name__ == "__main__":
    cleaner = DataCleaner()
    df_cleaned = cleaner.run_pipeline()
    print("\nCleaned Dataset Head:")
    print(df_cleaned[["Order ID", "Order Date", "Category", "Sub-Category", "Sales", "Profit", "Profit Margin", "Discount Band"]].head(5))
