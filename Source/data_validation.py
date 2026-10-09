# Student Name: Tanio
# Student FAN: barr0555
# File: data_validation.py
# Date: 22-09-2026
# Description: Validates the CICIoV2024 data loaded by the acquisition module.


import pandas as pd
from data_ingestion import DataFrame


# A reference list for the "expected" columns for every CICIoV2024 decimal CSV file. 
EXPECTED_COLUMNS = [
    "ID",
    "DATA_0",
    "DATA_1",
    "DATA_2",
    "DATA_3",
    "DATA_4",
    "DATA_5",
    "DATA_6",
    "DATA_7",
    "label",
    "category",
    "specific_class"
]


          
# A reference list of the columns that should contain numerical values in every CSV file
NUMERIC_COLUMNS = [
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


# Checks that the "NUMERIC_COLUMNS" in every file is of numeric data.
for file_name, df in DataFrame.items():

    print("\nData type check for", file_name) 

    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            if not pd.api.types.is_numeric_dtype(df[column]): 
                print(column, "is not numeric")



                
# A reference list of the columns that should contain values from 0 to 255.
BYTE_COLUMNS = [
    "DATA_0",
    "DATA_1",
    "DATA_2",
    "DATA_3",
    "DATA_4",
    "DATA_5",
    "DATA_6",
    "DATA_7"
]

# Checks that whether any values in the  "BYTE_COLUMNS" are outside the valid byte range.
for file_name, df in DataFrame.items():

    for column in BYTE_COLUMNS:

        if column in df.columns: # Finds rows where value is not in valid byte range

            if pd.api.types.is_numeric_dtype(df[column]): 

                invalid_values = df[
                    (df[column] < 0) | (df[column] > 255) 
                ]

                if len(invalid_values) > 0: # Counts number of rows not in valid byte range 
                    print(
                        file_name,
                        column,
                        "has",
                        len(invalid_values),
                        "values outside 0-255"
                    )




 # A reference list of the valid text values in the dataset.
VALID_LABELS = [
    "BENIGN",
    "ATTACK"
]

VALID_CATEGORIES = [
    "BENIGN",
    "DoS",
    "SPOOFING"
]

VALID_SPECIFIC_CLASSES = [
    "BENIGN",
    "DoS",
    "GAS",
    "RPM",
    "SPEED",
    "STEERING_WHEEL"
]

# A reference list of the specific classes that belong to the SPOOFING category.
SPOOFING_CLASSES = [
    "GAS",
    "RPM",
    "SPEED",
    "STEERING_WHEEL"
]

# Checks for unexpected label, category and specific_class in every file, not in the reference list.
for file_name, df in DataFrame.items():

    if "label" in df.columns:
        for value in df["label"].unique(): # Gets every different value in the label column
            if value not in VALID_LABELS: # Reports if label is not of reference list
                print(file_name, "has unexpected label:", value) 

    if "category" in df.columns:
        for value in df["category"].unique(): # Same 
            if value not in VALID_CATEGORIES: # Same
                print(file_name, "has unexpected category:", value) 

    if "specific_class" in df.columns:
        for value in df["specific_class"].unique(): # Same 
            if value not in VALID_SPECIFIC_CLASSES: # Same 
                print(file_name, "has unexpected specific class:", value)


# Checks whether any byte values contain decimals instead of whole numbers.
for file_name, df in DataFrame.items():

    for column in BYTE_COLUMNS:

        if column in df.columns:

            if pd.api.types.is_numeric_dtype(df[column]):

                fractional_values = df[
                    df[column].notna() & (df[column] % 1 != 0)
                ]

                if len(fractional_values) > 0:
                    print(
                        file_name,
                        column,
                        "has",
                        len(fractional_values),
                        "values that are not whole numbers"
                    )


# Checks that label, category and specific_class agree with each other.
for file_name, df in DataFrame.items():

    if (
        "label" in df.columns
        and "category" in df.columns
        and "specific_class" in df.columns
    ):

        valid_benign = (
            (df["label"] == "BENIGN")
            & (df["category"] == "BENIGN")
            & (df["specific_class"] == "BENIGN")
        )

        valid_dos = (
            (df["label"] == "ATTACK")
            & (df["category"] == "DoS")
            & (df["specific_class"] == "DoS")
        )

        valid_spoofing = (
            (df["label"] == "ATTACK")
            & (df["category"] == "SPOOFING")
            & (df["specific_class"].isin(SPOOFING_CLASSES))
        )

        contradictory_rows = df[
            ~(valid_benign | valid_dos | valid_spoofing)
        ]

        if len(contradictory_rows) > 0:
            print(
                file_name,
                "has",
                len(contradictory_rows),
                "rows with contradictory labels"
            )


 # Checks for repeated rows in each file.
for file_name, df in DataFrame.items():

    duplicate_count = df.duplicated().sum()

    print(
        file_name,
        "has",
        duplicate_count,
        "repeated rows"
    )               


# Checks whether expected columns are missing or unexpected columns are present.
for file_name, df in DataFrame.items():

    missing_columns = []
    unexpected_columns = []

    # Checks for missing expected columns.
    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            missing_columns.append(column)

    # Checks for additional columns that are not expected.
    for column in df.columns:
        if column not in EXPECTED_COLUMNS:
            unexpected_columns.append(column)

    if missing_columns:
        print(file_name, "is missing columns:", missing_columns)
    else:
        print(file_name, "has all expected columns")

    if unexpected_columns:
        print(file_name, "has unexpected columns:", unexpected_columns)



print("VALIDATION SUMMARY:")

for file_name, df in DataFrame.items():

    missing_columns = []
    unexpected_columns = []
    non_numeric_columns = []

    invalid_byte_values = 0
    fractional_byte_values = 0
    contradictory_label_rows = 0
    unexpected_labels = []
    unexpected_categories = []
    unexpected_specific_classes = []

    # Missing columns.
    for column in EXPECTED_COLUMNS:
        if column not in df.columns:
            missing_columns.append(column)

    # Unexpected columns.
    for column in df.columns:
        if column not in EXPECTED_COLUMNS:
            unexpected_columns.append(column)

    # Missing values.
    missing_value_count = df.isnull().sum().sum()

    # Non-numeric columns.
    for column in NUMERIC_COLUMNS:

        if column in df.columns:

            if not pd.api.types.is_numeric_dtype(df[column]):
                non_numeric_columns.append(column)

    # Invalid byte values.
    for column in BYTE_COLUMNS:

        if column in df.columns:

            if pd.api.types.is_numeric_dtype(df[column]):

                invalid_values = df[
                    (df[column] < 0) | (df[column] > 255)
                ]

                invalid_byte_values += len(invalid_values)

                fractional_values = df[
                    df[column].notna() & (df[column] % 1 != 0)
                ]

                fractional_byte_values += len(fractional_values)

    # Unexpected labels.
    if "label" in df.columns:

        for value in df["label"].unique():

            if value not in VALID_LABELS:
                unexpected_labels.append(value)

    # Unexpected categories.
    if "category" in df.columns:

        for value in df["category"].unique():

            if value not in VALID_CATEGORIES:
                unexpected_categories.append(value)

    # Unexpected specific classes.
    if "specific_class" in df.columns:

        for value in df["specific_class"].unique():

            if value not in VALID_SPECIFIC_CLASSES:
                unexpected_specific_classes.append(value)

    # Checks that label, category and specific_class agree with each other.
    if (
        "label" in df.columns
        and "category" in df.columns
        and "specific_class" in df.columns
    ):

        valid_benign = (
            (df["label"] == "BENIGN")
            & (df["category"] == "BENIGN")
            & (df["specific_class"] == "BENIGN")
        )

        valid_dos = (
            (df["label"] == "ATTACK")
            & (df["category"] == "DoS")
            & (df["specific_class"] == "DoS")
        )

        valid_spoofing = (
            (df["label"] == "ATTACK")
            & (df["category"] == "SPOOFING")
            & (df["specific_class"].isin(SPOOFING_CLASSES))
        )

        contradictory_rows = df[
            ~(valid_benign | valid_dos | valid_spoofing)
        ]

        contradictory_label_rows = len(contradictory_rows)

    # Repeated rows are reported but are not automatically considered invalid.
    duplicate_count = df.duplicated().sum()

    print("\nFile:", file_name)

    print("Missing columns:", len(missing_columns))
    print("Unexpected columns:", len(unexpected_columns))
    print("Missing values:", missing_value_count)
    print("Non-numeric columns:", len(non_numeric_columns))
    print("Invalid byte values:", invalid_byte_values)
    print("Fractional byte values:", fractional_byte_values)
    print("Contradictory label rows:", contradictory_label_rows)
    print("Unexpected labels:", len(unexpected_labels))
    print("Unexpected categories:", len(unexpected_categories))
    print(
        "Unexpected specific classes:",
        len(unexpected_specific_classes)
    )
    print("Repeated rows:", duplicate_count)

    # Repeated rows are excluded from failure because repeated CAN messages
    # can be legitimate.
    if (
        len(missing_columns) == 0
        and len(unexpected_columns) == 0
        and missing_value_count == 0
        and len(non_numeric_columns) == 0
        and invalid_byte_values == 0
        and fractional_byte_values == 0
        and contradictory_label_rows == 0
        and len(unexpected_labels) == 0
        and len(unexpected_categories) == 0
        and len(unexpected_specific_classes) == 0
    ):
        print("Validation Status: PASSED")

    else:
        print("Validation Status: ISSUES FOUND")

                
 # Passes the validated DataFrames to the data cleaning stage.
Validated_DataFrame = DataFrame
                    
