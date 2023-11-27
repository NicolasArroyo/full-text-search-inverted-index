import pandas as pd
import numpy as np

from faiss_index import create_faiss, get_faiss, faiss_knn_search

def prompt_yes_no(message: str) -> bool:
    return input(message).lower() == 'yes'

def read_collection(csv_file: str) -> dict[str, np.ndarray]:
    df = pd.read_csv(csv_file, header=None)

    collection = {row[0]: np.array(row[1:]) for row in df.itertuples(index=False)}

    return collection

def main():
    collection = read_collection('features_vectors.csv')
    vectors = np.array(list(collection.values()))
    track_ids = list(collection.keys())

    index = None
    if prompt_yes_no('Create indices? (yes/no): '):
        index = create_faiss(vectors)
    else:
        index = get_faiss()

    query_track_id = input('track_id of query: ')
    try:
        query_vector = collection[query_track_id]
    except:
        print("Aun no hemos indexado esa cancion.")
        return
    k = int(input('Top k: '))

    results = faiss_knn_search(index, query_vector, k, track_ids)
    print(results)

if __name__ == '__main__':
    main()
