# -*- mode: Python; coding: utf-8 -*-

import json
import os
import codecs
from glob import glob

__author__ = u"José Molina"

def open_json(filepath):
    """Cleanup input xml file, return string."""
    with open(filepath) as f:
        text = f.read()
    return json.loads(text)


def find_text(filepath):
    """
    Find the field in the doc that contains the body text, and call recursive_find_text on it.
    :param json_doc: json_object of a document
    :return: the raw text of the document
    """
    json_doc = open_json(filepath)
    if 'TEI.2' in json_doc and 'text' in json_doc['TEI.2']:
        text = ''
        if 'body' in json_doc['TEI.2']['text']:
            text = recursive_find_text(json_doc['TEI.2']['text']['body'])
        elif 'group' in json_doc['TEI.2']['text'] and 'text' in json_doc['TEI.2']['text']['group']:
            if 'body' in json_doc['TEI.2']['text']['group']['text']:
                text = recursive_find_text(json_doc['TEI.2']['text']['group']['text']['body'])
            else:
                for text_dict in json_doc['TEI.2']['text']['group']['text']:
                    text += recursive_find_text(text_dict['body'])
        else:
            message = 'The JSON file ' + filepath + ' does not contain body text.'
            raise KeyError(message)
        return text
    else:
        message = 'The JSON file ' + filepath + ' does not contain the field "TEI.2", ' \
                  'or the field "TEI.2" does not contain the subfield "text".'
        raise KeyError(message)


def recursive_find_text(item):
    """
    Recursively find all the text fields in the json
    :param item: initially the json_object to search
    :return: a string of text
    """
    s = ''
    if item is None:
        return s
    elif isinstance(item, (str, unicode)):
        return item + ' '
    elif isinstance(item, list):
        for sub_item in item:
            s += recursive_find_text(sub_item)
        return s
    elif isinstance(item, dict):
        for tag in ['#text', 'p', 'q', 'quote', 'cit', 'sp', 'l', 'div1', 'div2', 'div3']:
            if tag in item:
                s += recursive_find_text(item[tag])
        return s
    else:
        item_type = type(item).__name__
        message = "This item is a " + item_type + ". " \
                  "The function find_text takes either a str, a list, or a dict."
        raise TypeError(message)


if __name__ == '__main__':
    data_dir = 'latin_text_perseus'
    output_path = data_dir + os.sep + 'latin_authors_corpus.json'
    files = [y for x in os.walk(data_dir) for y in glob(os.path.join(x[0], '*lat.xml.json'))]
    with codecs.open(output_path, 'w', encoding='utf-8') as output_file:
        json_corpus = {}
        for filepath in files:
            text = find_text(filepath)
            if text == '':
                raise ValueError('No text was found in ' + filepath + '.')
            else:
                author = filepath.split(os.sep)[1]
                if author in json_corpus:
                    json_corpus[author].append(text)
                else:
                    json_corpus[author] = [text]
        json.dump(json_corpus, output_file)
