from numpy import ndarray

from collection_features import create_features_vector_file, read_collection
from sequential_knn import sequential_knn_search, sequential_range_search, calculate_percentile_radius
from rtree_index import create_rtree, get_rtree, rtree_knn_search
from faiss_index import create_faiss, get_faiss, faiss_knn_search

def prompt_yes_no(message: str):
    return input(message).lower() == 'yes'

def build_index(choosed_index: str, collection: ndarray):
    if choosed_index == 'rtree':
        return create_rtree(collection)
    elif choosed_index == 'faiss':
        return create_faiss(collection)
    return None

def get_index(choosed_index: str, dimension: int):
    if choosed_index == 'rtree':
        return get_rtree(dimension)
    elif choosed_index == 'faiss':
        return get_faiss(dimension)
    return None

def conduct_search(choosed_index: str, collection: ndarray, index, query: ndarray, k: int):
    if choosed_index == 'seq':
        conduct_sequential_search(collection, query, k)
    elif choosed_index == 'rtree':
        rtree_knn_search(index, query, k)
    elif choosed_index == 'faiss':
        faiss_knn_search(index, query, k)

def conduct_sequential_search(collection: ndarray, query: ndarray, k: int):
    r1 = calculate_percentile_radius(collection, query, 0.1)
    r2 = calculate_percentile_radius(collection, query, 0.5)
    r3 = calculate_percentile_radius(collection, query, 1)

    print()
    print('Sequential KNN search: ')
    sequential_knn_search(collection, query, k)
    print()
    print('Sequential range r1 search: ')
    sequential_range_search(collection, query, r1)
    print()
    print('Sequential range r2 search: ')
    sequential_range_search(collection, query, r2)
    print()
    print('Sequential range r3 search: ')
    sequential_range_search(collection, query, r3)

def main():
    # if prompt_yes_no('Create features vector file? (yes/no): '):
    #     create_features_vector_file()

    collection = read_collection('features_vectors.csv')

    choosed_index = input('Which search you want to use (seq, rtree, faiss): ')

    index = None
    if prompt_yes_no('Create indices? (yes/no): '):
        index = build_index(choosed_index, collection)
    else:
        index = get_index(choosed_index, collection.shape[1])

    query_i = int(input('# of query (collection i): '))
    query = collection[query_i]
    k = int(input('Top k: '))

    conduct_search(choosed_index, collection, index, query, k)

if __name__ == '__main__':
    main()
