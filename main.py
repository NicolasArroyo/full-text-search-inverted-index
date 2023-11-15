import os
import csv

from inv_index import InvIndex
from inv_index_divider_merger import InvIndexDividerMerger

def get_docs(file_name: str) -> list:
    os.makedirs('documents', exist_ok=True)

    docs_name = []
    with open(file_name, 'r') as file:
            reader = csv.reader(file)
            next(reader)

            for i, row in enumerate(reader, start=0):
                line = ', '.join(row[j] for j in [1, 2, 3, 6, 8, 10, 11])
                language = row[24]

                doc_name = f'documents/doc{i}.txt'
                docs_name.append(doc_name)
                with open(doc_name, 'w') as txt_file:
                     txt_file.write(line)

    return docs_name

def create_index(docs: list) -> InvIndex:
    index = InvIndex()
    index.index_docs(docs)

    return index

def main():
    docs = get_docs('spotify_songs.csv')
    index = create_index(docs)

    divider_merger = InvIndexDividerMerger(index)
    divider_merger.divide_and_save_blocks()
    divider_merger.merge_and_save_blocks()

    query = input('query: ')
    # query = "En Rohan, Théoden reúne a lanzó al ataque, justo en el momento en el que el Rey Brujo penetraba en Minas Tirith."
    k = int(input('#docs más cercanos: '))
    # k = 3


    results = divider_merger.search_query_merged_blocks(query, k)
    print(results)

if __name__ == "__main__":
    main()