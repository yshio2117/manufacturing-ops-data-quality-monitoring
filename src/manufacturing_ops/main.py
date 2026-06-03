import csv
from pathlib import Path
import argparse
from src.reason_extraction.pipeline.record_pipeline import run_pipeline


def validate_input_file(path_str):

    path = Path(path_str)

    # check file extension
    if path.suffix.lower() != ".csv":
        raise argparse.ArgumentTypeError(
            "Input file must be a .csv file."
        )

    # check if file exists
    if not path.exists():
        raise argparse.ArgumentTypeError(
            "Input file does not exist."
        )

    # check if it's a file
    if not path.is_file():
        raise argparse.ArgumentTypeError(
            "Input path is not a file."
        )

    return path 

    
def parse_args():

    parser = argparse.ArgumentParser()
    # review file name
    parser.add_argument(
        "--input-file", 
        required=True,
        type=validate_input_file,
        help="Input CSV file (required)"
    )
    # where to output (validated reviews & negative reasons)
    parser.add_argument(
        "--output",
        choices=["bigquery", "local"],
        default="bigquery",
        help="Output destination (default: bigquery)"
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Optional run ID for tracking (default: auto-generated)"
    )

    return parser.parse_args()


def main():
    args = parse_args()
    run_pipeline(args)


if __name__=='__main__':
    
    main()