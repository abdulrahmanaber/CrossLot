
import pandas as pd

path = "data/processed/nhtsa_vin_decoded_all.csv"

df = pd.read_csv(path, dtype=str)

success = df["ErrorCode"].str.strip().eq("0")
failed = df[~success]

print("CrossLot - NHTSA Results Inspection")
print("-----------------------------------")

print("Total VINs:", len(df))
print("Successful:", success.sum())
print("Not Successful:", len(failed))

print("\nError Code Distribution:")
print(df["ErrorCode"].value_counts(dropna=False))

print("\nFailed VIN Examples:")
columns = [
    col for col in
    ["VIN", "ErrorCode", "ErrorText", "Make", "Model", "ModelYear"]
    if col in df.columns
]

print(failed[columns].head(20))

print("\nMissing Make:", df["Make"].isna().sum())
print("Missing Model:", df["Model"].isna().sum())
print("Missing Model Year:", df["ModelYear"].isna().sum())


print("\nDetailed Error Messages:")
print("------------------------")

print(
    failed[["VIN", "ErrorCode", "ErrorText"]]
    .to_string(index=False)
)


def classify_status(error_code):
    code = str(error_code).strip()

    if code == "0":
        return "success"

    if code.startswith("ERROR:"):
        return "unsupported_year"

    codes = set(code.split(","))

    if "0" in codes:
        return "partial_success"

    return "needs_review"


df["decode_status"] = df["ErrorCode"].apply(classify_status)

output_path = "data/processed/nhtsa_vin_classified.csv"
df.to_csv(output_path, index=False)

print("\nDecode Status Distribution:")
print(df["decode_status"].value_counts())

print("\nSaved classified data to:", output_path)
