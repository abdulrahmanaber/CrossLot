
import pandas as pd
import os

input_path = "data/processed/vehicles_with_quality_flags.csv"
output_path = "data/processed/vehicles_standardized.csv"

df = pd.read_csv(input_path)

# Columns to standardize
columns = [
    "manufacturer",
    "fuel",
    "transmission",
    "drive",
    "type",
    "condition",
    "title_status"
]

# Preserve original values
for col in columns:
    df[f"{col}_original"] = df[col]

    # Remove extra spaces and standardize text
    df[col] = df[col].apply(
        lambda x: x.strip().lower() if isinstance(x, str) else x
    )

    # Replace missing values
    df[col] = df[col].fillna("unknown")

# Save standardized data
os.makedirs("data/processed", exist_ok=True)

df.to_csv(output_path, index=False)

print("CrossLot - Data Standardization")
print("--------------------------------")

for col in columns:
    print(f"{col}: {df[col].nunique()} unique values")

print("\nMissing values after standardization:")
print(df[columns].isnull().sum())

print("\nSaved successfully:", output_path)
print("Final Shape:", df.shape)
