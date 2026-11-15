
import pandas as pd

path = "data/processed/vehicles_nhtsa_merged.csv"

df = pd.read_csv(path, low_memory=False)

print("CrossLot - Merge Quality Validation")
print("-----------------------------------")

matched = df[df["vin_match"] == True]

print("Total records:", len(df))
print("Matched records:", len(matched))

print("\nMatched Data Completeness:")
print("Missing Make:", matched["nhtsa_make"].isna().sum())
print("Missing Model:", matched["nhtsa_model"].isna().sum())
print("Missing Year:", matched["nhtsa_year"].isna().sum())

print("\nDecode Status:")
print(matched["decode_status"].value_counts(dropna=False))

print("\nSample Matched Vehicles:")
print(
    matched[
        ["VIN", "manufacturer", "model",
         "nhtsa_make", "nhtsa_model",
         "nhtsa_year", "decode_status"]
    ].head(10).to_string(index=False)
)
