import argparse
import pandas as pd
import great_expectations as gx
from great_expectations.core.batch import RuntimeBatchRequest
import sys
import os


def run_quality_check(input_dir):
    nodes = pd.read_parquet(os.path.join(input_dir, "nodes.parquet"))
    edges = pd.read_parquet(os.path.join(input_dir, "edges.parquet"))

    context = gx.get_context()

    try:
        context.add_datasource(
            name="pandas_datasource",
            class_name="Datasource",
            execution_engine={"class_name": "PandasExecutionEngine"},
            data_connectors={
                "default_runtime_data_connector_name": {
                    "class_name": "RuntimeDataConnector",
                    "batch_identifiers": ["default_identifier_name"],
                }
            },
        )
    except:
        pass

    try:
        context.create_expectation_suite("nodes_suite")
    except:
        pass

    try:
        context.create_expectation_suite("edges_suite")
    except:
        pass

    batch_request_nodes = RuntimeBatchRequest(
        datasource_name="pandas_datasource",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="nodes_asset",
        runtime_parameters={"batch_data": nodes},
        batch_identifiers={"default_identifier_name": "nodes_batch"},
    )

    batch_request_edges = RuntimeBatchRequest(
        datasource_name="pandas_datasource",
        data_connector_name="default_runtime_data_connector_name",
        data_asset_name="edges_asset",
        runtime_parameters={"batch_data": edges},
        batch_identifiers={"default_identifier_name": "edges_batch"},
    )

    validator_nodes = context.get_validator(
        batch_request=batch_request_nodes,
        expectation_suite_name="nodes_suite",
    )
    validator_nodes.expect_column_values_to_be_unique("id")
    validator_nodes.save_expectation_suite()

    validator_edges = context.get_validator(
        batch_request=batch_request_edges,
        expectation_suite_name="edges_suite",
    )
    validator_edges.expect_column_values_to_not_be_null("src")
    validator_edges.expect_column_values_to_not_be_null("dst")
    validator_edges.save_expectation_suite()

    result_nodes = validator_nodes.validate()
    result_edges = validator_edges.validate()

    success = result_nodes.success and result_edges.success
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="input_dir", required=True)
    args = parser.parse_args()
    run_quality_check(args.input_dir)
