from collections import Counter

import os
import sys
import time
import re

from tqdm import tqdm
import jieba
from zhon import hanzi
from punctuation import CHIN_PUNC
import string

# os.walk
# dirpath, dirnames, filenames

words_to_add = ['阿们', '定额组', '弟兄姐妹们', '弟兄姊妹们']
for word in words_to_add:
    jieba.add_word(word)

SKIP = (CHIN_PUNC + string.whitespace +
        string.digits + string.punctuation +
        string.ascii_letters)

CHAR_PATTERN = re.compile(f'[{hanzi.characters}]')
SENT_PATTERN = re.compile(r'[0-9\-'+hanzi.sentence[1:])

class Document:
    def __init__(self, text, filename=None):
        self.text = text
        self.filename = filename

        self.char_counts = Counter(t for t in text if t not in SKIP)
        self.char_set = set(char for char in self.char_counts)
        self.total_char_count = sum(self.char_counts.values())

        self.words = []
        for word in jieba.cut(text, cut_all=False):
            if word in SKIP:
                continue
            if len(word) == len(CHAR_PATTERN.findall(word)):
                self.words.append(word)
        self.word_counts = Counter(self.words)
        self.word_set = set(word for word in self.word_counts)
        self.total_word_count = sum(self.word_counts.values())

        self.sentences = [s for s in SENT_PATTERN.findall(text) if len(s)>5]

        self.ngrams = {}

    def get_ngram_model(self, n, save=True):
        ngram = self.ngrams.get(n)
        if not ngram:
            ngram = self._compute_ngram(n)
            if save:
                self.ngrams[n] = ngram
        return ngram

    def _compute_ngram(self, n):
        ngram_counts = Counter()
        for i in range(len(self.words)-n):
            ngram = self.words[i:i+n]
            ngram_counts[' '.join(ngram)] += 1
        return ngram_counts

    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as infile:
            text = infile.read()
        return cls(text, filename)

    def __str__(self):
        f = self.filename if self.filename else 'text'
        return f'Doc constructed from {f} with {self.token_count} tokens'

class Corpus:
    def __init__(self, filenames):
        print('Creating Documents')
        self.documents = tuple(Document.from_file(f) for f in tqdm(filenames))

        print('Counting characters')
        self.char_counts = Counter()
        for d in tqdm(self.documents):
            self.char_counts.update(d.char_counts)

        print('Counting words')
        self.word_counts = Counter()
        for d in tqdm(self.documents):
            self.word_counts.update(d.word_counts)

        print('Counting sentences')
        self.sentence_counts = Counter(s for doc in tqdm(self.documents)
                                       for s in doc.sentences)

        self.ngrams = {}

        self.total_chars = sum(self.char_counts.values())
        self.total_words = sum(self.word_counts.values())
        self.total_sentences = sum(self.sentence_counts.values())

    def get_ngram_model(self, n, save=True, save_doc=True):
        ngram = self.ngrams.get(n)
        if not ngram:
            ngram = self._compute_ngram(n, save_doc=save_doc)
            if save:
                self.ngrams[n] = ngram
        return ngram

    def _compute_ngram(self, n, save_doc=True):
        ngram = Counter()
        for doc in tqdm(self.documents):
            ngram.update(doc.get_ngram_model(n, save=save_doc))
        return ngram


def get_token_vs_type_counts(corpus):
    token_counts = [0]
    type_counts = [0]
    types = set()
    tmp = 0
    for doc in corpus.documents:
        for token in doc.text:
            if token in SKIP:
                continue
            if token in types:
                tmp += 1
            else:
                types.add(token)
                token_counts.append(token_counts[-1] + tmp + 1)
                type_counts.append(type_counts[-1]+1)
                tmp = 0
    return token_counts, type_counts


def get_cutoff(corpus, cutoff=.8):
    types = []
    type_count = 0
    token_count = 0
    total = sum(corpus.char_counts.values())
    common = iter(corpus.char_counts.most_common())
    while (token_count/total) < cutoff:
        char, count = next(common)
        token_count += count
        types.append(char)
        type_count += 1
    print(f'With {type_count} types, can read '
          f'{token_count}/{total} tokens'
          f'--{cutoff}')
    return types, type_count




def get_filenames(root_dir='./talks/'):
    all_filenames = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        all_filenames += [os.path.join(dirpath, f) for f in filenames 
                          if not f.endswith('.swp')]
    return all_filenames


if __name__ == '__main__':
    filenames = get_filenames()[:50]
    #doc = Document.from_file(filenames[0])
    #corpus = Corpus(filenames)



