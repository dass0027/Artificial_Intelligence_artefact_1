# Student Name: Krish Anand
# Student FAN: anan0117
# File: data_ingestion.py
# Date: 05-10-2026
# Description: Automatically downloads and loads the CICIoV2024 decimal CSV files.

from pathlib import Path
from urllib.request import urlretrieve
import pandas as pd

Project_Root = Path(__file__).resolve().parent.parent     # Finding Project Root Folder
Data_Folder = Project_Root / "Data"                       # Location of Dataset
Data_Folder.mkdir(exist_ok=True)                           # Creates Data folder if it is missing

Dataset_URL = "https://github.com/dass0027/Artificial_Intelligence_artefact_1/releases/download/dataset-v1/"

print("Project root:", Project_Root)
print("Data Folder", Data_Folder)

Decimal_Files = [
    "decimal_benign.csv",
    "decimal_DoS.csv",
    "decimal_spoofing-GAS.csv",
    "decimal_spoofing-RPM.csv",
    "decimal_spoofing-SPEED.csv",
    "decimal_spoofing-STEERING_WHEEL.csv"
]

print("\nDataset Files Expected:")
print("____________________________")
for file_name in Decimal_Files:
    file_path = Data_Folder / file_name

    if file_path.exists():
        print("File Found", file_name)
    else:
        print("Downloading", file_name)

        try:
            urlretrieve(Dataset_URL + file_name, file_path)
            print("Downloaded", file_name)
        except Exception as error:
            print("Download failed for", file_name)
            print(error)

DataFrame = {}

for file_name in Decimal_Files:
    file_path = Data_Folder / file_name

    if file_path.exists():
        df = pd.read_csv(file_path)
        DataFrame[file_name] = df

        print(
            f"Loaded {file_name} "
            f"with {df.shape[0]} rows and {df.shape[1]} columns"
        )

print("__________________________")
print("DATA ACQUISITION")
print("Krish Anand | anan0117")
print("__________________________")
print(f"Expected Files: {len(Decimal_Files)}")
print(f"Loaded Files: {len(DataFrame)}")

if len(DataFrame) == len(Decimal_Files):
    print("ALL FILES ARE LOADED CORRECTLY")
else:
    print("SOME FILES NOT LOADED")
    raise FileNotFoundError("Not all CICIoV2024 decimal CSV files could be loaded.")
