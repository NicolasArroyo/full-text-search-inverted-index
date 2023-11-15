import math
import re
import os
import json

from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer

from inv_index import InvIndex

class InvIndexDividerMerger:
    PAGE_SIZE = 4096
    BLOCK_SIZE = PAGE_SIZE

    stop_list = 'stop_words_spanish.txt'

    initial_blocks_dir = 'initial_blocks'
    final_blocks_dir = 'final_blocks'

    def __init__(self, inv_index: InvIndex):
        self.index = inv_index
        self.stemmer = SnowballStemmer(language='spanish')

        os.makedirs(self.initial_blocks_dir, exist_ok=True)
        os.makedirs(self.final_blocks_dir, exist_ok=True)

    def divide_and_save_blocks(self):
        """
        Divide un índice invertido en bloques y los guarda en 'directory'.
        """

        current_block = {}
        current_block_size = 0
        block_count = 0

        for token, postings in self.index.inverted_index.items():
            entry = json.dumps({token.token: [(val.doc_index, val.tf, val.tf_idf) for val in postings]})
            entry_size = len(entry.encode('utf-8'))

            if current_block_size + entry_size > self.BLOCK_SIZE:
                with open(os.path.join(self.initial_blocks_dir, f"block_{block_count}.json"), 'w', encoding='utf-8') as file:
                    json.dump(current_block, file, ensure_ascii=False)
                block_count += 1
                current_block = {}
                current_block_size = 0

            current_block[token.token] = [(val.doc_index, val.tf, val.tf_idf) for val in postings]
            current_block_size += entry_size

        if current_block:
            with open(os.path.join(self.initial_blocks_dir, f"block_{block_count}.json"), 'w', encoding='utf-8') as file:
                json.dump(current_block, file, ensure_ascii=False)

        return block_count + 1

    def merge_and_save_blocks(self):
        """
        Fusiona los bloques en 'input_directory' y guarda los bloques fusionados en 'output_directory'.
        """

        block_files = [f for f in os.listdir(self.initial_blocks_dir) if f.startswith("block_") and f.endswith(".json")]
        merged_blocks = defaultdict(list)
        current_block_size = 0
        current_block_count = 0

        for block_file in block_files:
            with open(os.path.join(self.initial_blocks_dir, block_file), 'r', encoding='utf-8') as file:
                block = json.load(file)
                for token, postings in block.items():
                    entry = json.dumps({token: postings})
                    entry_size = len(entry.encode('utf-8'))
                    if current_block_size + entry_size > self.BLOCK_SIZE:
                        # Guardar el bloque actual y empezar uno nuevo
                        with open(os.path.join(self.final_blocks_dir, f"merged_block_{current_block_count}.json"), 'w',
                                encoding='utf-8') as out_file:
                            json.dump(merged_blocks, out_file, ensure_ascii=False)
                        current_block_count += 1
                        merged_blocks = defaultdict(list)
                        current_block_size = 0
                    merged_blocks[token].extend(postings)
                    current_block_size += entry_size

        # Guardar el último bloque si contiene datos
        if merged_blocks:
            with open(os.path.join(self.final_blocks_dir, f"merged_block_{current_block_count}.json"), 'w',
                    encoding='utf-8') as out_file:
                json.dump(merged_blocks, out_file, ensure_ascii=False)

    def reconstruct_index_from_blocks(self, num_blocks, directory):
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

    def print_reconstructed_index(self, reconstructed_index):
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

    def process_query(self, query):
        """
        Procesa la consulta aplicando tokenización, stemming y eliminación de palabras vacías.
        """
        query_tokens = re.findall(r'\w+', query)
        processed_query = [self.stemmer.stem(word) for word in query_tokens if word not in self.stop_list]
        return processed_query
    
    def calculate_similarity(self, block, query_vector, num_docs):
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
    
    def search_query_automatic_blocks(self, query, n):
        """
        Realiza una búsqueda en los bloques del índice invertido sin necesidad de especificar el número de bloques.
        Devuelve los n documentos más relevantes.
        """
        processed_query = self.process_query(query)
        query_vector = {token: 1 for token in processed_query}  # Simplificación para la demostración

        all_doc_scores = defaultdict(float)

        # Determinar automáticamente el número de bloques
        block_files = [f for f in os.listdir(self.initial_blocks_dir) if f.startswith("block_") and f.endswith(".json")]
        num_blocks = len(block_files)

        for block_idx in range(num_blocks):
            with open(os.path.join(self.initial_blocks_dir, f"block_{block_idx}.json"), 'r', encoding='utf-8') as file:
                block = json.load(file)
                doc_scores = self.calculate_similarity(block, query_vector, num_blocks)
                for doc_index, score in doc_scores.items():
                    all_doc_scores[doc_index] += score

        # Ordenar y seleccionar los top n documentos
        top_docs = sorted(all_doc_scores.items(), key=lambda x: x[1], reverse=True)[:n]

        # Formatear resultados para mostrar el porcentaje de similitud
        results = [(doc, f"{similarity * 100:.2f}%") for doc, similarity in top_docs]
        return results
    
    def search_query_merged_blocks(self, query, k):
        """
        Realiza una búsqueda en los bloques fusionados del índice invertido almacenados en 'merged_blocks_directory'.
        Devuelve los n documentos más relevantes para la consulta.
        """

        processed_query = self.process_query(query)
        query_vector = {token: 1 for token in processed_query}  # Simplificación para la demostración

        all_doc_scores = defaultdict(float)

        # Determinar automáticamente el número de bloques fusionados
        merged_block_files = [f for f in os.listdir(self.final_blocks_dir) if
                            f.startswith("merged_block_") and f.endswith(".json")]

        for block_file in merged_block_files:
            with open(os.path.join(self.final_blocks_dir, block_file), 'r', encoding='utf-8') as file:
                block = json.load(file)
                doc_scores = self.calculate_similarity(block, query_vector, len(merged_block_files))
                for doc_index, score in doc_scores.items():
                    all_doc_scores[doc_index] += score

        # Ordenar y seleccionar los top n documentos
        top_docs = sorted(all_doc_scores.items(), key=lambda x: x[1], reverse=True)[:k]

        # Formatear resultados para mostrar el porcentaje de similitud
        results = [(doc, f"{similarity * 100:.2f}") for doc, similarity in top_docs]
        return results