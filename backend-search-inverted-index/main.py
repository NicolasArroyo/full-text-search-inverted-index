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
            line = ', '.join(row[j] for j in [0, 1, 2, 3, 6, 8, 10, 11, -1])
            language = row[24]

            doc_name = f'documents/doc{i}.txt'
            docs_name.append(doc_name)
            with open(doc_name, 'w') as txt_file:
                txt_file.write(line)

    return docs_name


def create_index(docs: list) -> None:
    stemmer_map = ["ar", "da", "nl", "en", "fi", "fr", "de", "hu", "it", "no", "pt", "ro", "ru", "es", "sv", ]
    # stemmer_map = ["ar", "da", "nl", "fi", "fr", "de", "hu", "it", "no", "pt", "ro", "ru", "sv", ]

    for i in stemmer_map:
        print(i)
        index_i = InvIndex(i)
        index_i.index_docs(docs)


def main():
    stemmer_map = ["ar", "da", "nl", "en", "fi", "fr", "de", "hu", "it", "no", "pt", "ro", "ru", "es", "sv", ]

    docs = get_docs('spotify_songs.csv')
    create_index(docs)

    for i in stemmer_map:
        merger = InvIndexMerger(i)
        merger.merge_and_save_blocks()

    # query = input('query: ')
    # k = int(input('#docs más cercanos: '))
    # language = str(input('Language abbreviation: '))
    #
    # results = merger.search_query_merged_blocks(query, k, language)
    # print(results)


if __name__ == "__main__":
    main()
