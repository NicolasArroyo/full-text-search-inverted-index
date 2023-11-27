import os
from rtree import index as rtree_index
from numpy import ndarray

def create_rtree(collection: ndarray) -> rtree_index.Index:
    if os.path.exists('rtree_index.dat'):
        os.remove('rtree_index.dat')
    if os.path.exists('rtree_index.idx'):
        os.remove('rtree_index.idx')

    prop = rtree_index.Property()
    prop.dimension = collection.shape[1]
    index = rtree_index.Index('rtree_index', properties=prop, interleaved=False)

    for i, feature_vector in enumerate(collection):
        index.insert(i, feature_vector)

    return index

def get_rtree(dimension: int) -> rtree_index.Index:
    prop = rtree_index.Property()
    prop.dimension = dimension
    return rtree_index.Index('rtree_index', properties=prop, interleaved=False)

def rtree_knn_search(index: rtree_index.Index, query: ndarray, k: int):
    result = list(index.nearest(query, num_results=k))
    index.close()

    print(result)
