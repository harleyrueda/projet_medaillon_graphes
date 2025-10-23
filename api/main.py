from fastapi import FastAPI, HTTPException, Body
from neo4j import GraphDatabase
import os

app = FastAPI()


# ---------------------------------------------------------------------------------

# ----------------GET /health : Santé de l'API-------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------POST /query/cypher : Exécuter une requête Cypher---------------------------


# --------------GET /entity/{id} : Récupérer un noeud et ses voisins------------------------
