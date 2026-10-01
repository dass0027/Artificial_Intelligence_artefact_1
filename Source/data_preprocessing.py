# Student Name: Dulina Dassanayake 
# Student FAN: dass0027
# File: data_preprocessing.py
# Date: 24-09-2026
# Description: Pre process the CICIoV2024 data.
import numpy as np 
from data_cleaning import Cleaned_DataFrame

for file_name, df in Cleaned_DataFrame.items():
    print (file_name, df.shape)

    print ("number of cleaned datasets:", len(Cleaned_DataFrame))

for file_name, df in Cleaned_DataFrame.items():
    print ("\nFile:", file_name)
    print ("Rows and Columns:", df.shape)
    print ("Columns:", df.columns.tolist ())
    print ("Label Counts:")
    print (df["label"].value_counts())

if Cleaned_DataFrame :
    first_file = next(iter(Cleaned_DataFrame))
    print ("Preview :", first_file)
    print (Cleaned_DataFrame [first_file].head())
else:
    print ("Cleaned data loading was unsuccessful. Check the data folder")

    feature_columns = ["ID"] + [f"DATA_{i}" for i in range (8)]

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

feature_columns = ["ID"] + [f"DATA_{i}" for i in range(8)]
#Store the data set and prepared features and metadata
Preprocessed_DataFrame = {}

for file_name, df in Cleaned_DataFrame.items():

    X = df[feature_columns].copy()

    y_binary = df ["label"].map (binary_mapping)
    y_multiclass = df["specific_class"].map(multiclass_mapping)

    if y_binary.isna().any() or y_multiclass.isna().any():
        raise ValueError (f"Unexpected or missing labels in {file_name}")

    metadata = df [["label", "category", "specific_class"]].copy()
    metadata["source_file"] = file_name 

    Preprocessed_DataFrame [file_name] = {
    "X" : X,
    "y_binary": y_binary.astype("int64"),
    "y_multiclass": y_multiclass.astype("int64"),
    "metadata": metadata
    }

    print (f"{file_name}: prepared {len(X)} rows")

    #Checking the out put 
if len(Preprocessed_DataFrame) != 6:
    raise ValueError("Expected all six prepared datasets.")

for file_name, data in Preprocessed_DataFrame.items():
    X = data["X"]
    y_binary = data["y_binary"]
    y_multiclass = data["y_multiclass"]
    metadata = data["metadata"]

    if X.empty:
        raise ValueError(f"{file_name}: dataset is empty")

    # checking the features are numeric or not
    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise ValueError(f"{file_name}: invalid feature values")

    # checking every feature row matchs its targets and metadata.
    for values in [y_binary, y_multiclass, metadata]:
        if not X.index.equals(values.index):
            raise ValueError(f"{file_name}: rows are not aligned")

    print(f"{file_name}: checks passed — {X.shape}")