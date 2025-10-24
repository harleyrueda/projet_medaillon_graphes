import argparse
import os
import shutil
import pandas as pd


# ------------------------ fonction partition des edges en shards - vers Silver--------


def partition_to_silver(input_dir, output_dir, partitions):
    os.makedirs(output_dir, exist_ok=True)
    shutil.copyfile(f"{input_dir}/nodes.parquet", f"{output_dir}/nodes.parquet")
    edges = pd.read_parquet(
        f"{input_dir}/edges.parquet", columns=["src", "dst", "type"]
    )
    edges["shard"] = edges["src"] % partitions
    for i in range(partitions):
        shard_dir = f"{output_dir}/shard={i}"
        os.makedirs(shard_dir, exist_ok=True)
        edges.loc[edges["shard"] == i, ["src", "dst", "type"]].to_parquet(
            f"{shard_dir}/edges.parquet", index=False
        )


# ----------------------- point d'entree via argparse ---------------------------------


def partition_edges_main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="input_dir", required=True)
    ap.add_argument("--out", dest="output_dir", required=True)
    ap.add_argument("--partitions", type=int, default=8)
    args = ap.parse_args()
    partition_to_silver(args.input_dir, args.output_dir, args.partitions)


if __name__ == "__main__":
    partition_edges_main()
