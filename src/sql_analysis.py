"""
SQL Database Management & Analytical Query Execution Module.
Manages SQLite database ingestion from processed sales data, runs business queries,
and returns analytical DataFrames.
"""

import sys
import re
import sqlite3
import logging
from pathlib import Path
import pandas as pd

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class SQLManager:
    """Manages SQLite database creation, indexing, and SQL business queries execution."""

    def __init__(self,
                 db_path: Path = config.DATABASE_FILE,
                 data_path: Path = config.PROCESSED_DATA_FILE,
                 sql_file: Path = config.SQL_QUERIES_FILE):
        self.db_path = Path(db_path)
        self.data_path = Path(data_path)
        self.sql_file = Path(sql_file)

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection to the SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(self.db_path)

    def build_database(self, force_rebuild: bool = False) -> None:
        """
        Loads cleaned CSV data and creates the SQLite database with standardized column names
        and performance indexes.
        """
        if self.db_path.exists() and not force_rebuild:
            logger.info(f"Database already exists at {self.db_path}. Skipping rebuild.")
            return

        if not self.data_path.exists():
            from src.data_cleaning import DataCleaner
            logger.info("Processed data not found. Running cleaning pipeline first...")
            cleaner = DataCleaner()
            cleaner.run_pipeline()

        logger.info(f"Ingesting processed sales data from {self.data_path} into SQLite...")
        df = pd.read_csv(self.data_path)

        # Standardize column names for clean SQL queries (replace spaces and hyphens with underscores)
        df_sql = df.copy()
        df_sql.columns = [
            c.strip().replace(" ", "_").replace("-", "_").replace("/", "_")
            for c in df_sql.columns
        ]

        with self.get_connection() as conn:
            # Write to SQLite
            df_sql.to_sql(config.DB_TABLE_NAME, conn, if_exists="replace", index=False)
            logger.info(f"Successfully wrote {len(df_sql)} rows to table '{config.DB_TABLE_NAME}'.")

            # Create Indexes for fast analytical queries
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON sales(Order_Date);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON sales(Region);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON sales(Category);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_customer ON sales(Customer_ID);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_year_month ON sales(Order_Year_Month);")
            conn.commit()
            logger.info("Created performance indexes on sales table.")

    def run_query(self, query: str) -> pd.DataFrame:
        """Executes a single SQL query string and returns a Pandas DataFrame."""
        with self.get_connection() as conn:
            return pd.read_sql_query(query, conn)

    def parse_sql_file(self) -> list:
        """
        Parses SQL_queries.sql and extracts individual queries with their numbers, titles,
        descriptions, and SQL code.
        Returns a list of dicts: [{'id': int, 'title': str, 'description': str, 'sql': str}]
        """
        if not self.sql_file.exists():
            raise FileNotFoundError(f"SQL file not found at {self.sql_file}")

        with open(self.sql_file, "r", encoding="utf-8") as f:
            content = f.read()

        pattern = re.compile(r"-- QUERY\s+(\d+):\s*([^\n]+)\n(.*?)(?=(?:-- QUERY|\Z))", re.DOTALL)
        matches = pattern.findall(content)
        parsed_queries = []

        for q_num, q_title, body in matches:
            lines = body.splitlines()
            desc_lines = []
            sql_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("--"):
                    cleaned_comment = stripped.lstrip("-").strip()
                    if cleaned_comment:
                        desc_lines.append(cleaned_comment)
                else:
                    sql_lines.append(line)

            sql = "\n".join(sql_lines).strip().rstrip(";")
            if sql:
                full_title = f"Query {q_num}: {q_title.strip()}"
                parsed_queries.append({
                    "id": int(q_num),
                    "title": full_title,
                    "description": " | ".join(desc_lines),
                    "sql": sql
                })

        logger.info(f"Parsed {len(parsed_queries)} business queries from {self.sql_file.name}.")
        return parsed_queries

    def execute_all_queries(self) -> dict:
        """Executes all 20+ queries and returns a dictionary of query results."""
        self.build_database()
        queries = self.parse_sql_file()
        results = {}

        logger.info("--- Executing SQL Business Queries Collection ---")
        for idx, q_info in enumerate(queries, 1):
            title = q_info["title"]
            try:
                df_result = self.run_query(q_info["sql"])
                results[title] = {
                    "df": df_result,
                    "description": q_info["description"],
                    "sql": q_info["sql"]
                }
                logger.info(f"[{idx}/{len(queries)}] {title} -> {len(df_result)} rows returned.")
            except Exception as e:
                logger.error(f"Error executing {title}: {e}")
                raise e

        logger.info("All SQL queries executed successfully.")
        return results


if __name__ == "__main__":
    manager = SQLManager()
    manager.build_database(force_rebuild=True)
    all_results = manager.execute_all_queries()

    print("\n" + "=" * 60)
    print(" SAMPLE SQL QUERY EXECUTION RESULTS")
    print("=" * 60)

    # Display Query 1 (KPIs)
    kpi_key = [k for k in all_results.keys() if "QUERY 1:" in k.upper()][0]
    print(f"\n{kpi_key}:\n", all_results[kpi_key]["df"].to_string(index=False))

    # Display Query 2 (Regional)
    reg_key = [k for k in all_results.keys() if "QUERY 2:" in k.upper()][0]
    print(f"\n{reg_key}:\n", all_results[reg_key]["df"].to_string(index=False))

    # Display Query 4 (Subcat leakage)
    subcat_key = [k for k in all_results.keys() if "QUERY 4:" in k.upper()][0]
    print(f"\n{subcat_key} (Loss Sub-categories):\n", all_results[subcat_key]["df"].head(5).to_string(index=False))
