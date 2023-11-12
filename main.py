import math
import re
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
import json
import heapq


class InvIndexKey:
    def __init__(self, token):
        self.token = token
        self.idf = 0.0

    def __hash__(self) -> int:
        return hash(self.token)

    def __eq__(self, other) -> bool:
        if isinstance(other, InvIndexKey):
            return self.token == other.token
        elif isinstance(other, str):
            return self.token == other
        return False


class InvIndexVal:
    def __init__(self, doc_index, tf):
        self.doc_index = doc_index
        self.tf = tf
        self.tf_idf = 0.0


class InvIndex:
    def __init__(self):
        self.inverted_index = defaultdict(list)
        self.docs_counter = 0

    def index_docs(self, docs):
        stemmer = SnowballStemmer(language='spanish')
        self.docs_counter = self.docs_counter + len(docs)

        with open('stop_words_spanish.txt', encoding='utf-8') as file:
            stop_list = [line.rstrip().lower() for line in file]

        for doc_idx, doc in enumerate(docs):
            with open(doc, encoding="utf-8") as doc_file:
                doc_content = doc_file.read()
                self._process_content(doc_content, doc_idx, stemmer, stop_list)

        self._order_index_by_tokens()
        self._process_idf()

    def _process_content(self, content, doc_idx, stemmer, stop_list):
        doc_words = re.findall(r'\w+', content)

        for doc_word in doc_words:
            if doc_word in stop_list:
                continue

            token = stemmer.stem(doc_word)
            index_key = InvIndexKey(token)

            for value in self.inverted_index[index_key]:
                if value.doc_index == doc_idx:
                    value.tf += 1
                    break
            else:
                self.inverted_index[index_key].append(InvIndexVal(doc_idx, 1))

    def _order_index_by_tokens(self):
        self.inverted_index = dict(sorted(self.inverted_index.items(), key=lambda t: t[0].token))

    def _process_idf(self):
        for key in self.inverted_index:
            key.idf = math.log10(self.docs_counter / len(self.inverted_index[key]))

            for value in self.inverted_index[key]:
                value.tf_idf = key.idf * math.log10(1 + value.tf)

    def __str__(self):
        output = []

        for key, values in self.inverted_index.items():
            token_info = f"Token: {key.token} | idf: {round(key.idf, 3)}"
            output.append(token_info)

            for value in values:
                value_str = f"Doc: {value.doc_index}\t| tf: {value.tf}  \t| tf.idf: {round(value.tf_idf, 3):.3f}"
                output.append(value_str)

            output.append('')

        return "\n".join(output)


# Tamaño del bloque basado en el tamaño de página de Linux
PAGE_SIZE = 4096
BLOCK_SIZE = PAGE_SIZE


def divide_and_save_blocks(index, block_size, directory):
    """
    Divide un índice invertido en bloques y los guarda en 'directory'.
    """
    current_block = {}
    current_block_size = 0
    block_count = 0

    for token, postings in index.inverted_index.items():
        entry = json.dumps({token.token: [(val.doc_index, val.tf, val.tf_idf) for val in postings]})
        entry_size = len(entry.encode('utf-8'))

        if current_block_size + entry_size > block_size:
            with open(os.path.join(directory, f"block_{block_count}.json"), 'w', encoding='utf-8') as file:
                json.dump(current_block, file, ensure_ascii=False)
            block_count += 1
            current_block = {}
            current_block_size = 0

        current_block[token.token] = [(val.doc_index, val.tf, val.tf_idf) for val in postings]
        current_block_size += entry_size

    if current_block:
        with open(os.path.join(directory, f"block_{block_count}.json"), 'w', encoding='utf-8') as file:
            json.dump(current_block, file, ensure_ascii=False)

    return block_count + 1


def sequential_merge_blocks(num_blocks, directory):
    """
    Realiza una fusión secuencial de los bloques, cargando uno a la vez, para cumplir con las restricciones de memoria.
    """
    merged_index = defaultdict(list)

    for block_idx in range(num_blocks):
        with open(os.path.join(directory, f"block_{block_idx}.json"), 'r', encoding='utf-8') as file:
            block_data = json.load(file)
            for token, postings in block_data.items():
                merged_index[token].extend(postings)

    # Ordenar las listas de postings para cada token
    for token, postings in merged_index.items():
        merged_index[token] = sorted(postings, key=lambda x: x[0])  # Ordenar por índice de documento

    return merged_index


