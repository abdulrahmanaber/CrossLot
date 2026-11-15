
import pandas as pd

input_path = "data/processed/vehicles_standardized.csv"

df = pd.read_csv(input_path)

# Clean VIN without changing the original column
df["vin_clean"] = df["VIN"].astype("string").str.strip().str.upper()

# Identify missing VIN values
missing_vin = df["vin_clean"].isna() | (df["vin_clean"] == "")

# Standard VIN format: 17 characters, excluding I, O, Q
valid_vin = df["vin_clean"].str.fullmatch(
    r"[A-HJ-NPR-Z0-9]{17}", na=False
)

df["vin_status"] = "nonstandard_or_invalid_format"
df.loc[missing_vin, "vin_status"] = "missing"
df.loc[valid_vin, "vin_status"] = "valid_format"

# Print report
print("CrossLot - VIN Inspection")
print("-------------------------")

print("Total Records:", len(df))
print("Missing VIN:", missing_vin.sum())
print("Valid Format VIN:", valid_vin.sum())
print("Nonstandard or Invalid Format:", 
      ((~missing_vin) & (~valid_vin)).sum())

print("\nVIN Status:")
print(df["vin_status"].value_counts())

print("\nSample VIN Records:")
print(df[["VIN", "vin_clean", "vin_status"]].head(15))

# Save inspection results
output_path = "data/processed/vehicles_vin_inspected.csv"
df.to_csv(output_path, index=False)

print("\nSaved successfully:", output_path)
