import argparse
import codecs
import unicodedata
import operator

import nltk
import numpy

from sklearn.cross_validation import cross_val_score
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB


__author__ = 'Nikolay Anokhin'


def read_documents(data_path):
    """
    Reads a sequence of documents from the text file
    located on a given path.

    Returns:
        A generator of tuples (LANG_CODE, unicode)
    """
    with codecs.open(data_path, 'rU', "utf-8") as data_file:
        for line in data_file:
            lang, doc = line.strip().split('\t')
            yield lang, doc


def normalise_document(doc):
    """
    Convert document to lower-case and remove accents

    Returns:
        A normalised document as unicode
    """
    return ''.join(c for c in unicodedata.normalize('NFD', doc.lower()) if not unicodedata.combining(c))


def tokenize_document(doc, n):
    """
    Split document in N-Grams

    Returns:
        Generator of unicode n-grams
    """
    tokenizer = nltk.WordPunctTokenizer()
    for token in tokenizer.tokenize(doc):
        if len(token) >= n:
            for ngram in nltk.ngrams(token, n):
                yield u"".join(ngram)


def select_features(lang_freq, top_tokens):
    """
    From each language selects top_tokens to be used as features

    Returns:
        set(unicode tokens)
    """
    features = set()
    for lang, (lid, token_freq) in lang_freq.iteritems():
        sorted_token_freq = sorted(token_freq.iteritems(), key=operator.itemgetter(1), reverse=True)
        for token, freq in sorted_token_freq[:top_tokens]:
            features.add(token)
    return features


def keep_only_features(docs, features):
    """
    Removes non-feature tokens from the document representations
    """
    for token_freq in docs:
        for token in token_freq.keys():
            if token not in features:
                del token_freq[token]


def create_model():
    """
    Initialise an NB model, supported by Sklearn

    Returns:
        Sklearn model instance
    """
    return MultinomialNB()


def validate_model(model, x, y, folds=20):
    """
    Computes cross-validation score for the given data set and model

    Returns:
        A numpy.array of accuracy scores.
    """
    scores = cross_val_score(model, x, y, cv=folds)
    return scores


def main():
    print "## Welcome to the Text Mining tutorial ##"

    args = parse_args()

    # A list of dicts, each representing one document in format:
    # {feature1: count1, ...}
    docs = []
    # A list of numeric language ids corresponding to each document
    langs = []
    # Contains entries like {lang_code: {lang_id, {token_frequencies}}}
    lang_freq = {}
    for lang, doc in read_documents(args.ds_path[0]):
        normalized_doc = normalise_document(doc)

        token_freq = {}
        for token in tokenize_document(normalized_doc, args.n):
            token_freq[token] = 1 + token_freq.get(token, 0)
            if lang not in lang_freq:
                lang_freq[lang] = (len(lang_freq), {})
            lang_freq[lang][1][token] = 1 + lang_freq[lang][1].get(token, 0)

        docs.append(token_freq)
        langs.append(lang_freq[lang][0])

    features = select_features(lang_freq, args.top_tokens)

    keep_only_features(docs, features)

    dv = DictVectorizer()
    x = dv.fit_transform(docs).todense()

    model = create_model()

    scores = validate_model(model, x, numpy.array(langs))
    print "Model mean accuracy: {}".format(numpy.mean(scores))


def parse_args():
    parser = argparse.ArgumentParser(description='Experiments Text Mining')
    parser.add_argument('ds_path', nargs=1)
    parser.add_argument('-n', dest='n', help='Stands for n that is used in n-grams', type=int)
    parser.add_argument('-t', dest='top_tokens', help='Top tokens to take in each language', type=int, default=10)
    return parser.parse_args()




if __name__ == "__main__":
    main()
