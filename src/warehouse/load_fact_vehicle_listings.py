

import pandas as pd
from sqlalchemy import text

from sql_server_connection import get_sql_server_engine


print("CrossLot - Load FactVehicleListings")
print("-----------------------------------")

# 1. Load source data
source_columns = [
    "id", "price", "odometer", "image_count",
    "invalid_price", "suspicious_year", "suspicious_odometer",
    "resolution_status", "resolution_method", "similarity_score",
    "analytics_make", "analytics_model", "analytics_year",
    "fuel", "transmission", "drive", "type",
    "cylinders", "size", "paint_color",
    "region", "state", "address_city", "county",
    "address_postal_code", "address_country", "lat", "long",
    "posting_date", "updated_date",
    "condition", "title_status", "seller_type"
]

df = pd.read_csv(
    "data/processed/vehicles_final_resolved.csv",
    usecols=source_columns,
    low_memory=False
)

print("Source records:", len(df))

df["id"] = df["id"].astype("string").str.strip()

if df["id"].isna().any() or df["id"].duplicated().any():
    raise ValueError("Missing or duplicate listing IDs.")

# 2. Prepare vehicle attributes
vehicle_columns = [
    "analytics_make", "analytics_model", "analytics_year",
    "fuel", "transmission", "drive", "type",
    "cylinders", "size", "paint_color"
]

vehicle_source = df[vehicle_columns].copy()

vehicle_source.columns = [
    "Make", "Model", "ModelYear", "Fuel", "Transmission",
    "Drive", "VehicleType", "Cylinders", "VehicleSize", "PaintColor"
]

# 3. Prepare location attributes
location_source = df[[
    "region", "state", "address_city", "county",
    "address_postal_code", "address_country", "lat", "long"
]].copy()

location_source.columns = [
    "Region", "State", "City", "County",
    "PostalCode", "Country", "Latitude", "Longitude"
]

# 4. Prepare condition and seller
condition_source = df[["condition", "title_status"]].copy()
condition_source.columns = ["VehicleCondition", "TitleStatus"]

seller_source = df[["seller_type"]].copy()
seller_source.columns = ["SellerType"]

# 5. Read dimension tables
engine = get_sql_server_engine()

