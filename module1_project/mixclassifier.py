import numpy as np
import learning
import scripts

class MixClassifier():
  def __init__(self):
    self.alpha = [] #coeffs for linear combination
    self.classifiers = [] #list of tuples (clf, feature_extractor)


  def add(self, clf, extractor):
    self.classifiers.append((clf, extractor))
    self.alpha.append(0.0)


  def fit(self, data, labels):
    labels = np.array(map(lambda x: int(x), labels))
    features = []
    coef = []
    #cross-validation for every classifier
    for clf, extractor in self.classifiers:
      features.append(extractor(data))
      coef.append(learning.cross_val_score(clf, \
            features[-1], labels)[-1])
    norm = sum(coef)
    self.alpha = map(lambda x: x / norm, coef)
    print 'Alpha:', self.alpha
    #after-validation training
    for (clf,_), x in zip(self.classifiers, features):
      clf.fit(x, labels)
    return self


  def predict(self, data):
    predicted = []
    #prediction of every classifier
    for clf, extractor in self.classifiers:
      features = extractor(data)
      predicted.append(clf.predict(features) - 1)
    #classifiers combining
    weighted = np.array([ np.array(clf_res) * alpha_i for \
            clf_res, alpha_i in zip(predicted, self.alpha) ])
    result = np.round(sum(weighted)).astype(int) + 1
    return result

  
  #cross-validation
  def score_model(self, d, nfold = 3):
    scores = [] #list for classifiers quality metrics
    for i, (train_data, train_labels, test_data, test_labels) in \
                      enumerate(scripts.split_dict(d, nfold)):
      print 'Processing {} of {} (MixClassifier)'.format(i + 1, nfold)
      self.fit(train_data, train_labels)
      predicted_labels = self.predict(test_data)
      #gt contains ground truth labels (1 or 2)
      gt = np.array(map(lambda x: int(x), test_labels))
      summ = predicted_labels + gt
      diff = predicted_labels - gt
      TP = float(summ[summ > 3.5].size)
      TN = float(summ[summ < 2.5].size)
      FP = float(diff[diff > 0.5].size)
      FN = float(diff[diff < -0.5].size)
      scores.append([TP, FP, FN, TN])
    scores = np.array(scores)
    if len(scores) > 0:
      return sum(scores) / len(scores)
    return [0.0, 0.0, 0.0, 0.0]
