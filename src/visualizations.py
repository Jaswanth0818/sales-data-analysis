"""
Visualization Engine Module.
Generates publication-quality static charts (Matplotlib / Seaborn) saved to disk
and dynamic interactive Plotly charts for the Streamlit dashboard.
"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Apply modern theme defaults for Matplotlib
plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Segoe UI", "Arial"]
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8
plt.rcParams["grid.color"] = "#F1F5F9"
plt.rcParams["grid.linestyle"] = "--"
plt.rcParams["grid.alpha"] = 0.7

# Plotly global font and layout constants
PLOTLY_FONT = dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif", color="#0F172A")


class Visualizer:
    """Generates static figures (saved to charts/) and dynamic Plotly figures."""

    def __init__(self, charts_dir: Path = config.CHARTS_DIR):
        self.charts_dir = Path(charts_dir)
        self.charts_dir.mkdir(parents=True, exist_ok=True)

    # =====================================================================
    # SECTION 1: STATIC CHARTS (Matplotlib / Seaborn saved to disk)
    # =====================================================================

    def generate_all_static_charts(self, df: pd.DataFrame) -> dict:
        """Generates and saves all required static charts to the charts folder."""
        logger.info(f"Generating static charts in {self.charts_dir}...")
        saved_paths = {}

        saved_paths["sales_by_region"] = self.save_sales_by_region(df)
        saved_paths["monthly_sales_trend"] = self.save_monthly_sales_trend(df)
        saved_paths["category_performance"] = self.save_category_performance(df)
        saved_paths["top_10_products"] = self.save_top_10_products(df)
        saved_paths["bottom_10_products"] = self.save_bottom_10_products(df)
        saved_paths["customer_segments"] = self.save_customer_segments(df)
        saved_paths["discount_vs_profit"] = self.save_discount_vs_profit(df)
        saved_paths["sales_vs_profit"] = self.save_sales_vs_profit(df)
        saved_paths["regional_performance"] = self.save_regional_performance(df)
        saved_paths["yearly_growth"] = self.save_yearly_growth(df)
        saved_paths["shipping_performance"] = self.save_shipping_performance(df)

        logger.info(f"Successfully generated {len(saved_paths)} static charts.")
        return saved_paths

    def save_sales_by_region(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "sales_by_region.png"
        reg_df = df.groupby("Region")["Sales"].sum().sort_values(ascending=False).reset_index()

        fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
        colors = ["#1E3A8A", "#0284C7", "#0D9488", "#F59E0B"]
        bars = ax.bar(reg_df["Region"], reg_df["Sales"] / 1000, color=colors, width=0.55, edgecolor="none")

        ax.set_title("Total Revenue by Geographic Region ($K)", fontsize=14, fontweight="bold", pad=15, color="#0F172A")
        ax.set_ylabel("Revenue ($ Thousands)", fontsize=11, color="#334155")
        ax.set_xlabel("Region", fontsize=11, color="#334155")
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bar in bars:
            height = bar.get_height()
            ax.annotate(f"${height:,.1f}K",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1E293B")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_monthly_sales_trend(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "monthly_sales_trend.png"
        monthly = df.groupby("Order Year Month").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        monthly = monthly.sort_values(by="Order Year Month")

        fig, ax1 = plt.subplots(figsize=(14, 6), dpi=300)
        ax2 = ax1.twinx()

        line1 = ax1.plot(monthly["Order Year Month"], monthly["Sales"] / 1000, color="#0284C7", marker="o", linewidth=2.2, label="Revenue ($K)")
        line2 = ax2.plot(monthly["Order Year Month"], monthly["Profit"] / 1000, color="#10B981", marker="s", linewidth=2.0, linestyle="--", label="Profit ($K)")

        ax1.set_title("Monthly Revenue & Profit Progression", fontsize=15, fontweight="bold", pad=15, color="#0F172A")
        ax1.set_ylabel("Sales ($ Thousands)", fontsize=11, color="#0284C7")
        ax2.set_ylabel("Profit ($ Thousands)", fontsize=11, color="#10B981")
        ax1.tick_params(axis="x", rotation=60, labelsize=9)
        ax1.grid(True, linestyle="--", alpha=0.4)

        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax1.legend(lines, labels, loc="upper left", frameon=True)

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_category_performance(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "revenue_by_category.png"
        cat_df = df.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()

        x = np.arange(len(cat_df["Category"]))
        width = 0.35

        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        rects1 = ax.bar(x - width/2, cat_df["Sales"] / 1000, width, label="Sales ($K)", color="#1E3A8A")
        rects2 = ax.bar(x + width/2, cat_df["Profit"] / 1000, width, label="Profit ($K)", color="#10B981")

        ax.set_title("Revenue vs Profit Comparison by Category ($K)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(cat_df["Category"], fontsize=11, fontweight="bold")
        ax.set_ylabel("Amount ($ Thousands)", fontsize=11)
        ax.legend(frameon=True)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for rect in rects1:
            h = rect.get_height()
            ax.annotate(f"${h:,.1f}K", xy=(rect.get_x() + rect.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")
        for rect in rects2:
            h = rect.get_height()
            ax.annotate(f"${h:,.1f}K", xy=(rect.get_x() + rect.get_width()/2, h),
                        xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_top_10_products(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "top_10_products.png"
        top_p = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=True).tail(10)

        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        short_names = [name[:40] + "..." if len(name) > 40 else name for name in top_p.index]
        bars = ax.barh(short_names, top_p.values / 1000, color="#0284C7", height=0.6)

        ax.set_title("Top 10 Best-Selling Products by Revenue ($K)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Revenue ($ Thousands)", fontsize=11)
        ax.grid(axis="x", linestyle="--", alpha=0.5)

        for bar in bars:
            w = bar.get_width()
            ax.annotate(f"${w:,.1f}K", xy=(w, bar.get_y() + bar.get_height()/2),
                        xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_bottom_10_products(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "bottom_10_products.png"
        bot_p = df.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).tail(10)

        fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
        short_names = [name[:40] + "..." if len(name) > 40 else name for name in bot_p.index]
        bars = ax.barh(short_names, bot_p.values, color="#EF4444", height=0.6)

        ax.set_title("Top 10 Loss-Making Products (Total Profit Loss)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Cumulative Net Profit ($)", fontsize=11)
        ax.axvline(0, color="#1F2937", linewidth=1.0)
        ax.grid(axis="x", linestyle="--", alpha=0.5)

        for bar in bars:
            w = bar.get_width()
            ax.annotate(f"-${abs(w):,.0f}", xy=(w, bar.get_y() + bar.get_height()/2),
                        xytext=(-5, 0), textcoords="offset points", ha="right", va="center", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_customer_segments(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "customer_segment_analysis.png"
        seg = df.groupby("Segment").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
        colors = ["#1E3A8A", "#0284C7", "#0D9488"]

        ax1.pie(seg["Sales"], labels=seg["Segment"], autopct="%1.1f%%", colors=colors, startangle=140,
                wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
        ax1.set_title("Revenue Share by Segment", fontsize=13, fontweight="bold")

        ax2.pie(seg["Profit"], labels=seg["Segment"], autopct="%1.1f%%", colors=colors, startangle=140,
                wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2))
        ax2.set_title("Profit Share by Segment", fontsize=13, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_discount_vs_profit(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "discount_vs_profit.png"
        disc = df.groupby("Discount Band").agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum")
        ).reset_index()
        disc["Margin_%"] = ((disc["Profit"] / disc["Sales"]) * 100).round(1)

        order = ["No Discount (0%)", "Low (1-20%)", "Moderate (21-40%)", "High (>40%)"]
        disc["rank"] = disc["Discount Band"].map({k: i for i, k in enumerate(order)})
        disc = disc.sort_values(by="rank").drop(columns=["rank"])

        fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
        colors = ["#10B981" if m >= 15 else "#F59E0B" if m >= 0 else "#EF4444" for m in disc["Margin_%"]]
        bars = ax.bar(disc["Discount Band"], disc["Margin_%"], color=colors, width=0.55)

        ax.set_title("Profit Margin (%) by Discount Tier", fontsize=14, fontweight="bold", pad=15)
        ax.set_ylabel("Profit Margin (%)", fontsize=11)
        ax.axhline(0, color="#1F2937", linewidth=0.9)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        for bar in bars:
            h = bar.get_height()
            offset = 3 if h >= 0 else -10
            va = "bottom" if h >= 0 else "top"
            ax.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(0, offset), textcoords="offset points", ha="center", va=va, fontsize=10, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_sales_vs_profit(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "sales_vs_profit.png"
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        colors = df["Category"].map({"Technology": "#0284C7", "Office Supplies": "#0D9488", "Furniture": "#F59E0B"})
        ax.scatter(df["Sales"], df["Profit"], c=colors, alpha=0.6, edgecolors="none", s=30)

        ax.set_title("Sales vs. Profit by Order Transaction", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Sales ($)", fontsize=11)
        ax.set_ylabel("Profit ($)", fontsize=11)
        ax.axhline(0, color="#EF4444", linestyle="--", linewidth=1.0, alpha=0.8)
        ax.grid(True, linestyle="--", alpha=0.4)

        for cat, col in {"Technology": "#0284C7", "Office Supplies": "#0D9488", "Furniture": "#F59E0B"}.items():
            ax.scatter([], [], c=col, label=cat, alpha=0.8)
        ax.legend(title="Category", frameon=True)

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_regional_performance(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "regional_performance.png"
        reg = df.groupby(["Region", "Category"])["Sales"].sum().unstack()

        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        reg.plot(kind="bar", stacked=True, ax=ax, color=["#F59E0B", "#0D9488", "#0284C7"], width=0.6)

        ax.set_title("Regional Sales Distribution by Category ($)", fontsize=14, fontweight="bold", pad=15)
        ax.set_ylabel("Total Sales ($)", fontsize=11)
        ax.set_xlabel("Region", fontsize=11)
        ax.legend(title="Category", frameon=True)
        ax.tick_params(axis="x", rotation=0)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_yearly_growth(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "yearly_growth.png"
        yr = df.groupby("Order Year").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()

        fig, ax1 = plt.subplots(figsize=(9, 5), dpi=300)
        ax2 = ax1.twinx()

        bars = ax1.bar(yr["Order Year"].astype(str), yr["Sales"] / 1000, width=0.45, color="#1E3A8A", label="Sales ($K)")
        lines = ax2.plot(yr["Order Year"].astype(str), yr["Profit"] / 1000, color="#10B981", marker="o", linewidth=2.5, label="Profit ($K)")

        ax1.set_title("Annual Sales and Profit Growth", fontsize=14, fontweight="bold", pad=15)
        ax1.set_ylabel("Sales ($ Thousands)", fontsize=11, color="#1E3A8A")
        ax2.set_ylabel("Profit ($ Thousands)", fontsize=11, color="#10B981")
        ax1.grid(axis="y", linestyle="--", alpha=0.4)

        for bar in bars:
            h = bar.get_height()
            ax1.annotate(f"${h:,.0f}K", xy=(bar.get_x() + bar.get_width()/2, h),
                         xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    def save_shipping_performance(self, df: pd.DataFrame) -> Path:
        out_path = self.charts_dir / "shipping_performance.png"
        ship = df.groupby("Ship Mode")["Shipping Days"].mean().sort_values().reset_index()

        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
        colors = ["#10B981", "#0284C7", "#F59E0B", "#1E3A8A"]
        bars = ax.barh(ship["Ship Mode"], ship["Shipping Days"], color=colors, height=0.5)

        ax.set_title("Average Delivery Turnaround by Ship Mode (Days)", fontsize=14, fontweight="bold", pad=15)
        ax.set_xlabel("Average Days to Ship", fontsize=11)
        ax.grid(axis="x", linestyle="--", alpha=0.5)

        for bar in bars:
            w = bar.get_width()
            ax.annotate(f"{w:.1f} days", xy=(w, bar.get_y() + bar.get_height()/2),
                        xytext=(5, 0), textcoords="offset points", ha="left", va="center", fontsize=10, fontweight="bold")

        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()
        return out_path

    # =====================================================================
    # SECTION 2: INTERACTIVE PLOTLY FIGURES (For Streamlit Dashboard)
    # =====================================================================

    @staticmethod
    def plotly_revenue_profit_trend(df: pd.DataFrame) -> go.Figure:
        """Monthly Revenue & Profit line chart with dual axis and formatted tooltips."""
        m_df = df.groupby("Order Year Month").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        m_df = m_df.sort_values(by="Order Year Month")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(
                x=m_df["Order Year Month"], y=m_df["Sales"],
                name="Revenue ($)",
                line=dict(color="#0284C7", width=3),
                marker=dict(size=6, color="#0284C7"),
                mode="lines+markers",
                hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
            ),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(
                x=m_df["Order Year Month"], y=m_df["Profit"],
                name="Profit ($)",
                line=dict(color="#10B981", width=2.5, dash="dot"),
                marker=dict(size=5, color="#10B981"),
                mode="lines+markers",
                hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>"
            ),
            secondary_y=True
        )
        fig.update_layout(
            title=dict(text="<b>Monthly Revenue and Profit Trajectory</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            template="plotly_white",
            hovermode="x unified",
            margin=dict(l=45, r=45, t=55, b=35),
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(size=11, color="#334155")),
            height=370
        )
        fig.update_yaxes(
            title=dict(text="Revenue ($)", font=dict(size=11, color="#0284C7")),
            secondary_y=False,
            tickprefix="$",
            showgrid=True,
            gridcolor="#F1F5F9",
            tickfont=dict(size=10, color="#475569")
        )
        fig.update_yaxes(
            title=dict(text="Profit ($)", font=dict(size=11, color="#10B981")),
            secondary_y=True,
            tickprefix="$",
            showgrid=False,
            tickfont=dict(size=10, color="#475569")
        )
        fig.update_xaxes(tickangle=-45, showgrid=False, tickfont=dict(size=10, color="#475569"))
        return fig

    @staticmethod
    def plotly_sales_by_region(df: pd.DataFrame) -> go.Figure:
        """Donut chart for regional sales share with readable labels and legend."""
        reg = df.groupby("Region")["Sales"].sum().reset_index()
        fig = px.pie(
            reg, values="Sales", names="Region", hole=0.52,
            color="Region",
            color_discrete_map={"West": "#0284C7", "East": "#10B981", "Central": "#F59E0B", "South": "#EC4899"}
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(size=12, color="#FFFFFF", family="Arial Black"),
            hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
        )
        fig.update_layout(
            title=dict(text="<b>Sales Distribution by Region</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            template="plotly_white",
            margin=dict(l=20, r=20, t=55, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11, color="#334155")),
            height=370
        )
        return fig

    @staticmethod
    def plotly_category_profitability(df: pd.DataFrame) -> go.Figure:
        """Grouped bar chart for category Sales and Profit with legible data labels."""
        cat = df.groupby("Category").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        fig = go.Figure(data=[
            go.Bar(
                name="Revenue", x=cat["Category"], y=cat["Sales"],
                marker_color="#1E3A8A", text=[f"${s/1000:,.1f}K" for s in cat["Sales"]], textposition="outside",
                hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.2f}<extra></extra>"
            ),
            go.Bar(
                name="Profit", x=cat["Category"], y=cat["Profit"],
                marker_color="#10B981", text=[f"${p/1000:,.1f}K" for p in cat["Profit"]], textposition="outside",
                hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.2f}<extra></extra>"
            )
        ])
        fig.update_layout(
            barmode="group",
            title=dict(text="<b>Category Revenue vs Profit Comparison</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            template="plotly_white",
            margin=dict(l=45, r=25, t=55, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1, font=dict(size=11, color="#334155")),
            height=370
        )
        fig.update_yaxes(tickprefix="$", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11, color="#475569"))
        fig.update_xaxes(tickfont=dict(size=12, color="#1E293B", weight=600))
        return fig

    @staticmethod
    def plotly_subcategory_performance(df: pd.DataFrame) -> go.Figure:
        """Horizontal bar chart for Sub-Category profit with loss highlighting and un-truncated labels."""
        sub = df.groupby("Sub-Category")["Profit"].sum().sort_values().reset_index()
        colors = ["#EF4444" if p < 0 else "#10B981" for p in sub["Profit"]]

        fig = go.Figure(go.Bar(
            x=sub["Profit"], y=sub["Sub-Category"],
            orientation="h", marker_color=colors,
            text=[f"${p:,.0f}" for p in sub["Profit"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Net Profit: $%{x:,.2f}<extra></extra>"
        ))
        fig.update_layout(
            title=dict(text="<b>Sub-Category Net Profit (Red = Loss Maker)</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            xaxis_title=dict(text="Net Profit ($)", font=dict(size=11, color="#475569")),
            template="plotly_white",
            margin=dict(l=110, r=40, t=55, b=35),
            height=430
        )
        fig.update_xaxes(tickprefix="$", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#475569"))
        fig.update_yaxes(tickfont=dict(size=11, color="#1E293B", weight=500))
        return fig

    @staticmethod
    def plotly_top_products(df: pd.DataFrame, n: int = 10) -> go.Figure:
        """Top N Products by Sales with clean, readable left labels."""
        top_p = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=True).tail(n).reset_index()
        top_p["Short_Name"] = top_p["Product Name"].apply(lambda x: x[:32] + "..." if len(x) > 32 else x)

        fig = go.Figure(go.Bar(
            x=top_p["Sales"], y=top_p["Short_Name"],
            orientation="h", marker_color="#0284C7",
            text=[f"${s:,.0f}" for s in top_p["Sales"]],
            textposition="outside",
            customdata=top_p["Product Name"],
            hovertemplate="<b>%{customdata}</b><br>Revenue: $%{x:,.2f}<extra></extra>"
        ))
        fig.update_layout(
            title=dict(text=f"<b>Top {n} Products by Gross Revenue</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            template="plotly_white",
            xaxis_title=dict(text="Revenue ($)", font=dict(size=11, color="#475569")),
            margin=dict(l=140, r=50, t=55, b=35),
            height=420
        )
        fig.update_xaxes(tickprefix="$", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#475569"))
        fig.update_yaxes(tickfont=dict(size=11, color="#1E293B"))
        return fig

    @staticmethod
    def plotly_bottom_products(df: pd.DataFrame, n: int = 10) -> go.Figure:
        """Bottom N Loss-Making Products with readable labels and clear loss formatting."""
        bot_p = df.groupby("Product Name")["Profit"].sum().sort_values(ascending=False).tail(n).reset_index()
        bot_p["Short_Name"] = bot_p["Product Name"].apply(lambda x: x[:32] + "..." if len(x) > 32 else x)

        fig = go.Figure(go.Bar(
            x=bot_p["Profit"], y=bot_p["Short_Name"],
            orientation="h", marker_color="#EF4444",
            text=[f"-${abs(p):,.0f}" for p in bot_p["Profit"]],
            textposition="outside",
            customdata=bot_p["Product Name"],
            hovertemplate="<b>%{customdata}</b><br>Total Loss: $%{x:,.2f}<extra></extra>"
        ))
        fig.update_layout(
            title=dict(text=f"<b>Top {n} Loss-Generating Products (Total Net Loss)</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            template="plotly_white",
            xaxis_title=dict(text="Net Loss ($)", font=dict(size=11, color="#475569")),
            margin=dict(l=140, r=50, t=55, b=35),
            height=420
        )
        fig.update_xaxes(tickprefix="$", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#475569"))
        fig.update_yaxes(tickfont=dict(size=11, color="#1E293B"))
        return fig

    @staticmethod
    def plotly_customer_segments(df: pd.DataFrame) -> go.Figure:
        """Donut chart for customer segments with clear callouts."""
        seg = df.groupby("Segment")["Sales"].sum().reset_index()
        fig = px.pie(
            seg, values="Sales", names="Segment", hole=0.50,
            color_discrete_sequence=["#1E3A8A", "#0284C7", "#0D9488"]
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            textfont=dict(size=12, color="#FFFFFF", family="Arial Black"),
            hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.2f}<br>Share: %{percent}<extra></extra>"
        )
        fig.update_layout(
            title=dict(text="<b>Sales by Customer Segment</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            template="plotly_white",
            margin=dict(l=20, r=20, t=55, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5, font=dict(size=11, color="#334155")),
            height=370
        )
        return fig

    @staticmethod
    def plotly_discount_impact(df: pd.DataFrame) -> go.Figure:
        """Bar chart showing margin degradation by discount band with readable labels."""
        disc = df.groupby("Discount Band").agg(Sales=("Sales", "sum"), Profit=("Profit", "sum")).reset_index()
        disc["Margin_%"] = ((disc["Profit"] / disc["Sales"]) * 100).round(1)

        order = ["No Discount (0%)", "Low (1-20%)", "Moderate (21-40%)", "High (>40%)"]
        disc["rank"] = disc["Discount Band"].map({k: i for i, k in enumerate(order)})
        disc = disc.sort_values(by="rank").drop(columns=["rank"])

        colors = ["#10B981" if m >= 15 else "#F59E0B" if m >= 0 else "#EF4444" for m in disc["Margin_%"]]
        fig = go.Figure(go.Bar(
            x=disc["Discount Band"], y=disc["Margin_%"],
            marker_color=colors,
            text=[f"{m:.1f}%" for m in disc["Margin_%"]],
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Realized Margin: %{y:.1f}%<extra></extra>"
        ))
        fig.update_layout(
            title=dict(text="<b>Realized Profit Margin (%) by Discount Tier</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            yaxis_title=dict(text="Profit Margin (%)", font=dict(size=11, color="#475569")),
            template="plotly_white",
            margin=dict(l=45, r=25, t=55, b=35),
            height=390
        )
        fig.update_yaxes(ticksuffix="%", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=11, color="#475569"))
        fig.update_xaxes(tickfont=dict(size=11, color="#1E293B", weight=600))
        return fig

    @staticmethod
    def plotly_state_performance(df: pd.DataFrame) -> go.Figure:
        """Bar chart of top 5 and bottom 5 states by profit with visible labels."""
        st = df.groupby("State")["Profit"].sum().reset_index()
        top5 = st.sort_values(by="Profit", ascending=False).head(5)
        bot5 = st.sort_values(by="Profit", ascending=True).head(5)
        combined = pd.concat([bot5, top5]).sort_values(by="Profit")

        colors = ["#EF4444" if p < 0 else "#10B981" for p in combined["Profit"]]
        fig = go.Figure(go.Bar(
            x=combined["Profit"], y=combined["State"], orientation="h",
            marker_color=colors,
            text=[f"${p:,.0f}" if p >= 0 else f"-${abs(p):,.0f}" for p in combined["Profit"]],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Net Profit: $%{x:,.2f}<extra></extra>"
        ))
        fig.update_layout(
            title=dict(text="<b>State Profitability: Top 5 vs Bottom 5</b>", font=dict(size=15, color="#0F172A"), x=0.01),
            font=PLOTLY_FONT,
            xaxis_title=dict(text="Net Profit ($)", font=dict(size=11, color="#475569")),
            template="plotly_white",
            margin=dict(l=110, r=45, t=55, b=35),
            height=430
        )
        fig.update_xaxes(tickprefix="$", showgrid=True, gridcolor="#F1F5F9", tickfont=dict(size=10, color="#475569"))
        fig.update_yaxes(tickfont=dict(size=11, color="#1E293B", weight=500))
        return fig


if __name__ == "__main__":
    from src.data_cleaning import DataCleaner
    cleaner = DataCleaner()
    df_data = cleaner.load_raw_data()
    df_clean = cleaner.clean_and_engineer(df_data)

    vis = Visualizer()
    generated = vis.generate_all_static_charts(df_clean)
    print("\nGenerated Charts:")
    for k, p in generated.items():
        print(f"- {k}: {p.name}")
