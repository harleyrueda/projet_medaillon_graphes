import argparse
import sys
import pandas as pd


def run_quality(input_dir):
    df_nodes = pd.read_parquet(f"{input_dir}/nodes.parquet", columns=["id"])
    df_edges = pd.read_parquet(f"{input_dir}/edges.parquet", columns=["src", "dst"])

    nodes_id_unique = df_nodes["id"].is_unique
    src_nulls = df_edges["src"].isna().sum()
    dst_nulls = df_edges["dst"].isna().sum()

    print(f"nodes_id_unique={nodes_id_unique}")
    print(f"src_nulls={src_nulls}")
    print(f"dst_nulls={dst_nulls}")

    ok = nodes_id_unique and src_nulls == 0 and dst_nulls == 0
    sys.exit(0 if ok else 1)


def quality_checks():
    parser = argparse.ArgumentParser(description="Quality checks for Bronze layer")
    parser.add_argument("--in", dest="input_dir", required=True)
    args = parser.parse_args()
    run_quality(args.input_dir)


if __name__ == "__main__":
    quality_checks()
