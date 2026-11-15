
import pandas as pd

df = pd.read_csv(
    "data/processed/vehicles_nhtsa_merged.csv",
    low_memory=False
)

# Keep records with successful NHTSA decoding
reference = df[
    df["decode_status"] == "success"
].copy()

# Select canonical vehicle attributes
reference = reference[
    ["nhtsa_make", "nhtsa_model", "nhtsa_year"]
].dropna()

# Remove duplicate vehicle combinations
reference = reference.drop_duplicates()

# Normalize text
reference["nhtsa_make"] = (
    reference["nhtsa_make"].str.strip().str.lower()
)

reference["nhtsa_model"] = (
    reference["nhtsa_model"].str.strip().str.lower()
)

output_path = "data/processed/fuzzy_reference.csv"
reference.to_csv(output_path, index=False)

print("CrossLot - Fuzzy Reference Preparation")
print("--------------------------------------")
print("Reference records:", len(reference))
print("\nSample:")
print(reference.head(10).to_string(index=False))
print("\nSaved to:", output_path)
