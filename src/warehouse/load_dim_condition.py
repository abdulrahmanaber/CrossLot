
import pandas as pd
from sqlalchemy import text

from sql_server_connection import get_sql_server_engine


print("CrossLot - Load DimCondition")
print("----------------------------")

df = pd.read_csv(
    "data/processed/vehicles_final_resolved.csv",
    usecols=["condition", "title_status"],
    low_memory=False
)

print("Source records:", len(df))

df = df.rename(columns={
    "condition": "VehicleCondition",
    "title_status": "TitleStatus"
})

# Remove duplicate condition combinations
df = df.drop_duplicates().copy()

# Clean text values
for column in ["VehicleCondition", "TitleStatus"]:
    df[column] = df[column].map(
        lambda value: value.strip() if isinstance(value, str) else value
    )

# Convert missing values to None
df = df.astype(object).where(pd.notna(df), None)

print("Unique condition records:", len(df))

engine = get_sql_server_engine()

try:
    df.to_sql(
        name="DimCondition",
        con=engine,
        schema="dw",
        if_exists="append",
        index=False,
        chunksize=500
    )

    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM dw.DimCondition")
        ).scalar()

    print("DimCondition loaded successfully!")
    print("Rows in SQL Server:", count)

finally:
    engine.dispose()
