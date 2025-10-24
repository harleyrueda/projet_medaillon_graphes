from fastapi import FastAPI, HTTPException, Body
from neo4j import GraphDatabase
import os

app = FastAPI()

uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
user = os.getenv("NEO4J_USER", "neo4j")
password = os.getenv("NEO4J_PASSWORD", "")

driver = GraphDatabase.driver(uri, auth=(user, password))


# ---------------------------------------------------------------------------------

# ----------------GET /health : Santé de l'API-------------------------------------------


@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------POST /query/cypher : Exécuter une requête Cypher---------------------------


@app.post("/query/cypher")
def run_cypher(payload: dict = Body(...)):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="absence de champ 'query'.")
    try:
        with driver.session() as session:
            result = session.run(query)
            data = [record.data() for record in result]
        return {"result": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --------------GET /entity/{id} : Récupérer un noeud et ses voisins------------------------


@app.get("/entity/{node_id}")
def get_entity(node_id: int):
    query = """
    MATCH (n:Node {id: $id})
    OPTIONAL MATCH (n)-[r]->(m)
    RETURN n AS node, collect({rel: type(r), target: m.id}) AS neighbors
    """
    with driver.session() as session:
        result = session.run(query, id=node_id)
        record = result.single()
        if not record or not record["node"]:
            raise HTTPException(status_code=404, detail=f"Node {node_id} pas trouve.")
        node = dict(record["node"])
        neighbors = [n for n in record["neighbors"] if n["target"] is not None]
        return {"node": node, "neighbors": neighbors}
