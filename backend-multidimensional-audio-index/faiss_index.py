import os
import faiss
import numpy as np

def create_faiss(vectors: np.ndarray) -> faiss.IndexIVFFlat:
    if os.path.exists('faiss_index'):
        os.remove('faiss_index')

    dimension = vectors.shape[1]
    nlist = 50
    quantizer = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIVFFlat(quantizer, dimension, nlist)

    index.train(vectors)
    index.add(vectors)

    faiss.write_index(index, 'faiss_index')

    return index

def get_faiss() -> faiss.IndexIVFFlat:
    return faiss.read_index('faiss_index')

def faiss_knn_search(index: faiss.IndexIVFFlat, query: np.ndarray, k: int, track_ids: list) -> list[tuple[str, float]]:
    if len(query.shape) == 1:
        query = query.reshape(1, -1)

    index.nprobe = 8  # Number of nearest cells to search

    D, I = index.search(query, k)

    results = [(track_ids[i], D[0][j]) for j, i in enumerate(I[0])]
    results.sort(key=lambda x: x[1])

    return results
