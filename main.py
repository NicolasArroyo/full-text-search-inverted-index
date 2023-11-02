import math
import re
import sys
import os
import pickle
from collections import defaultdict, namedtuple
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from heapq import heapify, heappush, heappop

PAGE_SIZE = 4096  # Tamaño de página en bytes


class InvIndexKey:
    """
    Represents scores based only on terms.
    Each InvertedIndexKey stores a tokenized term and its inverse doc frequency (IDF).
    """

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
    """
    Represents scores based on terms and docs at the same time.
    Each InvertedIndexValue stores a specific doc index and the term frequency (TF) of all term in that doc.
    Also stores the tf.idf score, but it is only later calculated.
    """

    def __init__(self, doc_index, tf):
        self.doc_index = doc_index
        self.tf = tf
        self.tf_idf = 0.0


class InvIndex:
    """
    Uses both classes, InvIndexKey and InvIndexVal.
    Might be seen as a table with the keys (terms) as the rows and the vals (docs) as the cols.
    First process all scores based both on terms and docs, then the ones based only on terms.
    """

    def __init__(self):
        self.inverted_index = defaultdict(list)
        self.docs_counter = 0
        self.block_counter = 0

    def index_docs(self, docs):
        stemmer = SnowballStemmer(language='spanish')
        self.docs_counter += len(docs)

        with open('stop_words_spanish.txt', encoding='utf-8') as file:
            stop_list = [line.rstrip().lower() for line in file]

        for doc_idx, doc in enumerate(docs):
            with open(doc, encoding="utf-8") as doc_file:
                doc_content = doc_file.read()
                self._process_content(doc_content, doc_idx, stemmer, stop_list)

        # Guardar el último bloque si no está vacío
        if self.inverted_index:
            self._save_block_to_disk()

    def _save_block_to_disk(self):
        sorted_terms = dict(sorted(self.inverted_index.items(), key=lambda t: t[0].token))
        with open(f'block_{self.block_counter}.pkl', 'wb') as block_file:
            pickle.dump(sorted_terms, block_file)
        self.block_counter += 1

    def _process_content(self, content, doc_idx, stemmer, stop_list):
        doc_words = re.findall(r'\w+', content)

        for doc_word in doc_words:
            if doc_word in stop_list:
                continue

            token = stemmer.stem(doc_word)
            index_key = InvIndexKey(token)

            postings_list = self.inverted_index[index_key]

            # Verificar el tamaño del índice
            index_size = sys.getsizeof(pickle.dumps(self.inverted_index))
            if index_size + sys.getsizeof(index_key) + sys.getsizeof(InvIndexVal(doc_idx, 1)) >= PAGE_SIZE:
                self._save_block_to_disk()
                self.inverted_index.clear()  # Limpiar el índice para el siguiente bloque

            # Añadir el término y su posting list al índice
            for value in self.inverted_index[index_key]:
                if value.doc_index == doc_idx:
                    value.tf += 1
                    break
            else:
                self.inverted_index[index_key].append(InvIndexVal(doc_idx, 1))

    def _order_index_by_tokens(self):
        """
        Orders all terms inside the index alphabetically
        """
        self.inverted_index = dict(sorted(self.inverted_index.items(), key=lambda t: t[0].token))

    def _process_idf(self):
        """
        Calculates the idf and tf.idf of all terms in our index
        """
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

    def final_query(self, query_text, n_results):
        stemmer = SnowballStemmer(language='spanish')
        with open('stop_words_spanish.txt', encoding='utf-8') as file:
            stop_list = [line.rstrip().lower() for line in file]

        query_words = re.findall(r'\w+', query_text)
        query_vector = self._get_final_vector(query_words, stemmer, stop_list)

        similarities = []
        for doc_idx in range(self.docs_counter):
            doc_vector = self._get_final_vector_for_doc(doc_idx)
            similarity = cosine_similarity([query_vector], [doc_vector])[0][0]
            similarities.append((doc_idx, similarity))

        similarities.sort(key=lambda x: -x[1])
        return [(doc_idx, score) for doc_idx, score in similarities[:n_results]]

    def _get_final_vector(self, words, stemmer, stop_list):
        vector = [0] * len(self.final_index)
        for word in words:
            if word in stop_list:
                continue

            token = stemmer.stem(word)
            index_key = InvIndexKey(token)

            if index_key in self.final_index:
                idx = list(self.final_index.keys()).index(index_key)
                vector[idx] += 1

        return np.array(vector)

    def _get_final_vector_for_doc(self, doc_idx):
        vector = [0] * len(self.final_index)
        for idx, (key, values) in enumerate(self.final_index.items()):
            for value in values:
                if value.doc_index == doc_idx:
                    vector[idx] = value.tf_idf

        return np.array(vector)

    def _get_vector(self, words, stemmer, stop_list):
        vector = [0] * len(self.inverted_index)
        for word in words:
            if word in stop_list:
                continue

            token = stemmer.stem(word)
            index_key = InvIndexKey(token)

            if index_key in self.inverted_index:
                idx = list(self.inverted_index.keys()).index(index_key)
                vector[idx] += 1

        return np.array(vector)

    def _get_vector_for_doc(self, doc_idx):
        vector = [0] * len(self.inverted_index)
        for idx, (key, values) in enumerate(self.inverted_index.items()):
            for value in values:
                if value.doc_index == doc_idx:
                    vector[idx] = value.tf_idf

        return np.array(vector)

    def merge_blocks(self, block_filenames, final_index_filename):
        merged_index = defaultdict(list)
        for block_filename in block_filenames:
            with open(block_filename, 'rb') as block_file:
                block = pickle.load(block_file)
                for term, postings_list in block.items():
                    merged_postings_list = merged_index[term]
                    for posting in postings_list:
                        # Buscar si el documento ya está en la lista de postings fusionada
                        for merged_posting in merged_postings_list:
                            if merged_posting.doc_index == posting.doc_index:
                                # Sumar la frecuencia del término
                                merged_posting.tf += posting.tf
                                break
                        else:
                            # Si el documento no está en la lista de postings fusionada, agregarlo
                            merged_postings_list.append(posting)

        # Calcular el IDF y TF-IDF para cada término y documento en el índice fusionado
        for term, postings_list in merged_index.items():
            term.idf = math.log10(len(block_filenames) / len(postings_list))
            for posting in postings_list:
                posting.tf_idf = term.idf * math.log10(1 + posting.tf)

        # Guardar el índice fusionado en el archivo
        with open(final_index_filename, 'wb') as final_index_file:
            pickle.dump(merged_index, final_index_file)

    def load_final_index(self, final_index_filename):
        with open(final_index_filename, 'rb') as final_index_file:
            self.final_index = pickle.load(final_index_file)



