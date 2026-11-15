
import csv
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from airflow.sdk import dag, task
from airflow.sdk.bases.hook import BaseHook


PROJECT_PATH = Path("/mnt/c/Users/abdul/CrossLot")
PROCESSED_FILE = PROJECT_PATH / "data/processed/vehicles_final_resolved.csv"


@dag(
    dag_id="crosslot_pipeline",
    description="CrossLot Data Engineering Pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["CrossLot", "Data Engineering"],
)
def crosslot_pipeline():

    @task
    def check_project_files():
        if not PROCESSED_FILE.exists():
            raise FileNotFoundError(
                f"Missing file: {PROCESSED_FILE}"
            )

        print("CrossLot project files found!")
        print(f"Processed dataset: {PROCESSED_FILE}")

    @task
    def validate_dataset():
        required_columns = {
            "id",
            "analytics_make",
            "analytics_year",
        }

        seen_ids = set()
        row_count = 0
        duplicate_ids = 0
        missing_required = 0

        with open(
            PROCESSED_FILE,
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:

            reader = csv.DictReader(file)

            if not reader.fieldnames:
                raise ValueError("CSV file has no header")

            missing_columns = required_columns - set(
                reader.fieldnames
            )

            if missing_columns:
                raise ValueError(
                    f"Missing columns: {missing_columns}"
                )

            for row in reader:
                row_count += 1
                listing_id = row["id"].strip()

                if not listing_id:
                    missing_required += 1

                elif listing_id in seen_ids:
                    duplicate_ids += 1

                else:
                    seen_ids.add(listing_id)

                if (
                    not row["analytics_make"].strip()
                    or not row["analytics_year"].strip()
                ):
                    missing_required += 1

        print(f"Total records: {row_count}")
        print(f"Duplicate IDs: {duplicate_ids}")
        print(f"Missing required values: {missing_required}")

        if row_count == 0:
            raise ValueError("Dataset is empty")

        if duplicate_ids > 0:
            raise ValueError("Duplicate listing IDs found")

        if missing_required > 0:
            raise ValueError("Missing required values found")



        print("Data validation passed successfully!")

    @task
    def check_warehouse():

        # Get SQL Server connection from Airflow
        conn = BaseHook.get_connection("crosslot_sql")
        extra = conn.extra_dejson

        connection_string = (
            f"DRIVER={{{extra['driver']}}};"
            f"SERVER={conn.host},{conn.port};"
            f"DATABASE={conn.schema};"
            f"UID={conn.login};"
            f"PWD={conn.password};"
            f"Encrypt={extra['Encrypt']};"
            f"TrustServerCertificate={extra['TrustServerCertificate']};"
        )

        engine = create_engine(
            "mssql+pyodbc:///?odbc_connect="
            + quote_plus(connection_string)
        )

        required_tables = {
            "dw.DimVehicle",
            "dw.DimLocation",
            "dw.DimDate",
            "dw.DimCondition",
            "dw.DimSeller",
            "dw.FactVehicleListings",
        }

        try:
            with engine.connect() as connection:

                result = connection.execute(
                    text("""
                        SELECT TABLE_SCHEMA, TABLE_NAME
                        FROM INFORMATION_SCHEMA.TABLES
                        WHERE TABLE_TYPE = 'BASE TABLE'
                    """)
                )

                existing_tables = {
                    f"{row[0]}.{row[1]}"
                    for row in result
                }

                missing_tables = (
                    required_tables - existing_tables
                )

                if missing_tables:
                    raise ValueError(
                        f"Missing warehouse tables: {missing_tables}"
                    )

                fact_count = connection.execute(
                    text(
                        "SELECT COUNT_BIG(*) "
                        "FROM dw.FactVehicleListings"
                    )
                ).scalar_one()

                print("SQL Server connection successful!")
                print("All six warehouse tables exist.")
                print(
                    f"FactVehicleListings records: {fact_count}"
                )

                if fact_count == 0:
                    raise ValueError(
                        "FactVehicleListings is empty"
                    )

                print("Warehouse validation passed!")

        finally:
            engine.dispose()

    @task
    def pipeline_ready():
        print(
            "CrossLot pipeline completed successfully!"
        )

    (
        check_project_files()
        >> validate_dataset()
        >> check_warehouse()
        >> pipeline_ready()
    )


crosslot_pipeline()

