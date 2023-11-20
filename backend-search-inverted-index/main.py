import os
import csv

from inv_index import InvIndex
from inv_index_merger import InvIndexMerger

def get_docs(file_name: str) -> list:
    os.makedirs('documents', exist_ok=True)

    docs_name = []
    with open(file_name, 'r') as file:
            reader = csv.reader(file)
            next(reader)

            for i, row in enumerate(reader, start=0):
                line = ', '.join(row[j] for j in [1, 2, 3, 6, 8, 10, 11, -1])
                language = row[24]

                doc_name = f'documents/doc{i}.txt'
                docs_name.append(doc_name)
                with open(doc_name, 'w') as txt_file:
                     txt_file.write(line)

    return docs_name

def create_index(docs: list) -> None:
    index = InvIndex()
    index.index_docs(docs)

def main():
    docs = get_docs('spotify_songs.csv')
    create_index(docs)

    merger = InvIndexMerger()
    merger.merge_and_save_blocks()

    query = input('query: ')
    k = int(input('#docs más cercanos: '))
    language = str(input('Language abbreviation: '))

    results = merger.search_query_merged_blocks(query, k, language)
    print(results)

if __name__ == "__main__":
    main()