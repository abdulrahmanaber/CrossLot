
import pandas as pd
import requests
import os
import time

INPUT_PATH = "data/processed/vehicles_vin_inspected.csv"
OUTPUT_PATH = "data/processed/nhtsa_vin_decoded_all.csv"

BATCH_SIZE = 50
MAX_RETRIES = 3

df = pd.read_csv(INPUT_PATH)

# Keep valid VINs and remove duplicates
valid = df[df["vin_status"] == "valid_format"].copy()
valid = valid.dropna(subset=["vin_clean", "year"])
valid = valid.drop_duplicates(subset=["vin_clean"])

# Resume from previously saved results
if os.path.exists(OUTPUT_PATH):
    existing = pd.read_csv(OUTPUT_PATH)
    processed_vins = set(existing["VIN"].astype(str).str.upper())
else:
    existing = pd.DataFrame()
    processed_vins = set()

valid = valid[
    ~valid["vin_clean"].astype(str).str.upper().isin(processed_vins)
]

print("CrossLot - Full VIN Decoder")
print("---------------------------")
print("Unique VINs to process:", len(valid))
print("Already processed:", len(processed_vins))

url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/"

session = requests.Session()
total_success = 0

for start in range(0, len(valid), BATCH_SIZE):

    batch = valid.iloc[start:start + BATCH_SIZE]

    vin_list = [
        f"{row['vin_clean']},{int(row['year'])}"
        for _, row in batch.iterrows()
    ]

    payload = {
        "format": "json",
        "data": ";".join(vin_list)
    }

    print(
        f"\nProcessing batch "
        f"{start // BATCH_SIZE + 1} "
        f"({len(vin_list)} VINs)"
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.post(
                url,
                data=payload,
                timeout=60
            )
            response.raise_for_status()

            results = response.json()["Results"]

            if len(results) != len(vin_list):
                raise ValueError("Unexpected number of API results")

            result_df = pd.DataFrame(results)

            result_df.to_csv(
                OUTPUT_PATH,
                mode="a",
                header=not os.path.exists(OUTPUT_PATH),
                index=False
            )

            success = (
                result_df["ErrorCode"].astype(str).str.strip() == "0"
            ).sum()

            total_success += int(success)

            print("Received:", len(results))
            print("Successful decodes:", success)

            break

        except (requests.RequestException, ValueError, KeyError) as error:
            print(f"Attempt {attempt} failed:", error)

            if attempt == MAX_RETRIES:
                raise RuntimeError(
                    "Batch failed. Previous results were saved. "
                    "Run the script again to resume."
                ) from error

            time.sleep(3 * attempt)

    time.sleep(1)

print("\nFull VIN Processing Completed!")
print("Successful decodes in this run:", total_success)
print("Output:", OUTPUT_PATH)

