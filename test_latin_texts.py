# -*- mode: Python; coding: utf-8 -*-

from __future__ import division

from corpus import Document, LatinAuthorsCorpus
from naive_bayes import NaiveBayes
from maxent import MaxEnt

import sys, os
from unittest import TestCase, main

import string

class LatinText(Document):
    def features(self):
        puncs = [p for p in string.punctuation]
        for punc in puncs:
            data = self.data.lower().replace(punc, '')
        words = [w for w in data.split()]

        return set(words)

def get_labels(classifier):
    if isinstance(classifier, NaiveBayes):
        labels = sorted(classifier.model.keys())
    elif isinstance(classifier, MaxEnt):
        labels = sorted([l for l in classifier.model[2].keys()])
    else:
        raise TypeError
    return labels

def accuracy(classifier, test, verbose=sys.stderr):
    correct = [classifier.classify(x) == x.label for x in test]
    if verbose:
        # modified to show 2 decimal places
        acc = 100.0 * sum(correct) / len(correct)
        split_acc = str(acc).split('.')
        s = "accuracy: " + "{}.{:.2}%\n".format(split_acc[0], split_acc[1])
        print >> verbose, s,
    return sum(correct) / len(correct)

def recall(classifier, test, verbose=sys.stderr):
    r = {}
    for label in get_labels(classifier):
        true_pos = [classifier.classify(x) == x.label and x.label == label for x in test]
        false_neg = [classifier.classify(x) != x.label and x.label == label for x in test]
        if sum(true_pos + false_neg) != 0:
            r[label] = sum(true_pos) / sum(true_pos + false_neg)
        else:
            r[label] = 0.0
    if verbose:
        for label in sorted(r.keys()):
            split_r = str(100.0 * r[label]).split('.')
            s = str(label) + " recall: "
            s += "{}.{:.2}%\n".format(split_r[0], split_r[1])
            print >> verbose, s,
    return r

def precision(classifier, test, verbose=sys.stderr):
    p = {}
    for label in get_labels(classifier):
        true_pos = [classifier.classify(x) == x.label and x.label == label for x in test]
        false_pos = [classifier.classify(x) == label and x.label != label for x in test]
        if sum(true_pos + false_pos) != 0:
            p[label] = sum(true_pos) / sum(true_pos + false_pos)
        else:
            p[label] = 0.0
    if verbose:
        for label in sorted(p.keys()):
            split_p = str(100.0 * p[label]).split('.')
            s = str(label) + " precision: "
            s += "{}.{:.2}%\n".format(split_p[0], split_p[1])
            print >> verbose, s,
    return p

def f1(classifier, test, verbose=sys.stderr):
    r = recall(classifier, test, verbose=verbose)
    p = precision(classifier, test, verbose=verbose)
    f = {}
    for label in r:
        if (r[label] + p[label]) != 0.0:
            f[label] = (2 * r[label] * p[label]) / (r[label] + p[label])
        else:
            f[label] = 0.0
    if verbose:
        for label in sorted(f.keys()):
            split_f = str(100.0 * f[label]).split('.')
            s = str(label) + " f1: "
            s += "{}.{:.2}%\n".format(split_f[0], split_f[1])
            print >> verbose, s,
    return f

def avg_f1(classifier, test, verbose=sys.stderr):
    f = f1(classifier, test, verbose=verbose)
    if verbose:
        split_f = str(100.0 * sum(f.values()) / len(f)).split('.')
        s = "avg f1: " + "{}.{:.2}%\n".format(split_f[0], split_f[1])
        print >> verbose, s,
    return sum(f.values()) / len(f)

class LatinCorpusTest(TestCase):
    u"""Tests for the naïve Bayes classifier."""

    def test_naive_bayes(self, document_class=LatinText):
        latin_works = LatinAuthorsCorpus(document_class=document_class)
        classifier = NaiveBayes()
        if 'latin_bayes' in os.listdir('models'):
            classifier.load('models/latin_bayes')
        else:
            classifier.train(latin_works.train_data + latin_works.dev_data)
            classifier.save('models/latin_bayes')
        # avg_f1(classifier, latin_works.test_data, verbose=sys.stdout)
        self.assertGreater(accuracy(classifier, latin_works.test_data), 0.5)

    def test_maxent(self, document_class=LatinText):
        latin_works = LatinAuthorsCorpus(document_class=document_class)
        classifier = MaxEnt()
        if 'latin_maxent' in os.listdir('models'):
            classifier.load('models/latin_maxent')
        else:
            classifier.train(latin_works.train_data, latin_works.dev_data)
            classifier.save('models/latin_maxent')
        # avg_f1(classifier, latin_works.test_data, verbose=sys.stdout)
        self.assertGreater(accuracy(classifier, latin_works.test_data), 0.5)

if __name__ == '__main__':
    # Run all of the tests, print the results, and exit.
    main(verbosity=2)
