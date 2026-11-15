
import pandas as pd
from sqlalchemy import text

from sql_server_connection import get_sql_server_engine


print("CrossLot - Load DimLocation")
print("---------------------------")

columns = [
    "region",
    "state",
    "address_city",
    "county",
    "address_postal_code",
    "address_country",
    "lat",
    "long"
]

df = pd.read_csv(
    "data/processed/vehicles_final_resolved.csv",
    usecols=columns,
    low_memory=False
)

print("Source records:", len(df))

df = df.rename(columns={
    "region": "Region",
    "state": "State",
    "address_city": "City",
    "county": "County",
    "address_postal_code": "PostalCode",
    "address_country": "Country",
    "lat": "Latitude",
    "long": "Longitude"
})

# Remove duplicate locations
df = df.drop_duplicates().copy()

# Clean text values
text_columns = [
    "Region", "State", "City", "County",
    "PostalCode", "Country"
]

for column in text_columns:
    df[column] = df[column].map(
        lambda value: value.strip() if isinstance(value, str) else value
    )

# Convert coordinates to numeric
for column in ["Latitude", "Longitude"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Convert missing values to None
df = df.astype(object).where(pd.notna(df), None)

print("Unique location records:", len(df))

engine = get_sql_server_engine()

try:
    df.to_sql(
        name="DimLocation",
        con=engine,
        schema="dw",
        if_exists="append",
        index=False,
        chunksize=500
    )

    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM dw.DimLocation")
        ).scalar()

    print("DimLocation loaded successfully!")
    print("Rows in SQL Server:", count)

finally:
    engine.dispose()
