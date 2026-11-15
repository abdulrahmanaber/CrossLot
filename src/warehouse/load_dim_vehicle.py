
import pandas as pd
from sqlalchemy import text

from sql_server_connection import get_sql_server_engine


print("CrossLot - Load DimVehicle")
print("--------------------------")

# Load required columns
columns = [
    "analytics_make",
    "analytics_model",
    "analytics_year",
    "fuel",
    "transmission",
    "drive",
    "type",
    "cylinders",
    "size",
    "paint_color"
]

df = pd.read_csv(
    "data/processed/vehicles_final_resolved.csv",
    usecols=columns,
    low_memory=False
)

print("Source records:", len(df))

# Rename columns
df = df.rename(columns={
    "analytics_make": "Make",
    "analytics_model": "Model",
    "analytics_year": "ModelYear",
    "fuel": "Fuel",
    "transmission": "Transmission",
    "drive": "Drive",
    "type": "VehicleType",
    "cylinders": "Cylinders",
    "size": "VehicleSize",
    "paint_color": "PaintColor"
})

# Remove duplicate vehicle combinations
df = df.drop_duplicates().copy()

# Convert missing values to None
df = df.astype(object).where(pd.notna(df), None)

print("Unique vehicle records:", len(df))

# Load into SQL Server
engine = get_sql_server_engine()

try:
    df.to_sql(
        name="DimVehicle",
        con=engine,
        schema="dw",
        if_exists="append",
        index=False,
        chunksize=500
    )

    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM dw.DimVehicle")
        ).scalar()

    print("DimVehicle loaded successfully!")
    print("Rows in SQL Server:", count)

finally:
    engine.dispose()
