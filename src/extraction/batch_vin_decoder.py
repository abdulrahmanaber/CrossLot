
import pandas as pd
import requests
import os

input_path = "data/processed/vehicles_vin_inspected.csv"
output_path = "data/processed/nhtsa_vin_decoded.csv"

df = pd.read_csv(input_path)

# Select valid and unique VINs
sample = (
    df[df["vin_status"] == "valid_format"]
    .drop_duplicates(subset=["vin_clean"])
    .head(50)
)

# Prepare batch data
vin_list = [
    f"{row['vin_clean']},{int(row['year'])}"
    for _, row in sample.iterrows()
]

url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/"

payload = {
    "format": "json",
    "data": ";".join(vin_list)
}

print("CrossLot - Batch VIN Decoder")
print("-----------------------------")
print("Unique VINs to process:", len(vin_list))

try:
    response = requests.post(url, data=payload, timeout=60)
    response.raise_for_status()

    results = response.json()["Results"]

    decoded_df = pd.DataFrame(results)

    os.makedirs("data/processed", exist_ok=True)
    decoded_df.to_csv(output_path, index=False)

    print("\nBatch Processing Completed!")
    print("Received Results:", len(decoded_df))

    if "ErrorCode" in decoded_df.columns:
        print("Successful Decodes:",
              (decoded_df["ErrorCode"].astype(str).str.strip() == "0").sum())

    print("Saved to:", output_path)

except requests.exceptions.RequestException as error:
    print("API Request Failed:", error)

except (ValueError, KeyError) as error:
    print("API Response Error:", error)
