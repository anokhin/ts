#!/usr/bin/python2

from user import User
import scripts
import learning
import sklearn.svm
import sys
import numpy as np
from GDAlgorithm import GDAlgorithm
from dtalgorithm import DTAlgorithm
from nbalgorithm import NBAlgorithm
from mixclassifier import MixClassifier

def save_all_data_to_file(filename = 'data.json'):
  params = scripts.load_params()
  user = User(params['token'])
  my_uid = params['my_uid']
  data = user.walk(my_uid)
  scripts.save_data(data, filename)


def main():
  #save_all_data_to_file('koltsov.json')
  data = scripts.load_data('all_data.json')
  clf_svm = sklearn.svm.LinearSVC(dual = False)
  clf_nb = NBAlgorithm()
  clf_dt = DTAlgorithm(impurity_type='entropy', percent_threshold=1, max_depth=20)
  clf_gd = GDAlgorithm()
  clf_mix = MixClassifier()
  clf_mix.add(clf_svm, learning.getSVMfeatures)
  clf_mix.add(clf_nb, learning.getNBfeatures)
  clf_mix.add(clf_dt, learning.getDTfeatures)
  clf_mix.add(clf_gd, learning.getGDfeatures)

  svm_scores = learning.score_model(clf_svm, learning.getSVMfeatures, data)
  print 'SVM only:', svm_scores
  learning.print_normal_scores(svm_scores)

  nb_scores = learning.score_model(clf_nb, learning.getNBfeatures, data)
  print 'NB only:', nb_scores
  learning.print_normal_scores(nb_scores)

  dt_scores = learning.score_model(clf_dt, learning.getDTfeatures, data)
  print 'DT only:', dt_scores
  learning.print_normal_scores(dt_scores)

  gd_scores = learning.score_model(clf_gd, learning.getGDfeatures, data)
  print 'GD only:', gd_scores
  learning.print_normal_scores(gd_scores)

  total_scores = clf_mix.score_model(data)
  print 'Mixed results:', total_scores
  learning.print_normal_scores(total_scores)

if __name__ == '__main__':
  main()
