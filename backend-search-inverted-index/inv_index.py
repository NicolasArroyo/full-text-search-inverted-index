import json
import math
import os
import pickle
import re
import sys

from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer

from inv_index_attributes import InvIndexKey, InvIndexVal


class InvIndex:
    PAGE_SIZE = 4096


    def __init__(self, language):
        self.inverted_index = defaultdict(list)
        self.docs_counter = 0
        self.block_count = 0
        self.stop_list = []
        self.language = language
        self.initial_blocks_dir = 'initial_blocks_' + self.language
        os.makedirs(self.initial_blocks_dir, exist_ok=True)


    def get_stop_list(self):
        with open('stop_words_spanish.txt', encoding='utf-8') as file:
            self.stop_list = [line.rstrip().lower() for line in file]

    def index_docs(self, docs):
        self.docs_counter = self.docs_counter + len(docs)

        self.get_stop_list()

        for doc_idx, doc in enumerate(docs):
            with open(doc, encoding="utf-8") as doc_file:
                doc_content = doc_file.read()

                if doc_content.split(',')[-1] != " " + self.language:
                    continue

                stemmer = get_stemmer(doc_content.split(',')[-1])
                self._process_content(doc_content, doc_idx, stemmer)

    def _process_content(self, content, doc_idx, stemmer):
        doc_words = re.findall(r'\w+', content)

        for doc_word in doc_words:
            if doc_word in self.stop_list:
                continue

            token = stemmer.stem(doc_word)
            index_key = InvIndexKey(token)

            if index_key in self.inverted_index:
                for value in self.inverted_index[index_key]:
                    if value.doc_index == doc_idx:
                        value.tf += 1
                        break
                else:
                    self.inverted_index[index_key].append(InvIndexVal(doc_idx, 1))
            else:
                self.inverted_index[index_key] = [InvIndexVal(doc_idx, 1)]

            index_size = sys.getsizeof(pickle.dumps(self.inverted_index))

            if index_size + sys.getsizeof(index_key) + sys.getsizeof(InvIndexVal(doc_idx, 1)) > self.PAGE_SIZE:
                self._order_index_by_tokens()
                self._process_idf()

                self.save_current_block()

                self.inverted_index.clear()

    def save_current_block(self):
        current_block = {}

        for token, postings in self.inverted_index.items():
            current_block[token.token] = [(val.doc_index, val.tf, val.tf_idf) for val in postings]

        with open(os.path.join(self.initial_blocks_dir, f'block_{self.block_count}.json'), 'w',
                  encoding='utf-8') as file:
            json.dump(current_block, file, ensure_ascii=False)

        self.block_count += 1

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


def get_stemmer(language: str):
    stemmer_map = {
        " ar": "arabic",
        " da": "danish",
        " nl": "dutch",
        " en": "english",
        " fi": "finnish",
        " fr": "french",
        " de": "german",
        " hu": "hungarian",
        " it": "italian",
        " no": "norwegian",
        " pt": "portuguese",
        " ro": "romanian",
        " ru": "russian",
        " es": "spanish",
        " sv": "swedish"
    }

    stemmer_language = stemmer_map.get(language)
    if stemmer_language:
        return SnowballStemmer(stemmer_language)
    else:
        return SnowballStemmer("english")
