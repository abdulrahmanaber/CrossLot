
import pandas as pd

file_path = "data/raw/vehicles_data.csv"

df = pd.read_csv(file_path, nrows=10000)

print("CrossLot - Data Profiling")
print("-------------------------")

print("\nDataset Shape:")
print(df.shape)

print("\nMissing Values:")
print(df.isnull().sum().sort_values(ascending=False).head(15))

print("\nDuplicate Rows:")
print(df.duplicated().sum())

print("\nData Types:")
print(df.dtypes)

print("\nVehicle Statistics:")
print(df[["price", "year", "odometer"]].describe())



print("\nPotential Data Quality Issues:")
print("------------------------------")

checks = {
    "Zero or negative prices": df["price"] <= 0,
    "Very high prices (over $500,000)": df["price"] > 500000,
    "Years before 1980": df["year"] < 1980,
    "Future model years": df["year"] > 2026,
    "Zero or negative odometer": df["odometer"] <= 0,
    "Very high odometer (over 500,000)": df["odometer"] > 500000
}

for issue, condition in checks.items():
    print(f"{issue}: {condition.sum()}")

print("\nSuspicious Price Examples:")
print(df.loc[df["price"] > 500000, ["manufacturer", "model", "year", "price"]].head(10))

print("\nSuspicious Year Examples:")
print(df.loc[df["year"] > 2026, ["manufacturer", "model", "year", "price"]].head(10))
