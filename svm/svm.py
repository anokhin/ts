import sklearn.svm
import numpy
import argparse
from math import sqrt

def parse_file(file):
	f = open(file, 'r+')
	samples = [(line[-1] == '\n' and line[:-1] or line).decode('utf-8').split('\t') for line in f if line[0] != '#']
	features = [[int(feature) for feature in sample[1:]] for sample in samples]
	classes = [(sample[0] == u"male" and 1 or -1) for sample in samples]
	return features, classes

def cut_samples(features, classes):
	"""removes zero feature vectors from features.
	returns tuple of features and classes"""
	cutted = [elem for elem in zip(features, classes) if sum(elem[0]) != 0]
	return [elem[0] for elem in cutted], [elem[1] for elem in cutted]
	
def get_features(files):
	features = []
	classes = []
	for file in files:
		file_features, file_classes = parse_file(file)
		features.extend(file_features)
		classes.extend(file_classes)
	return cut_samples(features, classes)
	
	
def parse_args():
	parser = argparse.ArgumentParser(description = 'SVM friends gender predictor')
	parser.add_argument('input_files', metavar='IN', type=str, nargs='+', help='input files to use')
	parser.add_argument('-kernel', metavar='K', type=str, default='poly', help='kernel type for svm')
	parser.add_argument('-outfile', metavar='OUT', type=str, default="report.txt", help='output file for report')
	parser.add_argument('-c', metavar='C', type=float, default=0.7, help='penalty parameter C of the error term')
	parser.add_argument('-cvn', metavar='CVN', type=int, default=10, help='number of parts for cross-validation tests')
	parser.add_argument('-degree', metavar='D', type=int, default=3, help="degree of the polynomial kernel function ('poly'), ignored by all other kernels")
	parser.add_argument('--search', action='store_true', help='run in searching best model mode')
	return parser.parse_args()

		
class GenderPredictor(object):
	
	def __init__(self, kernel = 'poly', degree = 3, C = 1.0):
		self.clf = sklearn.svm.SVC(kernel = kernel, degree = degree, C = C)
		
	def fit(self, features, classes):
		self.clf.fit(features, classes)
		
	def predict(self, features):
		return self.clf.predict(features).tolist()
		
	def score(self, real, predicted, silent = False):
		succeed = len([prediction for prediction, clas in zip(predicted, real) if prediction == clas])
		total = len(real)
		accuracy = 1.0 * succeed / total * 100
		if not(silent):
			print("Predicted classes:")
			print(predicted)
			print("Real classes:")
			print(real)
			print("Accuracy: "	+ str(succeed) + " succeed of " + str(total) + " total (" + str(accuracy) + "%)")
		return accuracy

	def split_for_testing(self, features, classes, part, parts):
		tests = len(classes) / parts
		tests_start = tests*part
		tests_end = tests*(part+1)		
		return ({
					"features":features[:tests_start] + features[tests_end:],
					"classes":classes[:tests_start] + classes[tests_end:]
				},
				{
					"features":features[tests_start:tests_end],
					"classes":classes[tests_start:tests_end]
				})
		
		return ({"features":features[tests:], "classes":classes[tests:]},
				{"features":features[:tests], "classes":classes[:tests]})
				
	def cross_validation(self, features, classes, n, silent = False):
		if not(silent):
			print('Amount of objects: ' + str(len(classes)))
		real = []
		predicted = []
		for i in range(n):
			print ("\tstep " + str(i) + " of " + str(n))
			trainers, testers = self.split_for_testing(features, classes, i, n)
			self.fit(trainers["features"], trainers["classes"])
			predictions = self.predict(testers["features"])
			real.extend(testers["classes"])
			predicted.extend(predictions)
		return self.score(real, predicted, silent)

def search_model(features, classes, cvn, outfile):
	results = []
	best = ("", 0, 0)
	for kernel in ['linear', 'rbf', 'sigmoid', 'poly']:
		for C in [0.1, 0.4, 0.7, 1.0, 1.5, 3]:
			print("trying " + kernel + " with C = " + str(C))
			model = GenderPredictor(kernel = kernel, C = C)
			result = (kernel, C, model.cross_validation(features, classes, cvn, silent = True))
			print("Accuracy: " + str(result[2]) + "\n")
			results.append(result)
			if result[2] > best[2]:
				best = result
			if kernel == 'poly':
				print("trying " + kernel + " with C = " + str(C) + " and degree = 5")
				model = GenderPredictor(kernel = kernel, C = C, degree = 5)
				result = (kernel + "5", C, model.cross_validation(features, classes, cvn, silent = True))
				print("Accuracy: " + str(result[2]) + "\n")
				results.append(result)
				if result[2] > best[2]:
					best = result
	
	for result in results:
		print result
	print("___________________________________")
	print("The best result is " + str(best))
	
	f = open(outfile, 'w+')
	for result in results:
		f.write("\t".join([str(elem) for elem in result]) + "\n")
	f.write("\nThe best result is " + str(best))
	f.close()
	
			

def main():
	args = parse_args()
	features, classes = get_features(args.input_files)
	if args.search:
		search_model(features, classes, args.cvn, args.outfile)
	else:
		model = GenderPredictor(kernel = args.kernel, degree = args.degree, C = args.c)
		model.cross_validation(features, classes, args.cvn)
	

if __name__ == "__main__":
	main()
