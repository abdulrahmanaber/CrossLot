
import pandas as pd

df = pd.read_csv(
    "data/processed/vehicles_nhtsa_merged.csv",
    low_memory=False
)

reference = pd.read_csv(
    "data/processed/fuzzy_reference.csv"
)

candidates = df[
    (df["vin_match"] == False)
    & (df["manufacturer"] != "unknown")
    & (df["model"] != "unknown")
    & (df["year"].notna())
].copy()

print("Candidate Year Range:")
print(candidates["year"].describe())

print("\nReference Year Range:")
print(reference["nhtsa_year"].describe())

print("\nCandidate Years Sample:")
print(candidates["year"].value_counts().sort_index().head(15))

print("\nReference Years Sample:")
print(reference["nhtsa_year"].value_counts().sort_index().head(15))

