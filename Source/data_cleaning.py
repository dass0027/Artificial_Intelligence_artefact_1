# Student Name: Antonio
# Student FAN: aran0039
# File: data_cleaning.py
# Date: 22-09-2026
# Description: Cleans validated CICIoV2024 data before preprocessing.

import pandas as pd

from data_validation import (
    Validated_DataFrame,
    EXPECTED_COLUMNS,
    NUMERIC_COLUMNS,
    BYTE_COLUMNS,
    VALID_LABELS,
    VALID_CATEGORIES,
    VALID_SPECIFIC_CLASSES,
    SPOOFING_CLASSES,
)


# Stores the cleaned version of each validated CSV file.
Cleaned_DataFrame = {}


for file_name, df in Validated_DataFrame.items():

    # Makes a copy so the validated data is not changed directly.
    cleaned_df = df.copy()
    original_rows = len(cleaned_df)

    # Removes unexpected columns that are not part of the agreed dataset structure.
    unexpected_columns = []

    for column in cleaned_df.columns:
        if column not in EXPECTED_COLUMNS:
            unexpected_columns.append(column)

    if unexpected_columns:
        cleaned_df = cleaned_df.drop(columns=unexpected_columns)


    # Checks whether any required columns are missing.
    missing_columns = []

    for column in EXPECTED_COLUMNS:
        if column not in cleaned_df.columns:
            missing_columns.append(column)

    # A file with missing required columns cannot be cleaned reliably.
    if missing_columns:
        print(
            file_name,
            "cannot be cleaned because columns are missing:",
            missing_columns
        )
        continue


    # Converts columns that should contain numbers into numeric values.
    # Invalid text values become missing values.
    for column in NUMERIC_COLUMNS:
        cleaned_df[column] = pd.to_numeric(
            cleaned_df[column],
            errors="coerce"
        )


    # Removes rows containing missing values.
    cleaned_df = cleaned_df.dropna(
        subset=EXPECTED_COLUMNS
    )


    # Removes rows containing byte values outside 0 to 255.
    for column in BYTE_COLUMNS:

        cleaned_df = cleaned_df[
            (cleaned_df[column] >= 0) &
            (cleaned_df[column] <= 255)
        ]


    # Removes rows containing byte values that are not whole numbers.
    for column in BYTE_COLUMNS:

        cleaned_df = cleaned_df[
            cleaned_df[column] % 1 == 0
        ]


    # Removes rows containing unexpected labels.
    cleaned_df = cleaned_df[
        cleaned_df["label"].isin(VALID_LABELS)
    ]


    # Removes rows containing unexpected categories.
    cleaned_df = cleaned_df[
        cleaned_df["category"].isin(VALID_CATEGORIES)
    ]


    # Removes rows containing unexpected specific classes.
    cleaned_df = cleaned_df[
        cleaned_df["specific_class"].isin(
            VALID_SPECIFIC_CLASSES
        )
    ]


    # Removes rows where label, category and specific_class contradict each other.
    valid_benign = (
        (cleaned_df["label"] == "BENIGN")
        & (cleaned_df["category"] == "BENIGN")
        & (cleaned_df["specific_class"] == "BENIGN")
    )

    valid_dos = (
        (cleaned_df["label"] == "ATTACK")
        & (cleaned_df["category"] == "DoS")
        & (cleaned_df["specific_class"] == "DoS")
    )

    valid_spoofing = (
        (cleaned_df["label"] == "ATTACK")
        & (cleaned_df["category"] == "SPOOFING")
        & (cleaned_df["specific_class"].isin(SPOOFING_CLASSES))
    )

    cleaned_df = cleaned_df[
        valid_benign | valid_dos | valid_spoofing
    ]


    # Repeated CAN messages are kept because repeated messages can be legitimate.


    # Resets row numbers after invalid rows have been removed.
    cleaned_df = cleaned_df.reset_index(drop=True)


    # Stores the cleaned file for the preprocessing stage.
    Cleaned_DataFrame[file_name] = cleaned_df


    removed_rows = original_rows - len(cleaned_df)

    print("\nCleaning summary for", file_name)
    print("Original rows:", original_rows)
    print("Rows removed:", removed_rows)
    print("Cleaned rows:", len(cleaned_df))


print("\nDATA CLEANING COMPLETE")
print("Files cleaned:", len(Cleaned_DataFrame))
