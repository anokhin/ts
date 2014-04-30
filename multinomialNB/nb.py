import argparse
import codecs
import unicodedata
import operator

import nltk
import numpy

from sklearn.cross_validation import cross_val_score
from sklearn.feature_extraction import DictVectorizer
from sklearn.naive_bayes import MultinomialNB

import csv
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from sklearn.base import BaseEstimator

class MyMultinomialNB(BaseEstimator):
    def __init__(self):
        self.tokens = {}
        self.tokens_count = 0
        self.classes = {} 
        self.classes_count = 0
        self.classes_proba = []
        self.token_proba = [] 


    def read_tokens(self, docs):
        tokens_set = set()
        for d in docs:
            tokens_set.update(set(d))
        
        self.tokens = {}
        self.tokens_count = len(tokens_set)
        for i in range(self.tokens_count):
           self.tokens[tokens_set.pop()] = i


    def read_classes(self, classes):
        self.classes = {}
        classes_set = set(classes)
        self.classes_count = len(classes_set)
        for i in range(self.classes_count):
           self.classes[classes_set.pop()] = i


    def get_classes_proba(self, classes):
        self.classes_proba = [0 for i in range(self.classes_count)]
        for c in classes:
            self.classes_proba[self.classes[c]] += (1.0/self.classes_count)


    def get_tokens_proba(self, docs, classes):
        self.tokens_proba = [[0 for i in range(self.classes_count)] for i in range(self.tokens_count)]
        class_docs = {}
        for c in self.classes:
            class_docs[c] = [[],0]
            for i in range(len(classes)):
                if c == classes[i]:
                    class_docs[c][0].append(docs[i])
                    class_docs[c][1] += len(docs[i])

        for token in self.tokens:
            for c in class_docs:
                count = 0
                for d in class_docs[c][0]:
                    for t in d:
                        if token == t:
                           count += 1
                if class_docs[c][1] > 0:
                    self.tokens_proba[self.tokens[token]][self.classes[c]] = count/float(class_docs[c][1])

            
    def fit(self, docs, classes):        
        self.read_tokens(docs)
        self.read_classes(classes)
        self.get_classes_proba(classes)
        self.get_tokens_proba(docs, classes)
        return self


    def calc_score(self, doc):
        score = dict([(c,0) for c in self.classes])
        for c in self.classes:
           score[c] += self.classes_proba[self.classes[c]]
           for token in doc:
              if token in self.tokens:
                  score[c] *= self.tokens_proba[self.tokens[token]][self.classes[c]]
        return score


    def predict(self, doc):
        score = self.calc_score(doc)
        return max(score.iteritems(), key=operator.itemgetter(1))[0]


    def predict_proba(self, doc):
        score = self.calc_score(doc)
        return score

    
    def score(self, docs, classes):        
        count_all = len(classes)
        count_true = 0
        for i in range(count_all):
            target = classes[i]
            doc = docs[i]
            c = self.predict(doc)
            if c == target:
                count_true += 1
        return count_true/float(count_all)
    

def unicode_csv_reader(unicode_csv_data, **kwargs):
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data), delimiter='\t', quotechar='|', **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def utf_8_encoder(unicode_csv_data):
    for line in unicode_csv_data:
        yield line.encode('utf-8')


def read_documents(data_path):
    with codecs.open(data_path, 'rU', "utf-8") as data_file:
        reader = unicode_csv_reader(data_file)
        for (uid, fn, ln, sex, text) in reader:
            if text:
                yield sex, text


def normalise_document(doc):
    return ''.join(c for c in unicodedata.normalize('NFD', doc.lower()) if not unicodedata.combining(c))


def tokenize_document(doc, n):
    tokenizer = nltk.WordPunctTokenizer()
    russian_stemmer = SnowballStemmer("russian")
    english_stemmer = SnowballStemmer("english")
    for token in tokenizer.tokenize(doc):
#        if unicode(token).encode('utf-8') in stopwords.words('russian'): continue
#        if unicode(token).encode('utf-8') in stopwords.words('english'): continue
#        """
#        token = russian_stemmer.stem(token)
#        token = english_stemmer.stem(token)
#        yield token
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
    return MyMultinomialNB()


def validate_model(model, x, y, folds=20):
    """
    Computes cross-validation score for the given data set and model

    Returns:
        A numpy.array of accuracy scores.
    """
    scores = cross_val_score(model, x, y, cv=folds)
    return scores


def main():
    args = parse_args()
    docs = []
    sexs = []
    sex_freq = {}
    for sex, doc in read_documents(args.ds_path[0]):
        normalized_doc = normalise_document(doc)
        sex = int(sex)

        token_freq = {}
        for token in tokenize_document(normalized_doc, args.n):
            token_freq[token] = 1 + token_freq.get(token, 0)
            if sex not in sex_freq:
                sex_freq[sex] = (len(sex_freq), {})
            sex_freq[sex][1][token] = 1 + sex_freq[sex][1].get(token, 0)

        docs.append(token_freq)
        sexs.append(sex_freq[sex][0])

    features = select_features(sex_freq, args.top_tokens)
    keep_only_features(docs, features)
    dv = DictVectorizer()
    x = dv.fit_transform(docs).todense()
   
    model = create_model()
    scores = validate_model(model, x, numpy.array(sexs))
    print "Model mean accuracy: {}".format(numpy.mean(scores))


def parse_args():
    parser = argparse.ArgumentParser(description='Experiments Text Mining')
    parser.add_argument('ds_path', nargs=1)
    parser.add_argument('-n', dest='n', help='Stands for n that is used in n-grams', type=int, default=7)
    parser.add_argument('-t', dest='top_tokens', help='Top tokens to take in each language', type=int, default=20)
    return parser.parse_args()




if __name__ == "__main__":
    main()
