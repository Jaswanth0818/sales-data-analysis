"""
Exploratory Data Analysis (EDA) Module.
Computes comprehensive retail metrics, business trends, segment distributions,
and profitability indicators from the cleaned sales dataset.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class ExploratoryAnalyzer:
    """Performs end-to-end exploratory data analysis on cleaned sales data."""

    def __init__(self, data_path: Path = config.PROCESSED_DATA_FILE):
        self.data_path = Path(data_path)
        self.df = None

    def load_data(self) -> pd.DataFrame:
        """Loads the cleaned dataset."""
        if not self.data_path.exists():
            from src.data_cleaning import DataCleaner
            logger.info("Processed data not found. Running data cleaning first...")
            cleaner = DataCleaner()
            self.df = cleaner.run_pipeline()
        else:
            self.df = pd.read_csv(self.data_path)
            self.df["Order Date"] = pd.to_datetime(self.df["Order Date"])
            self.df["Ship Date"] = pd.to_datetime(self.df["Ship Date"])
        return self.df

    def get_executive_kpis(self, df: pd.DataFrame = None) -> dict:
        """Calculates headline executive KPIs."""
        if df is None:
            df = self.df

        total_sales = float(df["Sales"].sum())
        total_profit = float(df["Profit"].sum())
        total_orders = int(df["Order ID"].nunique())
        total_customers = int(df["Customer ID"].nunique())
        total_items_sold = int(df["Quantity"].sum())
        aov = round(total_sales / total_orders, 2) if total_orders > 0 else 0.0
        profit_margin = round((total_profit / total_sales) * 100, 2) if total_sales > 0 else 0.0
        avg_discount = round(float(df["Discount"].mean()) * 100, 2)
        loss_transactions = int((df["Profit"] < 0).sum())
        loss_rate = round((loss_transactions / len(df)) * 100, 2) if len(df) > 0 else 0.0

        return {
            "total_sales": total_sales,
            "total_profit": total_profit,
            "total_orders": total_orders,
            "total_customers": total_customers,
            "total_items_sold": total_items_sold,
            "aov": aov,
            "profit_margin": profit_margin,
            "avg_discount": avg_discount,
            "loss_transactions": loss_transactions,
            "loss_rate": loss_rate,
        }

    def analyze_category_performance(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyzes sales, profit, margin, and order count by Category."""
        if df is None:
            df = self.df
        cat_df = df.groupby("Category").agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Quantity=("Quantity", "sum"),
            Order_Count=("Order ID", "nunique"),
            Avg_Discount=("Discount", "mean")
        ).reset_index()

        cat_df["Profit_Margin_%"] = ((cat_df["Total_Profit"] / cat_df["Total_Sales"]) * 100).round(2)
        cat_df["Sales_Share_%"] = ((cat_df["Total_Sales"] / cat_df["Total_Sales"].sum()) * 100).round(2)
        cat_df["Avg_Discount_%"] = (cat_df["Avg_Discount"] * 100).round(2)
        return cat_df.sort_values(by="Total_Sales", ascending=False)

    def analyze_subcategory_performance(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyzes performance by Sub-Category with profit margin ranking."""
        if df is None:
            df = self.df
        subcat_df = df.groupby(["Category", "Sub-Category"]).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Quantity=("Quantity", "sum"),
            Order_Count=("Order ID", "nunique"),
            Avg_Discount=("Discount", "mean")
        ).reset_index()

        subcat_df["Profit_Margin_%"] = ((subcat_df["Total_Profit"] / subcat_df["Total_Sales"]) * 100).round(2)
        subcat_df["Sales_Share_%"] = ((subcat_df["Total_Sales"] / subcat_df["Total_Sales"].sum()) * 100).round(2)
        subcat_df["Avg_Discount_%"] = (subcat_df["Avg_Discount"] * 100).round(2)
        return subcat_df.sort_values(by="Total_Profit", ascending=False)

    def analyze_regional_performance(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyzes sales, profit, and margins across geographic Regions."""
        if df is None:
            df = self.df
        reg_df = df.groupby("Region").agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Orders=("Order ID", "nunique"),
            Total_Customers=("Customer ID", "nunique"),
            Avg_Discount=("Discount", "mean")
        ).reset_index()

        reg_df["Profit_Margin_%"] = ((reg_df["Total_Profit"] / reg_df["Total_Sales"]) * 100).round(2)
        reg_df["Sales_Share_%"] = ((reg_df["Total_Sales"] / reg_df["Total_Sales"].sum()) * 100).round(2)
        reg_df["Avg_Discount_%"] = (reg_df["Avg_Discount"] * 100).round(2)
        return reg_df.sort_values(by="Total_Sales", ascending=False)

    def analyze_state_performance(self, df: pd.DataFrame = None, top_n: int = 10) -> tuple:
        """Identifies top-performing and lowest-performing states by net profit."""
        if df is None:
            df = self.df
        state_df = df.groupby(["State", "Region"]).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Orders=("Order ID", "nunique")
        ).reset_index()
        state_df["Profit_Margin_%"] = ((state_df["Total_Profit"] / state_df["Total_Sales"]) * 100).round(2)

        top_states = state_df.sort_values(by="Total_Profit", ascending=False).head(top_n)
        bottom_states = state_df.sort_values(by="Total_Profit", ascending=True).head(top_n)
        return top_states, bottom_states, state_df

    def analyze_monthly_trends(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Calculates monthly sales, profit, and Month-over-Month (MoM) growth."""
        if df is None:
            df = self.df
        trend_df = df.groupby("Order Year Month").agg(
            Monthly_Sales=("Sales", "sum"),
            Monthly_Profit=("Profit", "sum"),
            Order_Count=("Order ID", "nunique"),
            Quantity_Sold=("Quantity", "sum")
        ).reset_index()

        trend_df["Profit_Margin_%"] = ((trend_df["Monthly_Profit"] / trend_df["Monthly_Sales"]) * 100).round(2)
        trend_df["Sales_MoM_Growth_%"] = (trend_df["Monthly_Sales"].pct_change() * 100).round(2).fillna(0.0)
        trend_df["Profit_MoM_Growth_%"] = (trend_df["Monthly_Profit"].pct_change() * 100).round(2).fillna(0.0)
        return trend_df

    def analyze_yearly_trends(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Calculates yearly sales, profit, and Year-over-Year (YoY) growth."""
        if df is None:
            df = self.df
        year_df = df.groupby("Order Year").agg(
            Yearly_Sales=("Sales", "sum"),
            Yearly_Profit=("Profit", "sum"),
            Total_Orders=("Order ID", "nunique"),
            Total_Customers=("Customer ID", "nunique")
        ).reset_index()

        year_df["Profit_Margin_%"] = ((year_df["Yearly_Profit"] / year_df["Yearly_Sales"]) * 100).round(2)
        year_df["Sales_YoY_Growth_%"] = (year_df["Yearly_Sales"].pct_change() * 100).round(2).fillna(0.0)
        year_df["Profit_YoY_Growth_%"] = (year_df["Yearly_Profit"].pct_change() * 100).round(2).fillna(0.0)
        return year_df

    def analyze_discount_impact(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyzes how discounts erode profitability across discount bands."""
        if df is None:
            df = self.df
        disc_df = df.groupby("Discount Band").agg(
            Transaction_Count=("Order ID", "count"),
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Avg_Sales=("Sales", "mean"),
            Avg_Profit=("Profit", "mean")
        ).reset_index()

        disc_df["Profit_Margin_%"] = ((disc_df["Total_Profit"] / disc_df["Total_Sales"]) * 100).round(2)
        # Order by standard discount band order
        order_map = {"No Discount (0%)": 0, "Low (1-20%)": 1, "Moderate (21-40%)": 2, "High (>40%)": 3}
        disc_df["rank"] = disc_df["Discount Band"].map(order_map)
        disc_df = disc_df.sort_values(by="rank").drop(columns=["rank"])
        return disc_df

    def analyze_top_bottom_products(self, df: pd.DataFrame = None, n: int = 10) -> tuple:
        """Extracts top products by sales, top products by profit, and bottom loss-making products."""
        if df is None:
            df = self.df
        prod_df = df.groupby(["Product ID", "Product Name", "Category", "Sub-Category"]).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Quantity=("Quantity", "sum")
        ).reset_index()
        prod_df["Profit_Margin_%"] = ((prod_df["Total_Profit"] / prod_df["Total_Sales"]) * 100).round(2)

        top_by_sales = prod_df.sort_values(by="Total_Sales", ascending=False).head(n)
        top_by_profit = prod_df.sort_values(by="Total_Profit", ascending=False).head(n)
        bottom_by_profit = prod_df.sort_values(by="Total_Profit", ascending=True).head(n)
        return top_by_sales, top_by_profit, bottom_by_profit

    def analyze_customers(self, df: pd.DataFrame = None, top_n: int = 10) -> tuple:
        """Analyzes customer segments and top spending customers."""
        if df is None:
            df = self.df
        # Segment analysis
        segment_df = df.groupby("Segment").agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Orders=("Order ID", "nunique"),
            Total_Customers=("Customer ID", "nunique")
        ).reset_index()
        segment_df["Profit_Margin_%"] = ((segment_df["Total_Profit"] / segment_df["Total_Sales"]) * 100).round(2)
        segment_df["Sales_Share_%"] = ((segment_df["Total_Sales"] / segment_df["Total_Sales"].sum()) * 100).round(2)
        segment_df["AOV"] = (segment_df["Total_Sales"] / segment_df["Total_Orders"]).round(2)

        # Top customers
        cust_df = df.groupby(["Customer ID", "Customer Name", "Segment"]).agg(
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Total_Orders=("Order ID", "nunique"),
            Total_Items=("Quantity", "sum")
        ).reset_index()
        cust_df["Profit_Margin_%"] = ((cust_df["Total_Profit"] / cust_df["Total_Sales"]) * 100).round(2)
        top_customers = cust_df.sort_values(by="Total_Sales", ascending=False).head(top_n)

        return segment_df, top_customers

    def analyze_shipping(self, df: pd.DataFrame = None) -> pd.DataFrame:
        """Analyzes shipping duration and order volume across shipping modes."""
        if df is None:
            df = self.df
        ship_df = df.groupby("Ship Mode").agg(
            Order_Count=("Order ID", "nunique"),
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
            Avg_Shipping_Days=("Shipping Days", "mean"),
            Min_Shipping_Days=("Shipping Days", "min"),
            Max_Shipping_Days=("Shipping Days", "max")
        ).reset_index()
        ship_df["Avg_Shipping_Days"] = ship_df["Avg_Shipping_Days"].round(1)
        ship_df["Order_Share_%"] = ((ship_df["Order_Count"] / ship_df["Order_Count"].sum()) * 100).round(2)
        return ship_df.sort_values(by="Order_Count", ascending=False)

    def run_full_eda(self) -> dict:
        """Executes full EDA and returns a structured dictionary of results."""
        self.load_data()
        logger.info("Executing comprehensive Exploratory Data Analysis...")

        kpis = self.get_executive_kpis()
        cat_df = self.analyze_category_performance()
        subcat_df = self.analyze_subcategory_performance()
        reg_df = self.analyze_regional_performance()
        top_states, bottom_states, all_states = self.analyze_state_performance()
        monthly_df = self.analyze_monthly_trends()
        yearly_df = self.analyze_yearly_trends()
        disc_df = self.analyze_discount_impact()
        top_prod_sales, top_prod_profit, bottom_prod = self.analyze_top_bottom_products()
        seg_df, top_cust = self.analyze_customers()
        ship_df = self.analyze_shipping()

        results = {
            "kpis": kpis,
            "category": cat_df,
            "subcategory": subcat_df,
            "region": reg_df,
            "top_states": top_states,
            "bottom_states": bottom_states,
            "all_states": all_states,
            "monthly_trends": monthly_df,
            "yearly_trends": yearly_df,
            "discount_impact": disc_df,
            "top_products_sales": top_prod_sales,
            "top_products_profit": top_prod_profit,
            "bottom_products_profit": bottom_prod,
            "segments": seg_df,
            "top_customers": top_cust,
            "shipping": ship_df
        }

        logger.info("EDA completed successfully.")
        return results


if __name__ == "__main__":
    analyzer = ExploratoryAnalyzer()
    eda_results = analyzer.run_full_eda()
    kpi = eda_results["kpis"]
    print("\n" + "=" * 50)
    print("      EXECUTIVE EDA SUMMARY")
    print("=" * 50)
    print(f"Total Revenue:       ${kpi['total_sales']:,.2f}")
    print(f"Total Profit:        ${kpi['total_profit']:,.2f}")
    print(f"Profit Margin:       {kpi['profit_margin']:.2f}%")
    print(f"Total Orders:        {kpi['total_orders']:,}")
    print(f"Total Customers:     {kpi['total_customers']:,}")
    print(f"Average Order Value: ${kpi['aov']:.2f}")
    print(f"Loss Rate:           {kpi['loss_rate']:.2f}% ({kpi['loss_transactions']:,} transactions)")
    print("=" * 50)
    print("\nCategory Performance:\n", eda_results["category"].to_string(index=False))
    print("\nRegional Performance:\n", eda_results["region"].to_string(index=False))
