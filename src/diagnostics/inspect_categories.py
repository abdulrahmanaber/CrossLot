
import pandas as pd

file_path = "data/processed/vehicles_with_quality_flags.csv"

df = pd.read_csv(file_path)

columns = [
    "manufacturer",
    "fuel",
    "transmission",
    "drive",
    "type",
    "condition",
    "title_status"
]

print("CrossLot - Category Inspection")
print("--------------------------------")

for col in columns:
    print(f"\n{col.upper()}")
    print(df[col].value_counts(dropna=False).head(15))
