from __future__ import division
from collections import defaultdict
from math import log

def train(samples):
	""" gets list: [((feature1, feature2, ...), class_id)] and 
	returns tuple: ({class_id : P (class_id)} , {(class_id, feature) : P (feature | class_id)})"""
	(p_class, p_feat_class) = (defaultdict(lambda:0), defaultdict(lambda:0))
	p_num_class = defaultdict(lambda:0)
	for (feats, class_id) in samples:
		p_class[class_id] += 1			# count classes frequencies
		for feat in feats:
			p_feat_class[class_id, feat] += 1			# count features frequencies
			p_num_class[class_id] +=1

	for (class_id, feat) in p_feat_class:				  # count p(feature|class_id)
		p_feat_class[(class_id, feat)] /= p_num_class[class_id]
	for c in p_class:						# count p(class_id)
		p_class[c] /= len(samples)

	return (p_class, p_feat_class)					  # return P(C) and P(O|C)
		

def classify(classifier, feats):
	""" gets tuple :({class_id : P (class_id)} , {(class_id, feature) : P (feature | class_id)}) and 
	tuple of features :(feature1, feature2...) and
	returns class_id"""
	(p_class, prob) = classifier
	return max(p_class.keys(),				# count argmin(-log(C|O)) to avoid to little numbers in product of probabilities
		key = lambda cl: log(p_class[cl]) + \
			sum(log(prob.get((cl,feat), 10**(-3))) for feat in feats))   #using 10^(-7) to avoid zero's appearance in log
			
def get_features(list_attr):
	"""get features from string"""
	list_lang = list_attr[2] != '[]' and ['lang:%s' % each[2:-1] for each in list_attr[2][1: -1].split(", ")] or [u'lang:None']
	list_like = list_attr[3] != '[]\n' and ['like:%s' % each[2:-1].split('/')[0] for each in list_attr[3][1: -2].split(", ")] or [u'like:None']
	qwe = ['rs:%s' % list_attr[1]]
	qwe.extend(list_like)
	return tuple(qwe)	

def get_pairs(sample):
	"""make tuple of features and class name"""
	return (get_features(sample), sample[0])

def get_test_train(all, size, i):
	"""divide all into test and train lists"""
	test_list = all[size * i: size * (i + 1)]
	train_list = all[: size * i] + all[size * (i + 1) :]
	return train_list, test_list
	
def main():
	samples = (line.decode('utf-8').split(u"\t") for line in open('lera_vanya_oleg_islam.txt', 'r+'))
	all = [get_pairs(string) for string in samples]
	length = len(all)
	#cross validation begins
	size = 10                   #size of segment in cross validation
	n = int(length / size)      #number of segments in cross validation
	if length % size != 0:
		n += 1
	predict_classes = []	
	for i in range(n):
		train_list, test_list = get_test_train(all, size, i)
		model = train(train_list)
		predict_classes.extend([classify(model,each[0]) for each in test_list])
	#cross validation ends	
	print (1.0 *len([i[1] for i,j in zip(all,predict_classes) if i[1] == j])/length)
			
if __name__ == "__main__":
	main()