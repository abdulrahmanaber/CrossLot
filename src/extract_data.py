
import pandas as pd
import os

# Dataset path
file_path = "data/raw/vehicles_data.csv"

# Check if file exists
if os.path.exists(file_path):

    # Read first 10 rows
    df = pd.read_csv(file_path, nrows=10)

    print("CrossLot - Data Extraction")
    print("--------------------------")

    print("\nDataset Columns:")
    print(df.columns.tolist())

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nData Shape:")
    print(df.shape)

else:
    print("Dataset file not found!")
