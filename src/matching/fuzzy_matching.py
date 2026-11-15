

import re
import pandas as pd
from rapidfuzz import fuzz


def normalize_model(value):
    value = str(value).lower().strip()

    value = re.sub(r"([a-z])([0-9])", r"\1 \2", value)
    value = re.sub(r"([0-9])([a-z])", r"\1 \2", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    value = re.sub(r"\s+", " ", value).strip()

    return value


candidates = pd.read_csv(
    "data/processed/fuzzy_candidates.csv",
    low_memory=False
)

reference = pd.read_csv(
    "data/processed/fuzzy_reference.csv",
    low_memory=False
)

reference["normalized_model"] = (
    reference["nhtsa_model"].apply(normalize_model)
)

results = []
review_details = []

print("CrossLot - Fuzzy Matching V3")
print("----------------------------")

for _, candidate in candidates.iterrows():

    make = str(candidate["manufacturer"]).strip().lower()
    model = normalize_model(candidate["model"])
    year = int(candidate["year"])

    possible_matches = reference[
        (reference["nhtsa_make"] == make)
        & ((reference["nhtsa_year"] - year).abs() <= 1)
    ].copy()

    if possible_matches.empty:
        results.append({
            "id": candidate["id"],
            "fuzzy_match_make": None,
            "fuzzy_match_model": None,
            "fuzzy_match_year": None,
            "similarity_score": 0,
            "fuzzy_status": "no_candidate"
        })

        review_details.append({
            "id": candidate["id"],
            "candidate_model": model,
            "candidate_year": year,
            "best_model": None,
            "best_year": None,
            "best_score": 0,
            "second_model": None,
            "second_year": None,
            "second_score": 0,
            "year_difference": None
        })
        continue

    possible_matches["similarity_score"] = (
        possible_matches["normalized_model"].apply(
            lambda ref_model: fuzz.ratio(model, ref_model)
        )
    )

    possible_matches["year_difference"] = (
        possible_matches["nhtsa_year"] - year
    ).abs()

    possible_matches = possible_matches.sort_values(
        by=["similarity_score", "year_difference"],
        ascending=[False, True]
    ).reset_index(drop=True)

    best = possible_matches.iloc[0]
    second = (
        possible_matches.iloc[1]
        if len(possible_matches) > 1
        else None
    )

    best_score = best["similarity_score"]

    # Ambiguous only when the top candidates are similarly ranked
    # by model similarity and equally close in year.
    ambiguous = (
        second is not None
        and best_score - second["similarity_score"] < 3
        and best["year_difference"] == second["year_difference"]
    )

    if best_score >= 90 and not ambiguous:
        status = "matched"
    elif best_score >= 80:
        status = "needs_review"
    else:
        status = "unmatched"

    results.append({
        "id": candidate["id"],
        "fuzzy_match_make": best["nhtsa_make"],
        "fuzzy_match_model": best["nhtsa_model"],
        "fuzzy_match_year": int(best["nhtsa_year"]),
        "similarity_score": round(best_score, 2),
        "fuzzy_status": status
    })

    review_details.append({
        "id": candidate["id"],
        "candidate_model": model,
        "candidate_year": year,
        "best_model": best["nhtsa_model"],
        "best_year": int(best["nhtsa_year"]),
        "best_score": round(best_score, 2),
        "second_model": second["nhtsa_model"] if second is not None else None,
        "second_year": int(second["nhtsa_year"]) if second is not None else None,
        "second_score": round(second["similarity_score"], 2) if second is not None else None,
        "year_difference": int(best["year_difference"])
    })


results_df = pd.DataFrame(results)
review_df = pd.DataFrame(review_details)

results_path = "data/processed/fuzzy_matching_results_v3.csv"
review_path = "data/processed/fuzzy_matching_review_v3.csv"

results_df.to_csv(results_path, index=False)
review_df.to_csv(review_path, index=False)

print("\nMatching Summary:")
print(results_df["fuzzy_status"].value_counts())

print("\nTotal processed:", len(results_df))
print("Results saved to:", results_path)
print("Review details saved to:", review_path)
