
import re
from rapidfuzz import fuzz


def normalize_model(value):
    value = str(value).lower().strip()

    # Separate letters and numbers
    value = re.sub(r"([a-z])([0-9])", r"\1 \2", value)
    value = re.sub(r"([0-9])([a-z])", r"\1 \2", value)

    # Remove punctuation
    value = re.sub(r"[^a-z0-9]+", " ", value)

    # Remove extra spaces
    value = re.sub(r"\s+", " ", value).strip()

    return value


examples = [
    ("F250", "F-250"),
    ("F150", "F-150"),
    ("LS 460 Luxury", "LS"),
    ("Prius", "Prius V"),
    ("Camry LE Hybrid", "Camry"),
    ("Mustang GT", "Mustang"),
    ("Tundra Crewmax TRD Pro", "Tundra"),
]

print("CrossLot - Model Normalization Test")
print("-----------------------------------")

for original, reference in examples:
    clean_original = normalize_model(original)
    clean_reference = normalize_model(reference)

    score = fuzz.ratio(clean_original, clean_reference)

    print(f"\nOriginal: {original}")
    print(f"Reference: {reference}")
    print(f"Normalized: {clean_original} | {clean_reference}")
    print(f"Similarity: {score:.2f}")