try:
    with engine.connect() as connection:
        dim_vehicle = pd.read_sql(
            text("SELECT * FROM dw.DimVehicle"), connection
        )

        dim_location = pd.read_sql(
            text("SELECT * FROM dw.DimLocation"), connection
        )

        dim_condition = pd.read_sql(
            text("SELECT * FROM dw.DimCondition"), connection
        )

        dim_seller = pd.read_sql(
            text("SELECT * FROM dw.DimSeller"), connection
        )

    # 6. Normalize text columns
    vehicle_text_columns = [
        "Make", "Model", "Fuel", "Transmission", "Drive",
        "VehicleType", "Cylinders", "VehicleSize", "PaintColor"
    ]
    vehicle_columns = list(vehicle_source.columns)

    for column in vehicle_text_columns:
        for frame in [vehicle_source, dim_vehicle]:
            frame[column] = frame[column].map(
                lambda v: str(v).strip() if pd.notna(v) else None
            )

    vehicle_source["ModelYear"] = pd.to_numeric(
        vehicle_source["ModelYear"], errors="coerce"
    )

    dim_vehicle["ModelYear"] = pd.to_numeric(
        dim_vehicle["ModelYear"], errors="coerce"
    )

    location_text_columns = [
        "Region", "State", "City", "County", "PostalCode", "Country"
    ]

    for column in location_text_columns:
        for frame in [location_source, dim_location]:
            frame[column] = frame[column].map(
                lambda v: str(v).strip() if pd.notna(v) else None
            )

    for column in ["Latitude", "Longitude"]:
        for frame in [location_source, dim_location]:
            frame[column] = pd.to_numeric(
                frame[column], errors="coerce"
            ).round(7)

    for column in ["VehicleCondition", "TitleStatus"]:
        for frame in [condition_source, dim_condition]:
            frame[column] = frame[column].map(
                lambda v: str(v).strip() if pd.notna(v) else None
            )

    for frame in [seller_source, dim_seller]:
        frame["SellerType"] = frame["SellerType"].map(
            lambda v: str(v).strip() if pd.notna(v) else None
        )

    # 7. Build dimension lookup tables
    vehicle_map = dim_vehicle[
        ["VehicleKey"] + vehicle_columns
    ].copy()

    location_map = dim_location[
        ["LocationKey"] + location_text_columns +
        ["Latitude", "Longitude"]
    ].copy()

    condition_map = dim_condition[
        ["ConditionKey", "VehicleCondition", "TitleStatus"]
    ].copy()

    seller_map = dim_seller[
        ["SellerKey", "SellerType"]
    ].copy()

    work = pd.concat([
        df[["id"]].reset_index(drop=True),
        vehicle_source.reset_index(drop=True),
        location_source.reset_index(drop=True),
        condition_source.reset_index(drop=True),
        seller_source.reset_index(drop=True)
    ], axis=1)

    # 8. Match dimension keys
    work = work.merge(
        vehicle_map,
        on=vehicle_columns,
        how="left",
        validate="many_to_one"
    )

    location_columns = location_text_columns + [
        "Latitude", "Longitude"
    ]

    work = work.merge(
        location_map,
        on=location_columns,
        how="left",
        validate="many_to_one"
    )

    work = work.merge(
        condition_map,
        on=["VehicleCondition", "TitleStatus"],
        how="left",
        validate="many_to_one"
    )

    work = work.merge(
        seller_map,
        on="SellerType",
        how="left",
        validate="many_to_one"
    )

    # 9. Generate date keys
    def make_date_key(value):
        if pd.isna(value):
            return None

        parsed = pd.to_datetime(
            str(value)[:10],
            format="%Y-%m-%d",
            errors="coerce"
        )

        if pd.isna(parsed):
            return None

        return int(parsed.strftime("%Y%m%d"))

    posting_keys = df["posting_date"].map(make_date_key)
    updated_keys = df["updated_date"].map(make_date_key)

    # 10. Validate dimension matches
    key_columns = [
        "VehicleKey", "LocationKey",
        "ConditionKey", "SellerKey"
    ]

    for column in key_columns:
        missing = work[column].isna().sum()

        if missing:
            raise ValueError(
                f"{missing} records have no matching {column}."
            )

    if posting_keys.isna().any():
        raise ValueError("Invalid posting dates found.")

    # Validate date keys against DimDate
    with engine.connect() as connection:
        valid_dates = set(
            pd.read_sql(
                text("SELECT DateKey FROM dw.DimDate"),
                connection
            )["DateKey"].astype(int)
        )

    if not set(posting_keys).issubset(valid_dates):
        raise ValueError("Some posting dates are missing from DimDate.")

    updated_values = set(updated_keys.dropna())

    if not updated_values.issubset(valid_dates):
        raise ValueError("Some updated dates are missing from DimDate.")

    # 11. Build final fact table
    fact = pd.DataFrame({
        "SourceListingID": df["id"],
        "VehicleKey": work["VehicleKey"],
        "LocationKey": work["LocationKey"],
        "PostingDateKey": posting_keys,
        "UpdatedDateKey": updated_keys,
        "ConditionKey": work["ConditionKey"],
        "SellerKey": work["SellerKey"],
        "Price": df["price"],
        "Odometer": df["odometer"],
        "ImageCount": df["image_count"],
        "InvalidPrice": df["invalid_price"],
        "SuspiciousYear": df["suspicious_year"],
        "SuspiciousOdometer": df["suspicious_odometer"],
        "ResolutionStatus": df["resolution_status"],
        "ResolutionMethod": df["resolution_method"],
        "SimilarityScore": df["similarity_score"]
    })

    fact = fact.astype(object).where(pd.notna(fact), None)

    print("Fact records prepared:", len(fact))
    print("All dimension keys matched successfully!")

    # 12. Load into SQL Server
    fact.to_sql(
        name="FactVehicleListings",
        con=engine,
        schema="dw",
        if_exists="append",
        index=False,
        chunksize=500
    )

    with engine.connect() as connection:
        count = connection.execute(
            text("SELECT COUNT(*) FROM dw.FactVehicleListings")
        ).scalar()

    print("FactVehicleListings loaded successfully!")
    print("Rows in SQL Server:", count)

finally:
    engine.dispose()