my_index = InvIndex()
my_index.index_docs(["libro1.txt", "libro2.txt", "libro3.txt", "libro4.txt", "libro5.txt", "libro6.txt"])

# Lista de nombres de archivos de bloque
block_filenames = [f'block_{i}.pkl' for i in range(27)]

# Nombre del archivo que contendrá el índice final
final_index_filename = 'final_index.pkl'

my_index.load_final_index(final_index_filename)
result = my_index.final_query("Tras la huida de Frodo y Sam en Parth Galen, Boromir muere a manos de los Uruk-hai mientras protegía a Merry y Pippin, los cuales son apresados por los sirvientes de Saruman. Aragorn, Legolas y Gimli deciden entonces perseguirles con el fin de rescatar a los dos hobbits. A partir de ese momento, la narración se divide en varias partes: por un lado, la persecución de los tres cazadores y por otro, las peripecias de Merry y Pippin en manos de los Orcos. En la primera, los tres cazadores se encuentran con el Éored Rohirrim de Éomer, Mariscal del Reino de Rohan, quien les informa sobre la Batalla en los Lindes de Fangorn en donde, aparentemente, habrían perecido los dos Hobbits. Esta parte culmina cuando Aragorn descubre huellas, en el campo de batalla, que los llevan a internarse en el Bosque de Fangorn y a reencontrarse con Gandalf, ahora convertido en el Mago Blanco. En la otra, Merry y Pippin van dejando señales para que los cazadores los rescaten, pensando en ardides para escapar, sufriendo la tortura y el cansancio. Al final, los Hobbits consiguen escaparse en medio de la batalla y refugiarse en el bosque de Fangorn, donde se encuentran con Bárbol, un Ent. Éste los lleva al interior del bosque a su casa (una vez que descubre que no se trata de Orcos), ayudándolos a reponerse de las fatigas y enterándose de las noticias del mundo exterior. Al otro día, el Ent convoca a una asamblea de sus congéneres para definir lo que harán ante el peligro que representa Saruman para Rohan y por ende a Gondor y al Oeste. Luego del reencuentro con Gandalf, los tres cazadores más el mago se dirigen a Edoras, en donde liberan a Théoden de la influencia maligna que ejercía el Mago de Isengard a través de su sirviente Gríma. Frente a la inminencia del ataque de Saruman, Gandalf aconseja al Rey de Rohan replegarse al Abismo de Helm para defender mejor el territorio, cosa que así hacen. Mientras preparan el repliegue, el mago se va de Meduseld con la intención de seguir una estrategia prefijada para derrotar a su oponente. En esta parte, se produce la Batalla del Abismo de Helm en donde las fuerzas combinadas de Rohirrim y Ucornos, tras la oportuna llegada de Gandalf con Rohirrim del Folde Oeste, derrotan por completo al ejército de la Mano Blanca. Estas historias confluyen en los últimos cuatro capítulos, del libro III: tras la batalla, una comitiva integrada por Théoden, Gandalf, Aragorn, Légolas, Gimli, Éomer y una treintena de caballeros, parten hacia Isengard. Al llegar son recibidos, para sorpresa de todos (menos de Gandalf) por Merry y Pippin, que están sentados en los escombros de las Puertas de Isengard. Los hobbits disfrutan de un segundo desayuno mientras cuentan a sus amigos todas las experiencias vividas desde su separación, y relatan como los Ents derrotaron a Saruman y destruyeron Isengard. Más tarde, se dirigen a Orthanc para mantener un diálogo con el Mago Blanco, que quedó atrapado dentro de la torre. La intención de Gandalf era darle otra oportunidad a Saruman para que se retractara de sus actos y los ayudara a vencer a Sauron. Pero él se niega y entonces deciden dejarle en custodia de Bárbol y encerrado en Orthanc. Previo a ello, Gríma arroja un objeto que Gandalf se apresura a guardar entre sus ropas, quitándoselo a Pippin. Pippin, intrigado y curioso con el objeto que Gandalf guardaba celosamente, y aprovechando que todos dormían en el campamento de Dol Baran, toma el objeto y sin saber que se trataba de la Palantir de Orthanc, lo mira quedando atrapado por la mirada de Sauron, puesto que este estaba comunicado con Barad-dûr. Tras tener horribles visiones, involuntariamente el hobbit revela a Sauron la estrategia de Gandalf. Esta desafortunada acción obliga al mago a llevar a Pippin a Minas Tirith, capital del Reino de Gondor, para ponerlo a salvo del «Señor oscuro» y para preparar la defensa de la ciudad ante la precipitación de los acontecimientos.", 3)
print(result)  # Imprime los índices de los 3 documentos más cercanos

