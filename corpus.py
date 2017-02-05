# -*- mode: Python; coding: utf-8 -*-

"""For the purposes of classification, a corpus is defined as a collection
of labeled documents. Such documents might actually represent words, images,
etc.; to the classifier they are merely instances with features."""

from abc import ABCMeta, abstractmethod
from csv import reader as csv_reader
import csv, codecs
import json
from glob import glob
from os.path import basename, dirname, split, splitext
from random import shuffle, seed

class Document(object):
    """A document completely characterized by its features."""

    max_display_data = 30  # limit for data abbreviation

    def __init__(self, data, label=None, source=None):
        self.data = data
        self.label = label
        self.feature_vector = []
        self.source = source

    # def __str__(self):
    #     return self.__repr__()
        
    # def __repr__(self):
    #     return (u"<%s: %s>" % (self.label, self.abbrev()) if self.label else
    #             u"%s" % self.abbrev())

    def abbrev(self):
        return (self.data if len(self.data) < self.max_display_data else
                self.data[0:self.max_display_data] + "...")

    def features(self):
        """A list of features that characterize this document."""
        return [self.data]

class Corpus(object):
    """An abstract collection of documents."""

    __metaclass__ = ABCMeta

    def __init__(self, datafiles, document_class=Document):
        self.documents = []
        self.datafiles = glob(datafiles)
        for datafile in self.datafiles:
            self.load(datafile, document_class)

    # Act as a mutable container for documents.
    def __len__(self): return len(self.documents)
    def __iter__(self): return iter(self.documents)
    def __getitem__(self, key): return self.documents[key]
    def __setitem__(self, key, value): self.documents[key] = value
    def __delitem__(self, key): del self.documents[key]

    @abstractmethod
    def load(self, datafile, document_class):
        """Make labeled document instances for the data in a file."""
        pass

class LatinAuthorsCorpus(Corpus):

    def __init__(self, datafiles="latin_text_perseus/latin_authors_corpus.json",
                 document_class=Document):
        self.train_data = []
        self.dev_data = []
        self.test_data = []
        super(LatinAuthorsCorpus, self).__init__(datafiles, document_class)

    def load(self, datafile, document_class, encoding='utf-8'):
        with codecs.open(datafile, 'r', encoding=encoding) as data:
            json_data = json.loads(data.read())
        for author in json_data:
            if len(json_data[author]) >= 5:
                docs = []
                for work in json_data[author]:
                    docs.append(document_class(work, author, datafile))
                assert len(docs) >= 5
                seed(3)
                shuffle(docs)
                k = int(0.5 * len(docs))
                j = int(0.75 * len(docs))
                self.documents.extend(docs)
                self.train_data.extend(docs[:k])
                self.dev_data.extend(docs[k:j])
                self.test_data.extend(docs[j:])
