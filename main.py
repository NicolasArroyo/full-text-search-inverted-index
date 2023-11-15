from inv_index import InvIndex
from inv_index_divider_merger import InvIndexDividerMerger

def main():
    index = InvIndex()
    index.index_docs(["libro1.txt", "libro2.txt", "libro3.txt", "libro4.txt", "libro5.txt", "libro6.txt"])

    divider_merger = InvIndexDividerMerger(index)
    divider_merger.divide_and_save_blocks()
    divider_merger.merge_and_save_blocks()

    # query = input('query: ')
    query = "En Rohan, Théoden reúne a lanzó al ataque, justo en el momento en el que el Rey Brujo penetraba en Minas Tirith."
    # k = int(input('#docs más cercanos: '))
    k = 3


    results = divider_merger.search_query_merged_blocks(query, k)

    print(results)

if __name__ == "__main__":
    main()