# Student Name: Dulina Dassanayake 
# Student FAN: dass0027
# File: data_preprocessing.py
# Date: 24-09-2026
# Description: Pre process the CICIoV2024 data.

from data_cleaning import Cleaned_DataFrame


#Encode labels for binary classification
binary_mapping = {
    "BENIGN": 0,
    "ATTACK": 1
}

#Encode labels for multiclass classification 
multiclass_mapping = {
    "BENIGN": 0,
    "DoS": 1,
    "GAS": 2,
    "RPM": 3,
    "SPEED": 4,
    "STEERING_WHEEL": 5
}

feature_columns = [
    "ID",
    "DATA_0",
    "DATA_1",
    "DATA_2",
    "DATA_3",
    "DATA_4",
    "DATA_5",
    "DATA_6",
    "DATA_7"
]

#Store the data set and prepared features and metadata
Preprocessed_DataFrame = {}

for file_name, df in Cleaned_DataFrame.items():

    if df.empty:
        raise ValueError(f"{file_name}: dataset is empty")

    X = df[feature_columns].copy()

    # Reject missing or infinite feature values.
    if X.isna().any().any() or X.isin(
        [float("inf"), float("-inf")]
    ).any().any():
        raise ValueError(
            f"{file_name}: features contain missing or infinite values"
        )

    y_binary = df["label"].map(binary_mapping)
    y_multiclass = df["specific_class"].map(multiclass_mapping)

    if y_binary.isna().any() or y_multiclass.isna().any():
        raise ValueError(f"Unexpected or missing labels in {file_name}")

    metadata = df[["label", "category", "specific_class"]].copy()
    metadata["source_file"] = file_name

    # checking every feature row matchs its targets and metadata.
    if not X.index.equals(y_binary.index):
        raise ValueError(f"{file_name}: binary target rows are not aligned")

    if not X.index.equals(y_multiclass.index):
        raise ValueError(f"{file_name}: multiclass target rows are not aligned")

    if not X.index.equals(metadata.index):
        raise ValueError(f"{file_name}: metadata rows are not aligned")

    Preprocessed_DataFrame[file_name] = {
        "X": X,
        "y_binary": y_binary.astype("int64"),
        "y_multiclass": y_multiclass.astype("int64"),
        "metadata": metadata
    }

    print(f"{file_name}: prepared {len(X)} rows")


#Checking the out put 
if len(Preprocessed_DataFrame) != 6:
    raise ValueError("Expected all six prepared datasets.")

print("\nDATA PREPROCESSING COMPLETE")
print("Prepared datasets:", len(Preprocessed_DataFrame))
