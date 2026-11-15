
import pandas as pd

candidates = pd.read_csv(
    "data/processed/fuzzy_candidates.csv",
    low_memory=False
)

results = pd.read_csv(
    "data/processed/fuzzy_matching_results_v3.csv"
)

# Combine original data with matching results
audit = candidates.merge(
    results,
    on="id",
    how="left"
)

print("CrossLot - Fuzzy Matching Quality Inspection")
print("--------------------------------------------")

print("\nStatus Distribution:")
print(audit["fuzzy_status"].value_counts())

print("\nSimilarity Score Statistics:")
print(
    audit.groupby("fuzzy_status")["similarity_score"]
    .describe()
    .round(2)
)

print("\nStrong Matches Sample:")
print(
    audit[audit["fuzzy_status"] == "matched"][
        [
            "manufacturer",
            "model",
            "year",
            "fuzzy_match_make",
            "fuzzy_match_model",
            "fuzzy_match_year",
            "similarity_score"
        ]
    ].head(15).to_string(index=False)
)

print("\nNeeds Review Sample:")
print(
    audit[audit["fuzzy_status"] == "needs_review"][
        [
            "manufacturer",
            "model",
            "year",
            "fuzzy_match_model",
            "fuzzy_match_year",
            "similarity_score"
        ]
    ].head(15).to_string(index=False)
)

