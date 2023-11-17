import time

from inv_index_merger import InvIndexMerger

if __name__ == '__main__':
    divider_merger = InvIndexMerger()

    query = input('Query: ')
    k = int(input('Top k: '))
    language = str(input('Language abbreviation: '))

    start_time = time.time()
    results = divider_merger.search_query_merged_blocks(query, k, language)
    end_time = time.time()

    elapsed_time = end_time - start_time

    print(f'Elapsed time: {elapsed_time} seconds')
    print(results)