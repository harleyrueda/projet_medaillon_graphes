#!/bin/bash
set -e
cd "$(dirname "$0")/.."

start_total=$(date +%s)

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

print("Fichiers CSV créés")
PYCODE


echo "En attente que Neo4j soit prêt"
until cypher-shell -a bolt://neo4j:7687 -u neo4j -p "" "RETURN 1" > /dev/null 2>&1; do
    echo "Neo4j n'est pas encore prêt"
    sleep 5
done
echo "Neo4j est prêt"

echo "Importation des données dans Neo4j"
cypher-shell -a bolt://neo4j:7687 -u neo4j -p "" <<'CYPHER'
MATCH (n) DETACH DELETE n;
CREATE INDEX node_id_index IF NOT EXISTS FOR (n:Node) ON (n.id);

CALL {
    LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
    WITH row
    CREATE (:Node {
        id: toInteger(row.`id:ID`),
        name: row.name,
        label: row.label
    })
} IN TRANSACTIONS OF 50 ROWS;

CALL {
    LOAD CSV WITH HEADERS FROM 'file:///edges.csv' AS row
    WITH row
    MATCH (src:Node {id: toInteger(row.`:START_ID`)}),
          (dst:Node {id: toInteger(row.`:END_ID`)})
    CREATE (src)-[:REL]->(dst)
} IN TRANSACTIONS OF 50 ROWS;
CYPHER

cypher-shell -a bolt://neo4j:7687 -u neo4j -p "" "MATCH (n:Node) RETURN count(n) AS nodes;"
cypher-shell -a bolt://neo4j:7687 -u neo4j -p "" "MATCH ()-[r:REL]->() RETURN count(r) AS relationships;"

end_total=$(date +%s)
echo "Importation terminee en $((end_total - start_total)) secondes."

