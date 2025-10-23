import argparse
import os
import pandas as pd


def convert_csv_to_parquet(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    df_nodes = pd.read_csv(
        f"{input_dir}/nodes.csv",
        dtype={"id": "int64", "label": "string", "name": "string"},
    )
    df_nodes.to_parquet(f"{output_dir}/nodes.parquet", index=False)
    print(f"{output_dir}/nodes.parquet")

    df_edges = pd.read_csv(
        f"{input_dir}/edges.csv",
        dtype={"src": "int64", "dst": "int64", "type": "string"},
    )
    df_edges.to_parquet(f"{output_dir}/edges.parquet", index=False)
    print(f"{output_dir}/edges.parquet")


def pipeline_bronze():
    parser = argparse.ArgumentParser(description="CSV conversion parquet")
    parser.add_argument("--in", dest="input_dir", required=True)
    parser.add_argument("--out", dest="output_dir", required=True)
    args = parser.parse_args()
    convert_csv_to_parquet(args.input_dir, args.output_dir)


if __name__ == "__main__":
    pipeline_bronze()
