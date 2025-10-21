#!/bin/bash
set -e
cd "$(dirname "$0")/.."

INPUT_DIR=${1:-data/silver}
OUTPUT_DIR=${2:-data/gold}

mkdir -p "$OUTPUT_DIR"

python3 - <<PYCODE
import pandas as pd
import os
import glob

input_dir = os.path.abspath("${INPUT_DIR}")
output_dir = os.path.abspath("${OUTPUT_DIR}")

os.makedirs(output_dir, exist_ok=True)
print(f"Reading from: {input_dir}")
print(f"Writing to: {output_dir}")

nodes = pd.read_parquet(os.path.join(input_dir, "nodes.parquet"))
nodes.rename(columns={"id": "id:ID"}, inplace=True)
nodes.to_csv(os.path.join(output_dir, "nodes.csv"), index=False)

edges_files = glob.glob(os.path.join(input_dir, "shard=*/edges.parquet"))
edges = pd.concat([pd.read_parquet(f) for f in edges_files])
edges.rename(columns={"src": ":START_ID", "dst": ":END_ID"}, inplace=True)
edges.to_csv(os.path.join(output_dir, "edges.csv"), index=False)

print("CSV files created successfully.")
PYCODE

docker compose up -d neo4j
sleep 20

echo "Esperando a que Neo4j esté listo..."
until docker exec neo4j cypher-shell "RETURN 1" > /dev/null 2>&1; do
    echo "Neo4j no está listo, esperando..."
    sleep 5
done
echo "Neo4j está listo!"

docker exec -i neo4j cypher-shell <<'CYPHER'
MATCH (n) DETACH DELETE n;
CREATE INDEX node_id_index IF NOT EXISTS FOR (n:Node) ON (n.id);

USING PERIODIC COMMIT 100
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
CREATE (:Node {id: toInteger(row.`id:ID`), name: row.name, label: row.label});

USING PERIODIC COMMIT 100
LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
MATCH (src:Node {id: toInteger(row.`:START_ID`)}),
      (dst:Node {id: toInteger(row.`:END_ID`)})
CREATE (src)-[:REL]->(dst);
CYPHER
