import pandas as pd
import great_expectations as gx
import os
import sys
import argparse

# -----Verification qualité via Great Expectations--------------------------------
# -- (expect_column_values_to_be_unique, expect_column_values_to_not_be_null)------


def gx_quality_checks(input_dir):
    nodes = pd.read_parquet(os.path.join(input_dir, "nodes.parquet"))
    edges = pd.read_parquet(os.path.join(input_dir, "edges.parquet"))

    validator_nodes = gx.from_pandas(nodes)
    validator_nodes.expect_column_values_to_be_unique("id")
    result_nodes = validator_nodes.validate()

    validator_edges = gx.from_pandas(edges)
    validator_edges.expect_column_values_to_not_be_null("src")
    validator_edges.expect_column_values_to_not_be_null("dst")
    result_edges = validator_edges.validate()

    print("id unique:", result_nodes.success)
    print("src not null:", result_edges.results[0].success)
    print("dst not null:", result_edges.results[1].success)

    success = result_nodes.success and result_edges.success
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_dir", required=True)
    args = parser.parse_args()
    gx_quality_checks(args.input_dir)
