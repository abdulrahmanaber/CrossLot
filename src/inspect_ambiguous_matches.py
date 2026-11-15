
import pandas as pd

results = pd.read_csv(
    "data/processed/fuzzy_matching_results_v3.csv"
)

review = pd.read_csv(
    "data/processed/fuzzy_matching_review_v3.csv"
)

audit = results.merge(review, on="id", how="left")

ambiguous = audit[
    (audit["fuzzy_status"] == "needs_review")
    & (audit["best_score"] >= 95)
]

print("CrossLot - Ambiguous Matches Inspection")
print("---------------------------------------")

print("High-score cases needing review:", len(ambiguous))

print(
    ambiguous[
        [
            "candidate_model",
            "candidate_year",
            "best_model",
            "best_year",
            "best_score",
            "second_model",
            "second_year",
            "second_score",
            "year_difference"
        ]
    ].to_string(index=False)
)
