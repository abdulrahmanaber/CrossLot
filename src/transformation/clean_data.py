
import pandas as pd
import os

file_path = "data/raw/vehicles_data.csv"
output_path = "data/processed/vehicles_with_quality_flags.csv"

# Read only 10,000 rows for testing
df = pd.read_csv(file_path, nrows=10000)

# Add data quality flags
df["invalid_price"] = (df["price"] <= 0) | (df["price"] > 500000)

df["suspicious_year"] = (
    (df["year"] < 1980) | (df["year"] > 2026)
)

df["suspicious_odometer"] = df["odometer"] > 500000

# Display quality report
print("CrossLot - Data Quality Report")
print("--------------------------------")

print("Invalid Prices:", df["invalid_price"].sum())
print("Suspicious Years:", df["suspicious_year"].sum())
print("Suspicious Odometers:", df["suspicious_odometer"].sum())

# Save data without deleting any records
os.makedirs("data/processed", exist_ok=True)

df.to_csv(output_path, index=False)

print("\nOutput saved successfully:")
print(output_path)
print("Final Shape:", df.shape)
