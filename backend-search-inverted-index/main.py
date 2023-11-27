import time
from fastapi import FastAPI
from inv_index_merger import InvIndexMerger
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from postgres import query_my_index

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
    language: str
    query: str
    k: int
    index: str

@app.post("/search/")
async def search(item : Item):
    language = item.language
    query = item.query
    k = item.k
    index = item.index

    print(item)

    if index == "myindex" :
        merger = InvIndexMerger(language)

        start_time = time.time()
        results = merger.search_query_merged_blocks(query, k)
        end_time = time.time()

        elapsed_time = end_time - start_time


        results = [
            {
                "track_id": open(f"./documents/doc{result[0]}.txt", 'r').readline()[:22],
                "similarity": result[1]
            } for result in results
        ]

        return {
            "code": 200,
            "results": results,
            "time": round(elapsed_time, 2)
        }
    else:
        [results, elapsed_time] = query_my_index(query, language, k)
        results = [
            {
                "track_id": track_id,
                "similarity": 0
            }
            for track_id in results
        ]

        return {
            "code": 200,
            "results": results,
            "time": round(elapsed_time, 2)
        }