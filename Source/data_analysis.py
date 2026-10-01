# Student Name: Odai Al Massri
# Student FAN: alma0360
# File: analysis_output.py
# Date: 29-09-2026
# Description: Summarises CICIoV2024 data and exports checked ML-ready outputs.
# Usage: python analysis_output.py --input-dir ../Data --output-dir ../Output

"""Analyse and export the team's CICIoV2024 decimal CSV files.

This module is the Analysis and Output stage. It streams the six agreed source
files, enforces the shared schema, reports class distributions, and exports
model features/targets separately from descriptive metadata. It does not
silently remove or repair records: data-quality problems stop the run so the
upstream validation/cleaning owner can address them.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import tempfile
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


EXPECTED_FILES = (
    "decimal_benign.csv",
    "decimal_DoS.csv",
    "decimal_spoofing-GAS.csv",
    "decimal_spoofing-RPM.csv",
    "decimal_spoofing-SPEED.csv",
    "decimal_spoofing-STEERING_WHEEL.csv",
)
EXPECTED_COLUMNS = (
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
    "specific_class",
)
FEATURE_COLUMNS = ("ID",) + tuple(f"DATA_{index}" for index in range(8))
BYTE_COLUMNS = tuple(f"DATA_{index}" for index in range(8))
LABELS = {"BENIGN", "ATTACK"}
CATEGORIES = {"BENIGN", "DoS", "SPOOFING"}
SPECIFIC_CLASSES = {"BENIGN", "DoS", "GAS", "RPM", "SPEED", "STEERING_WHEEL"}
BINARY_MAP = {"BENIGN": 0, "ATTACK": 1}
CLASS_MAP = {
    "BENIGN": 0,
    "DoS": 1,
    "GAS": 2,
    "RPM": 3,
    "SPEED": 4,
    "STEERING_WHEEL": 5,
}


def _new_file_summary() -> dict[str, Any]:
    """Create counters for one input file."""
    return {
        "rows": 0,
        "labels": Counter(),
        "categories": Counter(),
        "specific_classes": Counter(),
        "quality_issues": Counter(),
    }


def _parse_integer(value: str | None) -> int | None:
    """Parse a finite whole-number value; return None when it is invalid."""
    if value is None or not value.strip():
        return None
    try:
        number = Decimal(value.strip())
    except InvalidOperation:
        return None
    if not number.is_finite() or number != number.to_integral_value():
        return None
    try:
        return int(number)
    except (OverflowError, ValueError):
        return None


def _validate_header(header: list[str] | None, file_name: str) -> None:
    """Fail if the input header differs from the agreed column contract."""
    actual = tuple(header or ())
    if actual != EXPECTED_COLUMNS:
        missing = [column for column in EXPECTED_COLUMNS if column not in actual]
        unexpected = [column for column in actual if column not in EXPECTED_COLUMNS]
        raise ValueError(
            f"{file_name}: schema mismatch. Expected columns in this order: "
            f"{list(EXPECTED_COLUMNS)}; received: {list(actual)}. "
            f"Missing: {missing}; unexpected: {unexpected}."
        )


def _count_values(counter: Counter[str]) -> dict[str, int]:
    """Return a stable, JSON-compatible counter mapping."""
    return {str(key): int(value) for key, value in sorted(counter.items())}


def _process_file(
    input_path: Path,
    file_name: str,
    model_writer: csv.writer,
    metadata_writer: csv.writer,
    file_summary: dict[str, Any],
    total_summary: dict[str, Any],
    next_record_index: int,
) -> tuple[int, int]:
    """Validate, summarize and stream one CSV into temporary output files."""
    invalid_rows = 0
    try:
        with input_path.open("r", encoding="utf-8-sig", newline="") as input_file:
            reader = csv.DictReader(input_file)
            _validate_header(reader.fieldnames, file_name)
            for row in reader:
                file_summary["rows"] += 1
                total_summary["rows"] += 1
                issues: Counter[str] = Counter()
                if None in row:
                    issues["malformed_rows"] += 1

                for column, counter_name in (
                    ("label", "labels"),
                    ("category", "categories"),
                    ("specific_class", "specific_classes"),
                ):
                    value = row.get(column)
                    if value is not None and value.strip():
                        file_summary[counter_name][value] += 1
                        total_summary[counter_name][value] += 1

                missing_columns = [
                    column
                    for column in EXPECTED_COLUMNS
                    if row.get(column) is None or not row[column].strip()
                ]
                issues["missing_cells"] += len(missing_columns)

                numeric: dict[str, int | None] = {}
                for column in FEATURE_COLUMNS:
                    raw_value = row.get(column)
                    parsed = _parse_integer(raw_value)
                    numeric[column] = parsed
                    if raw_value is not None and raw_value.strip() and parsed is None:
                        issues["invalid_or_non_integer_numeric_cells"] += 1

                if numeric["ID"] is not None and numeric["ID"] < 0:
                    issues["invalid_id_cells"] += 1

                for column in BYTE_COLUMNS:
                    value = numeric[column]
                    if value is not None and not 0 <= value <= 255:
                        issues["out_of_range_byte_cells"] += 1

                label = row.get("label") or ""
                category = row.get("category") or ""
                specific_class = row.get("specific_class") or ""
                if label and label not in LABELS:
                    issues["unexpected_label_rows"] += 1
                if category and category not in CATEGORIES:
                    issues["unexpected_category_rows"] += 1
                if specific_class and specific_class not in SPECIFIC_CLASSES:
                    issues["unexpected_specific_class_rows"] += 1

                if label and category and specific_class:
                    if specific_class == "BENIGN":
                        hierarchy_valid = label == "BENIGN" and category == "BENIGN"
                    elif specific_class == "DoS":
                        hierarchy_valid = label == "ATTACK" and category == "DoS"
                    elif specific_class in {"GAS", "RPM", "SPEED", "STEERING_WHEEL"}:
                        hierarchy_valid = label == "ATTACK" and category == "SPOOFING"
                    else:
                        hierarchy_valid = False
                    if not hierarchy_valid:
                        issues["inconsistent_label_hierarchy_rows"] += 1

                numeric_invalid = any(value is None for value in numeric.values())
                range_invalid = any(
                    numeric[column] is not None and not 0 <= numeric[column] <= 255
                    for column in BYTE_COLUMNS
                )
                id_invalid = numeric["ID"] is not None and numeric["ID"] < 0
                labels_valid = (
                    label in LABELS
                    and category in CATEGORIES
                    and specific_class in SPECIFIC_CLASSES
                    and (
                        (specific_class == "BENIGN" and label == "BENIGN" and category == "BENIGN")
                        or (specific_class == "DoS" and label == "ATTACK" and category == "DoS")
                        or (
                            specific_class in {"GAS", "RPM", "SPEED", "STEERING_WHEEL"}
                            and label == "ATTACK"
                            and category == "SPOOFING"
                        )
                    )
                )
                is_invalid = bool(
                    missing_columns
                    or None in row
                    or numeric_invalid
                    or range_invalid
                    or id_invalid
                    or not labels_valid
                )
                file_summary["quality_issues"].update(issues)

                if is_invalid:
                    invalid_rows += 1
                    continue

                model_writer.writerow(
                    [numeric[column] for column in FEATURE_COLUMNS]
                    + [BINARY_MAP[label], CLASS_MAP[specific_class]]
                )
                metadata_writer.writerow(
                    [next_record_index, file_name, label, category, specific_class]
                )
                next_record_index += 1
    except (csv.Error, UnicodeDecodeError) as exc:
        raise ValueError(f"{file_name}: could not parse CSV ({exc})") from exc

    return invalid_rows, next_record_index


def analyse_and_export(input_dir: Path, output_dir: Path) -> dict[str, Any]:
    """Summarise the six data files and write checked ML-ready outputs.

    Args:
        input_dir: Folder containing the six decimal CSV inputs.
        output_dir: Folder for output CSV files and the JSON summary.

    Returns:
        A JSON-compatible summary dictionary.

    Raises:
        FileNotFoundError: If an expected input file is missing.
        ValueError: If a schema or data-quality issue is found.
    """
    input_dir = input_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    missing_files = [name for name in EXPECTED_FILES if not (input_dir / name).is_file()]
    if missing_files:
        raise FileNotFoundError(
            f"Missing expected dataset files in {input_dir}: {', '.join(missing_files)}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, Any] = {
        "dataset": "CICIoV2024 decimal CSV files",
        "input_directory": str(input_dir),
        "feature_columns": list(FEATURE_COLUMNS),
        "target_columns": ["target_binary", "target_class"],
        "class_mappings": {"binary": BINARY_MAP, "multiclass": CLASS_MAP},
        "duplicate_policy": "Repeated CAN messages are retained.",
        "files": {},
        "totals": {
            "rows": 0,
            "labels": Counter(),
            "categories": Counter(),
            "specific_classes": Counter(),
        },
    }
    total_invalid = 0

    # Use temporary outputs so a failed run never publishes partial datasets.
    with tempfile.TemporaryDirectory(prefix="analysis_output_", dir=output_dir) as temp_name:
        temp_dir = Path(temp_name)
        model_path = temp_dir / "ml_ready.csv"
        metadata_path = temp_dir / "metadata.csv"
        next_record_index = 0
        try:
            with model_path.open("w", encoding="utf-8", newline="") as model_file:
                with metadata_path.open("w", encoding="utf-8", newline="") as metadata_file:
                    model_writer = csv.writer(model_file)
                    metadata_writer = csv.writer(metadata_file)
                    model_writer.writerow(list(FEATURE_COLUMNS) + ["target_binary", "target_class"])
                    metadata_writer.writerow(
                        ["record_index", "source_file", "label", "category", "specific_class"]
                    )

                    for file_name in EXPECTED_FILES:
                        file_summary = _new_file_summary()
                        invalid_rows, next_record_index = _process_file(
                            input_dir / file_name,
                            file_name,
                            model_writer,
                            metadata_writer,
                            file_summary,
                            summary["totals"],
                            next_record_index,
                        )
                        total_invalid += invalid_rows
                        summary["files"][file_name] = {
                            "rows": int(file_summary["rows"]),
                            "valid_rows": int(file_summary["rows"] - invalid_rows),
                            "invalid_rows": int(invalid_rows),
                            "label_counts": _count_values(file_summary["labels"]),
                            "category_counts": _count_values(file_summary["categories"]),
                            "specific_class_counts": _count_values(file_summary["specific_classes"]),
                            "quality_issue_counts": _count_values(file_summary["quality_issues"]),
                        }
        except OSError as exc:
            raise ValueError(f"Could not read an input or write temporary output: {exc}") from exc

        if summary["totals"]["rows"] == 0:
            raise ValueError("The expected input files contained no records.")
        if total_invalid:
            details = "; ".join(
                f"{name}: {info['invalid_rows']} invalid row(s), "
                f"quality counts={info['quality_issue_counts']}"
                for name, info in summary["files"].items()
                if info["invalid_rows"]
            )
            raise ValueError(
                f"{total_invalid} invalid row(s) found. No final outputs were published. "
                f"Per-file details: {details}. Return these issues to the upstream "
                "validation/cleaning stage."
            )

        summary["totals"]["labels"] = _count_values(summary["totals"]["labels"])
        summary["totals"]["categories"] = _count_values(summary["totals"]["categories"])
        summary["totals"]["specific_classes"] = _count_values(
            summary["totals"]["specific_classes"]
        )
        summary["totals"]["valid_rows"] = int(summary["totals"]["rows"])
        summary["totals"]["invalid_rows"] = 0
        summary_path = temp_dir / "analysis_summary.json"
        summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

        for source in (model_path, metadata_path, summary_path):
            os.replace(source, output_dir / source.name)

    return summary


def _parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(
        description="Summarise CICIoV2024 CSVs and create checked ML-ready outputs."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing the six agreed decimal CSV files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where outputs will be written.",
    )
    return parser.parse_args()


def main() -> int:
    """Run analysis, save outputs, and print a concise result summary."""
    args = _parse_args()
    try:
        result = analyse_and_export(args.input_dir, args.output_dir)
    except (FileNotFoundError, ValueError) as exc:
        print(f"ANALYSIS/OUTPUT FAILED: {exc}")
        return 1

    print("ANALYSIS/OUTPUT COMPLETE")
    print(f"Total records: {result['totals']['rows']:,}")
    print(f"Label counts: {result['totals']['labels']}")
    print(f"Attack-category counts: {result['totals']['categories']}")
    print(f"Output folder: {args.output_dir.resolve()}")
    print("Created: ml_ready.csv, metadata.csv, analysis_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
