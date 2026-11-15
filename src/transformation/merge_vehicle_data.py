
import pandas as pd

print("CrossLot - Final Vehicle Resolution")
print("-----------------------------------")

# 1. Load vehicle data
vehicles = pd.read_csv(
    "data/processed/vehicles_vin_inspected.csv",
    dtype={"vin_clean": str, "id": str}
)

# 2. Load NHTSA decoded data
nhtsa = pd.read_csv(
    "data/processed/nhtsa_vin_classified.csv",
    dtype={"VIN": str}
)

# 3. Load Fuzzy Matching V3 results
fuzzy = pd.read_csv(
    "data/processed/fuzzy_matching_results_v3.csv",
    dtype={"id": str}
)

print("Vehicles records:", len(vehicles))
print("NHTSA records:", len(nhtsa))
print("Fuzzy records:", len(fuzzy))

# 4. Prepare NHTSA data
nhtsa_selected = nhtsa[
    ["VIN", "Make", "Model", "ModelYear", "decode_status"]
].copy()

nhtsa_selected = nhtsa_selected.rename(
    columns={
        "VIN": "vin_clean",
        "Make": "nhtsa_make",
        "Model": "nhtsa_model",
        "ModelYear": "nhtsa_year"
    }
)

nhtsa_selected = nhtsa_selected.drop_duplicates(
    subset=["vin_clean"]
)

# 5. Merge vehicles with NHTSA
merged = vehicles.merge(
    nhtsa_selected,
    on="vin_clean",
    how="left",
    validate="many_to_one"
)

# 6. VIN resolution indicators
merged["vin_decoded"] = merged["decode_status"].notna()

merged["vin_match"] = (
    merged["decode_status"] == "success"
)

merged["vin_needs_review"] = (
    merged["decode_status"].isin([
        "needs_review",
        "partial_success",
        "unsupported_year"
    ])
)

# 7. Merge Fuzzy results using unique vehicle ID
merged = merged.merge(
    fuzzy,
    on="id",
    how="left",
    validate="one_to_one"
)

# 8. Fuzzy resolution indicators
fuzzy_matched = merged["fuzzy_status"] == "matched"
fuzzy_review = merged["fuzzy_status"] == "needs_review"

# 9. Determine resolution status
merged["resolution_status"] = "not_processed"

merged.loc[
    merged["fuzzy_status"].notna(),
    "resolution_status"
] = "unmatched"

merged.loc[
    fuzzy_review,
    "resolution_status"
] = "fuzzy_needs_review"

merged.loc[
    fuzzy_matched,
    "resolution_status"
] = "fuzzy_matched"

merged.loc[
    merged["vin_decoded"] & ~merged["vin_match"],
    "resolution_status"
] = "vin_decode_needs_review"

merged.loc[
    merged["vin_match"],
    "resolution_status"
] = "vin_matched"

# 10. Determine resolution method
merged["resolution_method"] = "none"

merged.loc[
    merged["fuzzy_status"].notna(),
    "resolution_method"
] = "fuzzy_make_model_year"

merged.loc[
    merged["vin_decoded"] & ~merged["vin_match"],
    "resolution_method"
] = "vin_decode_review"

merged.loc[
    merged["vin_match"],
    "resolution_method"
] = "vin"

# 11. Create resolved vehicle attributes
merged["resolved_make"] = merged["nhtsa_make"].where(
    merged["vin_match"]
)

merged["resolved_model"] = merged["nhtsa_model"].where(
    merged["vin_match"]
)

merged["resolved_year"] = merged["nhtsa_year"].where(
    merged["vin_match"]
)

# Use fuzzy values only for confirmed fuzzy candidates
merged.loc[fuzzy_matched, "resolved_make"] = (
    merged.loc[fuzzy_matched, "fuzzy_match_make"]
)

merged.loc[fuzzy_matched, "resolved_model"] = (
    merged.loc[fuzzy_matched, "fuzzy_match_model"]
)

merged.loc[fuzzy_matched, "resolved_year"] = (
    merged.loc[fuzzy_matched, "fuzzy_match_year"]
)

# Analytics fallback attributes
merged["analytics_make"] = (
    merged["resolved_make"]
    .fillna(merged["manufacturer"])
)

merged["analytics_model"] = (
    merged["resolved_model"]
    .fillna(merged["model"])
)

merged["analytics_year"] = (
    merged["resolved_year"]
    .fillna(merged["year"])
)

# 12. Validation
print("\nResolution Results")
print("------------------")

print("Total vehicles:", len(merged))
print("\nResolution status:")
print(merged["resolution_status"].value_counts(dropna=False))

print("\nResolution method:")
print(merged["resolution_method"].value_counts(dropna=False))

print("\nVIN matches:", merged["vin_match"].sum())
print("Fuzzy matches:", fuzzy_matched.sum())

print("\nDuplicate IDs:", merged["id"].duplicated().sum())

# 13. Save final dataset
output_path = "data/processed/vehicles_final_resolved.csv"

merged.to_csv(output_path, index=False)

print("\nSaved:", output_path)
print("Final shape:", merged.shape)
