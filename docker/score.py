#!/usr/bin/env python3
"""Score task 2 prediction file.

Task 2 will return accuracy as its only metric.
"""
import argparse
import json
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score

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


def score(gold, pred):
    """
    Calculate exact accuracy.
    """
    # Combine together to ensure Participant IDs are listed in same
    # order between goldstandard and prediction.
    res = gold.join(
        pred.set_index(INDEX_COL),
        lsuffix="_gold",
        rsuffix="_pred"
    )
    return {'accuracy': accuracy_score(
        res['Disease_Name_gold'],
        res['Disease_Name_pred'])
    }


def main():
    """Main function."""
    args = get_args()
    cols = {INDEX_COL: np.int64, PRED_COL: str}

    gold = pd.read_table(args.goldstandard_file,
                         index_col=INDEX_COL)
    pred = pd.read_table(args.predictions_file,
                         usecols=cols)
    scores = score(gold, pred)

    if args.output:
        with open(args.output, "w") as out:
            res = {
                "submission_status": "SCORED",
                **scores
            }
            out.write(json.dumps(res))
    else:
        print(scores)


if __name__ == "__main__":
    main()
