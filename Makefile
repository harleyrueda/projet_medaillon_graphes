.PHONY: up down seed bronze silver gold e2e quality

# -------------------------- Docker ---------------------------------------------------------
up:
	docker compose up -d

down:
	docker compose down -v

# --------------------- 1) Génération de données synthétiques --------------------------------------
seed:
	python3 scripts/generate_sample_data.py --out data/raw --nodes 100000 --edges 500000

# --------------------  2) BRONZE CSV -> Parquet  --------------------------------------------------
bronze:
	python3 scripts/to_parquet.py --in data/raw --out data/bronze

# --------------------  3) SILVER Validation qualité + Partitionnement des edges  ------------------
silver:
	# Validation Qualité
	python3 quality/gx_checkpoint.py --in data/bronze
	# Partitionnement des edges
	python3 scripts/partition_edges.py --in data/bronze --out data/silver --partitions 8

# --------------------  4) GOLD Import dans Neo4j  -------------------------------------------------
gold:
	bash scripts/neo4j_bulk_import.sh
	

# --- End to End ---
e2e: seed bronze silver gold
