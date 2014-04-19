import sklearn.svm
import numpy
import argparse
from math import sqrt
import pylab as pl
import numpy as np
import os


def parse_file(file):
	f = open(file, 'r+')
	samples = [(line[-1] == '\n' and line[:-1] or line).decode('utf-8').split('\t') for line in f if line[0] != '#']
	features = [[int(feature) for feature in sample[1:]] for sample in samples]
	classes = [(sample[0] == u"male" and 1 or -1) for sample in samples]
	return features, classes

def cut_samples(features, classes):
	cutted = [elem for elem in zip(features, classes) if sum(elem[0]) != 0]
	return [elem[0] for elem in cutted], [elem[1] for elem in cutted]
	
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
	parser.add_argument('-outfile', metavar='OUT', type=str, default="data_report.txt", help='output file for report')
	return parser.parse_args()

def create_gistogram(features, classes):
	gistogram = [{} for i in range(len(features[0]))]
	for sample, cls in zip(features, classes):
		for i, feature in enumerate(sample):
			if gistogram[i].has_key(feature):
				gistogram[i][feature][cls] += 1
			else:
				gistogram[i][feature] = {cls:1, -cls:0}
	return gistogram
				
	
def save_plots(gistogram):
	titles = [
			"Favorite athletes",
			"Favorite teams",
			"Inspirational people",
			"Albums",
			"Books",
			"Movies",
			"Groups",
			"Statuses"]
			
	if not os.path.exists("figs"):
		os.makedirs("figs")
			
	for i, d in enumerate(gistogram):
		pl.clf()
		X = np.arange(len(d))
		pl.bar(X, [elem[1] for elem in d.values()], align='center', width=0.3, color='b', label='Male')
		pl.bar(X + 0.3, [elem[-1] for elem in d.values()], align='center', width=0.3, color='r', label='Female')
		pl.xticks(X + 0.15, d.keys())
		ymax = max([max(elem[1], elem[-1]) for elem in d.values()]) + 1
		pl.ylim(0, ymax)
		pl.xlabel('Feature')
		pl.ylabel('Quantity')
		pl.title(titles[i])
		pl.legend()
		pl.savefig("figs/" + str(i) + 'fig.png', bbox_inches='tight')
		
def create_gender_pie(male_samples):
	if not os.path.exists("figs"):
		os.makedirs("figs")
	pl.clf()
	pl.pie([male_samples * 100, (1 - male_samples) * 100], labels=['Male', 'Female'], autopct='%1.1f%%', shadow=True, startangle=90)
	pl.title('Gender distribution')
	pl.savefig('figs/gender.png', bbox_inches='tight')
	
		

def main():
	args = parse_args()
	features, classes = get_features(args.input_files)
	total_samples = len(features)
	features, classes = cut_samples(features, classes)
	cutted_samples = len(features)
	male_samples = 1.0 * len([elem for elem in classes if elem == 1]) / cutted_samples
	female_samples = 1 - male_samples
	
	f = open(args.outfile, 'w+')
	f.write("Total samples:\t" + str(total_samples) + "\n")
	f.write("Cutted samples:\t" + str(cutted_samples) + "\n")
	f.write("Male percentage:\t" + str(male_samples) + "\n")
	f.write("Female percentage:\t" + str(female_samples) + "\n")
	f.close()
	
	
	gistogram = create_gistogram(features, classes)
	save_plots(gistogram)
	create_gender_pie(male_samples)
				
	

if __name__ == "__main__":
	main()
