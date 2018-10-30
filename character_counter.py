from collections import Counter
import os
import sys
import time
from punctuation import CHIN_PUNC
import string

# os.walk
# dirpath, dirnames, filenames

SKIP = (CHIN_PUNC + string.whitespace +
        string.digits + string.punctuation +
        string.ascii_letters)

class Document:
    def __init__(self, text, filename=None):
        self.text = text
        self.filename = filename

        self.char_counts = Counter(t for t in text if t not in SKIP)
        self.total_char_count = sum(self.char_counts.values())


    @classmethod
    def from_file(cls, filename):
        with open(filename, 'r') as infile:
            text = infile.read()
        return Document(text, filename)

    def __str__(self):
        f = self.filename if self.filename else 'text'
        return f'Doc constructed from {f} with {self.token_count} tokens'

class Corpus:
    def __init__(self, filenames):
        self.documents = tuple(Document.from_file(f) for f in filenames)
        self.char_counts = sum((d.char_counts for d in self.documents), Counter())



def get_filenames(root_dir='./talks/'):
    all_filenames = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        all_filenames += [os.path.join(dirpath, f) for f in filenames]
    return all_filenames


if __name__ == '__main__':
    filenames = get_filenames()
    corpus = Corpus(filenames)



