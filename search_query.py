from inv_index_divider_merger import InvIndexDividerMerger

if __name__ == '__main__':
    divider_merger = InvIndexDividerMerger()

    query = input('Query: ')
    k = int(input('Top k: '))
    results = divider_merger.search_query_automatic_blocks(query, k)
    print(results)