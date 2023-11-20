import time

from inv_index_merger import InvIndexMerger

if __name__ == '__main__':
    # query = input('Query: ')
    # k = int(input('Top k: '))
    # language = str(input('Language abbreviation: '))

    query = "a"
    k = 3
    language = "it"

    merger = InvIndexMerger(language)

    start_time = time.time()
    results = merger.search_query_merged_blocks(query, k)
    end_time = time.time()

    elapsed_time = end_time - start_time

    print(f'Elapsed time: {elapsed_time} seconds')
    print(results)
