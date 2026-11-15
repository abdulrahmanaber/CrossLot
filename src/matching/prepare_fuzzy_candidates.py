
import pandas as pd

df = pd.read_csv(
    "data/processed/vehicles_nhtsa_merged.csv",
    low_memory=False
)

candidates = df[
    (df["vin_match"] == False)
    & (df["manufacturer"].notna())
    & (df["model"].notna())
    & (df["year"].notna())
    & (df["manufacturer"].str.lower() != "unknown")
    & (df["model"].str.lower() != "unknown")
].copy()

fuzzy_candidates = candidates[
    candidates["year"].between(1985, 2027)
].copy()

older_vehicles = candidates[
    candidates["year"] < 1985
].copy()

fuzzy_candidates.to_csv(
    "data/processed/fuzzy_candidates.csv",
    index=False
)

older_vehicles.to_csv(
    "data/processed/older_unmatched.csv",
    index=False
)

print("Total candidates:", len(candidates))
print("Fuzzy candidates:", len(fuzzy_candidates))
print("Older unmatched:", len(older_vehicles))
print("\nFiles saved successfully.")

