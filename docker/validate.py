#!/usr/bin/env python3
"""Validate task 2 prediction file.

Prediction files require 2 columns:
    - Participant_ID
    - Disease_Name
"""
import argparse
import json
import pandas as pd
import numpy as np

INDEX_COL = "Participant_ID"
PRED_COL = "Disease_Name"


def get_args():
    """Set up command-line interface and get arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--predictions_file",
                        type=str, required=True)
    parser.add_argument("-g", "--goldstandard_file",
                        type=str, required=True)
    parser.add_argument("-o", "--output", type=str)
    return parser.parse_args()


def check_dups(pred):
    """Check for duplicate participant IDs i.e. confirm all IDs are unique."""
    duplicates = pred.duplicated(subset=[INDEX_COL])
    if duplicates.any():
        return (
            f"Found {duplicates.sum()} duplicate participant ID(s): "
            f"{pred[duplicates].Participant_ID.to_list()}"
        )
    return ""


def check_missing_ids(gold, pred):
    """Check for missing participant IDs."""
    pred = pred.set_index(INDEX_COL)
    missing_ids = gold.index.difference(pred.index)
    if missing_ids.any():
        return (
            f"Found {missing_ids.shape[0]} missing participant ID(s): "
            f"{missing_ids.to_list()}"
        )
    return ""


def check_unknown_ids(gold, pred):
    """Check for unknown participant IDs."""
    pred = pred.set_index(INDEX_COL)
    unknown_ids = pred.index.difference(gold.index)
    if unknown_ids.any():
        return (
            f"Found {unknown_ids.shape[0]} unknown participant ID(s): "
            f"{unknown_ids.to_list()}"
        )
    return ""


def validate(gold_file, pred_file):
    """Validate predictions file against goldstandard."""
    errors = []
    cols = {INDEX_COL: np.int64, PRED_COL: str}

    gold = pd.read_table(gold_file,
                         index_col=INDEX_COL)
    try:
        pred = pd.read_table(pred_file,
                             usecols=cols,
                             dtype=cols)
    except ValueError:
        errors.append(
            f"Invalid column names and/or types found. "
            f"Expecting: {str(cols)}."
        )
    else:
        errors.append(check_dups(pred))
        errors.append(check_missing_ids(gold, pred))
        errors.append(check_unknown_ids(gold, pred))
    return errors


def main():
    """Main function."""
    args = get_args()

    invalid_reasons = validate(
        gold_file=args.goldstandard_file,
        pred_file=args.predictions_file,
    )

    invalid_reasons = "\n".join(filter(None, invalid_reasons))
    status = "INVALID" if invalid_reasons else "VALIDATED"

    # truncate validation errors if >500 (character limit for sending email)
    if len(invalid_reasons) > 500:
        invalid_reasons = invalid_reasons[:496] + "..."
    res = json.dumps({
        "submission_status": status,
        "submission_errors": invalid_reasons
    })

    if args.output:
        with open(args.output, "w") as out:
            out.write(res)
    else:
        print(res)


if __name__ == "__main__":
    main()
