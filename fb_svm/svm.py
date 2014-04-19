import sklearn.svm
import numpy
import argparse


def parse_file(file):
	f = open(file, 'r+')
	samples = [(line[-1] == '\n' and line[:-1] or line).decode('utf-8').split('\t') for line in f if line[0] != '#']
	features = [[int(feature) for feature in sample[1:]] for sample in samples]
	classes = [(sample[0] == u"male" and 1 or -1) for sample in samples]
	return features, classes

	
def get_features(files):
	features = []
	classes = []
	for file in files:
		file_features, file_classes = parse_file(file)
		features.extend(file_features)
		classes.extend(file_classes)
	return features, classes
	
	
def parse_args():
	parser = argparse.ArgumentParser(description = 'SVM friends gender predictor')
	parser.add_argument('input_files', metavar='IN', type=str, nargs='+', help='input files to use')
	return parser.parse_args()

		
class GenderPredictor(object):
	
	def __init__(self):
		self.clf = sklearn.svm.SVC()
		
	def fit(self, features, classes):
		self.clf.fit(features, classes)
		
	def predict(self, features):
		return self.clf.predict(features).tolist()
		
	def test(self, predictions, classes):
		print("Predicted classes:")
		print(predictions)
		print("Real classes:")
		print(classes)
		succeed = len([prediction for prediction, clas in zip(predictions, classes) if prediction == clas])
		total = len(classes)
		accuracy = 1.0 * succeed / total * 100
		print("Accuracy: "	+ str(succeed) + " succeed of " + str(total) + " total (" + str(accuracy) + "%)")
		return accuracy

	def split_for_testing(self, features, classes):
		print (len(classes))
		tests = len(classes) / 4
		return ({"features":features[tests:], "classes":classes[tests:]},
				{"features":features[:tests], "classes":classes[:tests]})

def main():
	args = parse_args()
	features, classes = get_features(args.input_files)
	model = GenderPredictor()
	trainers, testers = model.split_for_testing(features, classes)
	model.fit(trainers["features"], trainers["classes"])
	predictions = model.predict(testers["features"])
	model.test(predictions, testers["classes"])
	

if __name__ == "__main__":
	main()
