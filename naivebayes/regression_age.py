from naive_bayes import BernoulliNB, GaussianNB, MultinomialNB
import argparse
import codecs
from sklearn import naive_bayes

from sklearn.cross_validation import cross_val_score
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import recall_score

import unicodedata
import numpy as np

from sklearn.datasets import load_iris

def read_rsv(data_path):
	rsv_content = codecs.open(data_path, 'r', 'utf-8').read()
	rows = rsv_content.split(unichr(30))[:-1]

	for row in rows:
		entries = row.split(unichr(31))
		if len(entries) > 3:
			tokens, gender = entries[:-2], entries[-2]
			if tokens and gender:
				yield tokens, gender


def normalize_record(doc):
	return ''.join(c for c in unicodedata.normalize('NFD', doc.lower()) if not unicodedata.combining(c))


def select_features(lang):
	features = set()
	for token in lang:
		features.add(token)
	return features


def validate_model(model, X, y, folds=10, scoring='accuracy'):
	scores = cross_val_score(model, X, y, cv=folds, scoring=scoring)
	return scores

def create_model():
	models = ['MultinomialNB', 'BernoulliNB', 'GaussianNB']
	alpha = [0.1, 0.5, 1.0, 1.5, 2.0, 5.0]
	for n in models:
		if n == 'GaussianNB':
			yield globals()[n]()
		else: 
			for a in alpha:
				yield globals()[n](alpha=a)


def main():
	print "## Classify FB users ##"

	args = parse_args()

	names = []
	genders = []

	for data, gender in read_rsv(args.ds_path[0]):
		user = u''
		for word in data:
			normalized_word = normalize_record(word)
			user += normalized_word + " "

		names.append(user)
		genders.append(gender)

	cv = CountVectorizer()
	X = cv.fit_transform(names).todense()

	for model in create_model():
		print model
		scores = validate_model(model, X, np.array(genders))
		print scores
		print "Mean accuracy: {0}".format(np.mean(scores))
		

def parse_args():
	parser = argparse.ArgumentParser(description="Homework Naive Bayes")
	parser.add_argument('ds_path', nargs=1, help='Path to unit separated file with data about Facebook users')
	return parser.parse_args()

if __name__ == "__main__":
	main()