import numpy as np
from math import log


class Data:
	def __init__(self, vocab, token_gen_table, token_user_table):
		self.vocab = vocab
		self.token_gen_table = token_gen_table
		self.token_user_table = token_user_table
		genders = [1,2]
		prob_gender = np.zeros(2)
		prob_token_gender = np.zeros((len(vocab), 2))

		ndocs = np.zeros(2)

		for i in range(0, len(self.token_user_table) - 1):
			ndocs[self.token_user_table[i,0] - 1] += 1

		#tf = zeros((len(vocab), len(docs)))
		#idf = zeros(len(vocab))
		#tf_idf_table = zeros((len(vocab), len(docs)))


	#def tokenize(self, doc):


	#def makeVocab(self):


	'''def make_token_doc_table(self):
		tf = zeros((len(vocab), len(docs)))
		buff = zeros((len(vocab), len(docs)))
		df = zeros((len(vocab), len(docs)))
		idf = zeros((len(vocab), len(docs)))

		for dv in vocab:
			for di in docs:
				if (dv in di.vocab):
					tf[vocab.index(vi), docs.index(di)] += 1
					buff[vocab.index(vi), docs.index(di)] = 1

			df[vocab.index(dv)] = sum(buff[vocab.index(dv)], :)
			idf[vocab.index(dv)] = log( len(docs)/df[vocab.index(dv)] )



	def tf_idf(self):
		tf_idf_table = zeros((len(vocab), len(docs)))

		for dv in vocab:
			for di in docs:
				tf_idf_table[vocab.index(vi), docs.index(di)] = 
					tf[vocab.index(vi), docs.index(di)]*idf[vocab.index(dv)]'''




		

	def train(self, model_type):
		prob_gender = zeros(2)
		prob_token_gender = zeros(len(vocab), 2)
		for gi in self.genders:
			prob_gender[gi-1] = self.ndocs[gi]/sum(self.ndocs)

			for vi in vocab:
				if model_type == "MultinomialLaplase":

					if vi in vocab: 
						prob_token_gender[self.vocab.index(vi), gi] = (token_gen_table[self.vocab.index(vi), gi] + 0.5)/(sum(self.token_gen_table[:,gi]) + 0.5*len(self.vocab))

	
	def apply(self, tokens):

		loc_vocab = tokens
		score_gen = zeros(2)

		for gi in self.genders:
			score_gen[gi] += log(self.prob_gender[gi])

			for vi in loc_vocab:
				if vi in self.vocab:
					score_gen[gi] += self.prob_token_gender[self.vocab.index(vi), gi]

		return argmax(score_gen) + 1


		