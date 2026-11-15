
import pandas as pd
import requests

input_path = "data/processed/vehicles_vin_inspected.csv"

df = pd.read_csv(input_path)

# Select 5 VINs with valid format
sample = df[df["vin_status"] == "valid_format"].head(5)

# Prepare VINs with model years
vin_list = []

for _, row in sample.iterrows():
    vin = row["vin_clean"]
    year = row["year"]

    vin_list.append(f"{vin},{int(year)}")

# NHTSA API endpoint
url = "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/"

payload = {
    "format": "json",
    "data": ";".join(vin_list)
}

print("CrossLot - NHTSA API Test")
print("-------------------------")
print("Sending", len(vin_list), "VINs...")

try:
    response = requests.post(url, data=payload, timeout=30)
    response.raise_for_status()

    results = response.json()["Results"]

    print("\nAPI Response:")
    for vehicle in results:
        print("-------------------------")
        print("VIN:", vehicle.get("VIN"))
        print("Make:", vehicle.get("Make"))
        print("Model:", vehicle.get("Model"))
        print("Model Year:", vehicle.get("ModelYear"))
        print("Vehicle Type:", vehicle.get("VehicleType"))
        print("Error Code:", vehicle.get("ErrorCode"))

    print("\nSuccessfully received", len(results), "results.")

except requests.exceptions.RequestException as error:
    print("API Request Failed:", error)

except (ValueError, KeyError) as error:
    print("Invalid API Response:", error)
