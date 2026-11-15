
import pandas as pd
from sqlalchemy import text

from sql_server_connection import get_sql_server_engine


print("CrossLot - Load DimSeller")
print("-------------------------")

df = pd.read_csv(
    "data/processed/vehicles_final_resolved.csv",
    usecols=["seller_type"],
    low_memory=False
)

print("Source records:", len(df))

df = df.rename(columns={
    "seller_type": "SellerType"
})

# Clean values
df["SellerType"] = df["SellerType"].map(
    lambda value: value.strip() if isinstance(value, str) else value
)

# Remove duplicates
df = df.drop_duplicates().copy()

# SellerType is NOT NULL in SQL Server
df = df[df["SellerType"].notna()]

print("Unique seller records:", len(df))

engine = get_sql_server_engine()

try:
    df.to_sql(
        name="DimSeller",
        con=engine,
        schema="dw",
        if_exists="append",
        index=False,
        chunksize=500
    )

    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM dw.DimSeller")
        ).scalar()

    print("DimSeller loaded successfully!")
    print("Rows in SQL Server:", count)

finally:
    engine.dispose()