def reconstruct_index_from_blocks(num_blocks, directory):
    """
    Reconstruye el índice invertido a partir de los bloques almacenados en 'directory'.
    """
    reconstructed_index = defaultdict(list)

    for i in range(num_blocks):
        with open(os.path.join(directory, f"block_{i}.json"), 'r', encoding='utf-8') as file:
            block_data = json.load(file)
            for token, postings in block_data.items():
                reconstructed_index[token].extend(postings)

    return reconstructed_index


def print_reconstructed_index(reconstructed_index):
    """
    Imprime el índice reconstruido 'reconstructed_index' en el mismo formato que InvIndex.
    Calcula automáticamente el número total de documentos.
    """
    output = []

    # Calcular el número total de documentos
    num_docs = max(doc_index for postings in reconstructed_index.values() for doc_index, _, _ in postings) + 1

    for token, postings in reconstructed_index.items():
        idf = math.log10(num_docs / len(postings))
        token_info = f"Token: {token} | idf: {round(idf, 3)}"
        output.append(token_info)

        for doc_index, tf, tf_idf in postings:
            value_str = f"Doc: {doc_index}\t| tf: {tf}  \t| tf.idf: {round(tf_idf, 3):.3f}"
            output.append(value_str)

        output.append('')

    return "\n".join(output)


def process_query(query, stemmer, stop_list):
    """
    Procesa la consulta aplicando tokenización, stemming y eliminación de palabras vacías.
    """
    query_tokens = re.findall(r'\w+', query)
    processed_query = [stemmer.stem(word) for word in query_tokens if word not in stop_list]
    return processed_query


def calculate_similarity(block, query_vector, num_docs):
    """
    Calcula la similitud coseno entre la consulta y los documentos en un bloque.
    """
    doc_scores = defaultdict(float)
    for token, postings in block.items():
        if token in query_vector:
            for doc_index, tf, tf_idf in postings:
                doc_scores[doc_index] += query_vector[token] * tf_idf

    # Normalizar los puntajes de similitud
    for doc_index in doc_scores:
        doc_scores[doc_index] /= math.sqrt(num_docs)

    return doc_scores


def search_query_automatic_blocks(query, blocks_directory, stemmer, stop_list, n):
    """
    Realiza una búsqueda en los bloques del índice invertido sin necesidad de especificar el número de bloques.
    Devuelve los n documentos más relevantes.
    """
    processed_query = process_query(query, stemmer, stop_list)
    query_vector = {token: 1 for token in processed_query}  # Simplificación para la demostración

    all_doc_scores = defaultdict(float)

    # Determinar automáticamente el número de bloques
    block_files = [f for f in os.listdir(blocks_directory) if f.startswith("block_") and f.endswith(".json")]
    num_blocks = len(block_files)

    for block_idx in range(num_blocks):
        with open(os.path.join(blocks_directory, f"block_{block_idx}.json"), 'r', encoding='utf-8') as file:
            block = json.load(file)
            doc_scores = calculate_similarity(block, query_vector, num_blocks)
            for doc_index, score in doc_scores.items():
                all_doc_scores[doc_index] += score

    # Ordenar y seleccionar los top n documentos
    top_docs = sorted(all_doc_scores.items(), key=lambda x: x[1], reverse=True)[:n]

    # Formatear resultados para mostrar el porcentaje de similitud
    results = [(doc, f"{similarity * 100:.2f}%") for doc, similarity in top_docs]
    return results


# Directorio para guardar los bloques
blocks_directory = 'blocks'
os.makedirs(blocks_directory, exist_ok=True)

my_index = InvIndex()
my_index.index_docs(["libro1.txt", "libro2.txt", "libro3.txt", "libro4.txt", "libro5.txt", "libro6.txt"])

# Dividir y guardar los bloques
num_blocks = divide_and_save_blocks(my_index, BLOCK_SIZE, blocks_directory)

# Fusionar los bloques para reconstruir el índice invertido
merged_index = sequential_merge_blocks(num_blocks, blocks_directory)

# Reconstruir el índice invertido a partir de los bloques almacenados
reconstructed_index = reconstruct_index_from_blocks(num_blocks, blocks_directory)

reconstructed_index_str = print_reconstructed_index(reconstructed_index)

# Imprimir el índice reconstruido
# print(reconstructed_index_str)
# print('######################################################')
# print(my_index)

stemmer = SnowballStemmer(language='spanish')
stop_list = 'stop_words_spanish.txt'
query = "Tras la huida de Frodo y Sam en Parth Galen, Boromir muere a manos de los Uruk-hai"
n = 3
results = search_query_automatic_blocks(query, blocks_directory, stemmer, stop_list, n)

print(results)
