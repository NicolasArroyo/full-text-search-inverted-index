import time

from inv_index_divider_merger import InvIndexMerger

if __name__ == '__main__':
    divider_merger = InvIndexMerger()

    query = input('Query: ')
    k = int(input('Top k: '))

    start_time = time.time()
    results = divider_merger.search_query_automatic_blocks(query, k)
    end_time = time.time()

    elapsed_time = end_time - start_time

    print(f'Elapsed time: {elapsed_time} seconds')
    print(results)