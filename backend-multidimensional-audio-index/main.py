import time
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import numpy as np
from faiss_index import get_faiss, faiss_knn_search

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

class Item(BaseModel):
    trackid: str
    k: int

def read_collection(csv_file: str) -> dict[str, np.ndarray]:
    df = pd.read_csv(csv_file, header=None)

    collection = {row[0]: np.array(row[1:]) for row in df.itertuples(index=False)}

    return collection



@app.post("/search/")
async def search(item : Item):
    k = item.k
    trackid = item.trackid

    collection = read_collection('features_vectors.csv')
    track_ids = list(collection.keys())

    index = get_faiss()

    try:
        query_vector = collection[trackid]
    except:
        return {
            "code": 404,
            "message": "Song not found.",
            "results": [],
            "time": 0
        }

    init = time.time()
    results = faiss_knn_search(index, query_vector, k+1, track_ids)
    elapsed_time = time.time() - init

    results = [
        {
            "track_id": str(result[0]),
            "distance": round(float(result[1]), 3)
        } for result in results[1:]
    ]

    return {
        "code": 200,
        "message": "Query succesfull.",
        "results": results,
        "time": round(elapsed_time*1000, 2)
    }