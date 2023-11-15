import math
import re

from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer

from inv_index_attributes import InvIndexKey, InvIndexVal

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
            print(f'Proccessing document {doc}')
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