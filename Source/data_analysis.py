# Student Name: Odai Al Massri
# Student FAN: alma0360
# File: data_analysis.py
# Date: 05-10-2026
# Description: Combines and exports the preprocessed CICIoV2024 data.

from pathlib import Path
import pandas as pd
from data_preprocessing import Preprocessed_DataFrame


# Finds the project root folder and creates an Output folder.
Project_Root = Path(__file__).resolve().parent.parent
Output_Folder = Project_Root / "Output"
Output_Folder.mkdir(exist_ok=True)


# Stores each prepared dataset before they are combined.
model_data = []
metadata_data = []


# Gets the prepared features, targets and metadata from preprocessing.
for file_name, data in Preprocessed_DataFrame.items():

    model_df = data["X"].copy()
    model_df["y_binary"] = data["y_binary"]
    model_df["y_multiclass"] = data["y_multiclass"]

    metadata_df = data["metadata"].copy()

    model_data.append(model_df)
    metadata_data.append(metadata_df)

    print(file_name, "added to analysis output")


# Stops if no preprocessed datasets were received.
if len(model_data) == 0:
    raise ValueError("No preprocessed datasets were received.")


# Combines all six prepared datasets into shared outputs.
Combined_Model_DataFrame = pd.concat(
    model_data,
    ignore_index=True
)

Combined_Metadata_DataFrame = pd.concat(
    metadata_data,
    ignore_index=True
)


# Checks that the model data and metadata still contain the same number of rows.
if len(Combined_Model_DataFrame) != len(Combined_Metadata_DataFrame):
    raise ValueError("Model data and metadata rows are not aligned.")


# Creates a simple class-count summary.
Class_Summary = (
    Combined_Metadata_DataFrame["specific_class"]
    .value_counts()
    .rename_axis("specific_class")
    .reset_index(name="count")
)


# Saves the final prepared outputs.
Combined_Model_DataFrame.to_csv(
    Output_Folder / "ml_ready.csv",
    index=False
)

Combined_Metadata_DataFrame.to_csv(
    Output_Folder / "metadata.csv",
    index=False
)

Class_Summary.to_csv(
    Output_Folder / "class_summary.csv",
    index=False
)


print("\nDATA ANALYSIS AND OUTPUT")
print("__________________________")
print("Prepared datasets:", len(Preprocessed_DataFrame))
print("Total rows:", len(Combined_Model_DataFrame))
print("\nSpecific class counts:")
print(Class_Summary)
print("\nOutput files saved in:", Output_Folder)
