# Name: Krish Anand | anan0117
# Loading dataset decimal CSV into Pandas DataFrame

from pathlib import Path
import pandas as pd

Project_Root = Path(__file__).resolve().parent.parent     # Finding Project Root Folder
Data_Folder = Project_Root / "Data"                       # Location of Dataset

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
        print("Missing File", file_name)

DataFrame = {}

for file_name in Decimal_Files:
            file_path = Data_Folder / file_name

            if file_path.exists():
                df = pd.read_csv(file_path)
                DataFrame[file_name] = df

                print(f"Loaded {file_name} "
                      f"with {df.shape[0]} rows and {df.shape[1]} columns")

                

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
