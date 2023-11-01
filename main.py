import math
import re
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


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

    def index_docs(self, docs):
        """
        Main function that indexes all terms in a given list of docs
        """
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
        """
        Calculates the TF of all the terms in a specific doc
        """
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

    def query(self, query_text, n_results):
        stemmer = SnowballStemmer(language='spanish')
        with open('stop_words_spanish.txt', encoding='utf-8') as file:
            stop_list = [line.rstrip().lower() for line in file]

        query_words = re.findall(r'\w+', query_text)
        query_vector = self._get_vector(query_words, stemmer, stop_list)

        similarities = []
        for doc_idx in range(self.docs_counter):
            doc_vector = self._get_vector_for_doc(doc_idx)
            similarity = cosine_similarity([query_vector], [doc_vector])[0][0]
            similarities.append((doc_idx, similarity))

        similarities.sort(key=lambda x: -x[1])
        return [(doc_idx, score) for doc_idx, score in similarities[:n_results]]

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


my_index = InvIndex()
my_index.index_docs(["libro1.txt", "libro2.txt", "libro3.txt", "libro4.txt", "libro5.txt", "libro6.txt"])
#print(my_index)

#result = my_index.query("Finalizada la batalla, los capitanes de los ejércitos deciden, por idea de Gandalf, desviar la atención de Sauron para que Frodo pueda cumplir su misión y, con las fuerzas que les quedan, se dirigen hacia la Puerta Negra. Una vez allí y tras negarse a las condiciones de Sauron, se inicia la batalla", 3)
#result = my_index.query("casa casa casa casa casa casa", 3)
result = my_index.query("de camino a Edoras, Aragorn y el rey Théoden", 3)
print(result)  # Imprime los índices de los 3 documentos más cercanos
