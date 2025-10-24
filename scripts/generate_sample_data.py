import argparse
import os
import csv
import random
from tqdm import tqdm

# ------------- géneration de noeuds synthetiques (nodes.csv) ------------------------


def generate_nodes(path, count):
    labels = ["Person", "Org", "Paper"]
    with open(os.path.join(path, "nodes.csv"), mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "label", "name"])
        for i in tqdm(range(count), desc="Generation des nodes"):
            label = random.choice(labels)
            name = f"{label.lower()}_{i}"
            writer.writerow([i, label, name])


# ------------- géneration des relations synthetiques (edges.csv) ------------------------


def generate_edges(path, count, max_node_id):
    with open(os.path.join(path, "edges.csv"), mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["src", "dst", "type"])
        for i in tqdm(range(count), desc="Generation des edges"):
            src = random.randint(0, max_node_id - 1)
            dst = random.randint(0, max_node_id - 1)
            writer.writerow([src, dst, "REL"])


# ----------------------- point d'entree via argparse - generation (graphs) graphes syntetiques ---------------------------------


def generate_synthetic_graph():
    parser = argparse.ArgumentParser(description="Generation donnees synthetiques")
    parser.add_argument(
        "--out", required=True, help="Output directory (e.g., data/raw)"
    )
    parser.add_argument(
        "--nodes", type=int, default=1_000_000, help=" nodes a generer "
    )
    parser.add_argument("--edges", type=int, default=5_000_000, help=" edges a generer")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)
    generate_nodes(args.out, args.nodes)
    generate_edges(args.out, args.edges, args.nodes)


if __name__ == "__main__":
    generate_synthetic_graph()
