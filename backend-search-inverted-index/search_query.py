import time

from inv_index_merger import InvIndexMerger

if __name__ == '__main__':
    # query = input('Query: ')
    # k = int(input('Top k: '))
    # language = str(input('Language abbreviation: '))

    query = "Good Kid"
    k = 5
    language = "en"

    merger = InvIndexMerger(language)

    start_time = time.time()
    results = merger.search_query_merged_blocks(query, k)
    end_time = time.time()

    elapsed_time = end_time - start_time

    print(f'Elapsed time: {elapsed_time} seconds')
    
    for result in results:
        path = f"./documents/doc{result[0]}.txt"
        print(open(path, 'r').readline()[:22])

