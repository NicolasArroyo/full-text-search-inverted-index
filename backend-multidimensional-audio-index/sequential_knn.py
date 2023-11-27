import heapq
import numpy as np
from numpy import ndarray

def euclidean_distance(v: ndarray, u: ndarray):
    return np.sqrt(sum((v - u) ** 2))

def sequential_knn_search(collection: ndarray, Q: ndarray, k: int):
    heap = []

    for i, c_i in enumerate(collection):
        dist = euclidean_distance(c_i, Q)

        if len(heap) < k:
            heapq.heappush(heap, (-dist, i))
        else:
            if dist < -heap[0][0]:
                heapq.heappop(heap)
                heapq.heappush(heap, (-dist, i))

    result = sorted([(i, -dist) for dist, i in heap], key=lambda x: x[1])

    print(result)

def sequential_range_search(collection: ndarray, Q: ndarray, r: float):
    result = []

    for i, c_i in enumerate(collection):
        dist = euclidean_distance(c_i, Q)
        if dist < r:
            result.append((i, dist))

    result = sorted(result, key=lambda x: x[0])

    print(result)

def calculate_percentile_radius(collection: ndarray, Q: ndarray, percentile: float):
    distances = [euclidean_distance(c_i, Q) for c_i in collection]

    r = np.percentile(distances, percentile)

    return float(r)