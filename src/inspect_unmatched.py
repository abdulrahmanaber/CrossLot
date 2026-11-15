
import pandas as pd

df = pd.read_csv(
    "data/processed/vehicles_nhtsa_merged.csv",
    low_memory=False
)

unmatched = df[df["vin_match"] == False].copy()

print("CrossLot - Fuzzy Matching Preparation")
print("-------------------------------------")

print("\nVIN Status Distribution:")
print(unmatched["vin_status"].value_counts(dropna=False))

print("\nManufacturer Distribution:")
print(unmatched["manufacturer"].value_counts().head(15))

# Exclude unknown and missing values
candidates = unmatched[
    unmatched["manufacturer"].notna()
    & unmatched["model"].notna()
    & unmatched["year"].notna()
    & (unmatched["manufacturer"].str.lower() != "unknown")
    & (unmatched["model"].str.lower() != "unknown")
].copy()

print("\nFuzzy Matching Candidates:", len(candidates))

print("\nSample Candidates:")
print(
    candidates[
        ["vin_status", "manufacturer", "model", "year", "price"]
    ].head(10).to_string(index=False)
)
