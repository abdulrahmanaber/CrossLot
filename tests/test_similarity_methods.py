
from rapidfuzz import fuzz

examples = [
    ("ls 460 luxury", "ls"),
    ("prius", "prius v"),
    ("camry le hybrid", "camry"),
    ("mustang gt", "mustang"),
    ("tundra crewmax trd pro", "tundra"),
    ("silverado 1500 lt z71", "silverado"),
    ("f250", "f-250"),
]

print("CrossLot - Similarity Methods Comparison")
print("----------------------------------------")

for original, reference in examples:
    print(f"\nOriginal:  {original}")
    print(f"Reference: {reference}")
    print("Ratio:", fuzz.ratio(original, reference))
    print("Token Sort:", fuzz.token_sort_ratio(original, reference))
    print("Token Set:", fuzz.token_set_ratio(original, reference))
    print("WRatio:", fuzz.WRatio(original, reference))

