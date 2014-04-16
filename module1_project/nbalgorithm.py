import numpy as np
from math import log
import re
import nltk
from nltk.corpus import stopwords


class NBAlgorithm:
	def __init__(self):
		self.vocab = []
		self.token_gen_table = np.zeros((len(self.vocab),2))
		self.token_user_table = np.zeros((1, 0))
		self.genders = [1,2]
		self.prob_gender = np.zeros(2)
		self.prob_token_gender = np.zeros((len(self.vocab), 2))
		self.ndocs = np.array([0, 0], dtype=int)


	def fit(self, train_features, train_labels):

		self.ndocs = np.array([0, 0], dtype=int)

		self.ndocs[0] = float(train_labels[train_labels < 1.5].size)
		self.ndocs[1] = float(train_labels[train_labels > 1.5].size)

		female_indices = np.where(train_labels == 1)[0]
		male_indices = np.where(train_labels == 2)[0]
		vocab_set = set()

		n_users = len(train_features)							# full vocabulary of training dataset assempling
		for tf in train_features:
			if len(tf[0]) <> 0:
				curr_bands = [key for key in tf[0]]
				vocab_set |= set(curr_bands)



		self.vocab = dict(zip(vocab_set, range(len(vocab_set))))				# vocabulary tranfser into dictionary data structure (for easier indexation)



		self.token_female_table = np.zeros((self.ndocs[0], len(vocab_set)))		# next two matrixes show amount of appearances for each band name
		self.token_male_table = np.zeros((self.ndocs[1], len(vocab_set)))		# each table refers to users of corresponding gender
		for i in range(self.ndocs[0]):
			real_i = female_indices[i]
			if len(train_features[real_i][0]) <> 0:
				curr_data = [ self.vocab.get(key) for key in train_features[real_i][0]]
				self.token_female_table[i, curr_data] += train_features[real_i][1]

		for i in range(self.ndocs[1]):
			real_i = male_indices[i]
			if len(train_features[real_i][0]) <> 0:
				curr_data = [self.vocab.get(key) for key in train_features[real_i][0]]
				self.token_male_table[i, curr_data] += train_features[real_i][1]



		self.token_gen_table = np.zeros((len(self.vocab), 2))					# this matrix shows amount of appearances for each band name in all users of specific gender
		self.token_gen_table[:,0] = sum(self.token_female_table)
		self.token_gen_table[:,1] = sum(self.token_male_table)


		self.prob_gender = np.zeros(2)
		self.prob_token_gender = np.zeros((len(self.vocab), 2))

		self.prob_gender = self.ndocs/float(sum(self.ndocs))					# training
		self.prob_token_gender[:,0] = (self.token_gen_table[:,0] +0.5)/(sum(self.token_gen_table[:,0]) + 0.5*len(self.vocab))
		self.prob_token_gender[:,1] = (self.token_gen_table[:,1] +0.5)/(sum(self.token_gen_table[:,1]) + 0.5*len(self.vocab))


	def predict(self, test_features):
		result = np.zeros(len(test_features))
		counter = 0
		for i in test_features:

			loc_vocab = i[0]													# array of band names for current user

			score_gen = np.zeros(2)
			for gi in range(2):
				score_gen[gi] += log(self.prob_gender[gi])
				curr_data = [ self.vocab.get(key) for key in loc_vocab if key in self.vocab]
				score_gen_buff = [log(self.prob_token_gender[key, gi]) for key in curr_data]
				score_gen[gi] += sum(score_gen_buff)

			result[counter] = np.argmax(score_gen) + 1
			counter += 1

		return result
