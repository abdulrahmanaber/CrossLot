
import pandas as pd
from sqlalchemy import text

from sql_server_connection import get_sql_server_engine


print("CrossLot - Load DimDate")
print("-----------------------")

# Read source date columns
df = pd.read_csv(
    "data/processed/vehicles_final_resolved.csv",
    usecols=["posting_date", "updated_date"],
    low_memory=False
)

# Extract original local calendar dates
dates = set()

for column in ["posting_date", "updated_date"]:
    values = df[column].dropna().astype(str)

    for value in values:
        date_value = pd.to_datetime(
            value[:10],
            format="%Y-%m-%d",
            errors="coerce"
        )

        if pd.notna(date_value):
            dates.add(date_value.normalize())

print("Unique calendar dates:", len(dates))

# Build date dimension
date_records = []

for date_value in sorted(dates):
    date_records.append({
        "DateKey": int(date_value.strftime("%Y%m%d")),
        "FullDate": date_value.date(),
        "Year": date_value.year,
        "Quarter": date_value.quarter,
        "Month": date_value.month,
        "MonthName": date_value.strftime("%B"),
        "Day": date_value.day,
        "DayOfWeek": date_value.isoweekday(),
        "DayName": date_value.strftime("%A"),
        "IsWeekend": date_value.isoweekday() >= 6
    })

date_df = pd.DataFrame(date_records)

print("Date records prepared:", len(date_df))

engine = get_sql_server_engine()

try:
    date_df.to_sql(
        name="DimDate",
        con=engine,
        schema="dw",
        if_exists="append",
        index=False,
        chunksize=500
    )

    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM dw.DimDate")
        ).scalar()

    print("DimDate loaded successfully!")
    print("Rows in SQL Server:", count)

finally:
    engine.dispose()
