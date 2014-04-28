import scripts
import numpy as np
import time
import re
import nltk
from nltk.corpus import stopwords
import codecs

#estimate model quality
def score_model(clf, extractor, d, nfold = 3):
  (data, labels) = scripts.convert_data(d)
  features = extractor(data)
  labels = np.array(map(lambda x: int(x), labels))
  return cross_val_score(clf, features, labels)


def print_normal_scores(scores):
  precision = scores[0] / (scores[0] + scores[1])
  print 'Precision:', precision
  recall = scores[0] / (scores[0] + scores[2])
  print 'Recall:', recall
  f_score = 2.0 * precision * recall / (precision + recall)
  print 'F_score:', f_score
  print '#' * 40

#cross-validation
def cross_val_score(clf, features, labels, nfold = 3):
  scores = [] #list for classifiers quality metrics
  for (train_features, train_labels, test_features, gt) in \
              scripts.split_features(features, labels, nfold):
    clf.fit(train_features, train_labels)
    predicted_labels = clf.predict(test_features)
    #gt contains ground truth labels (1 or 2)
    summ = predicted_labels + gt
    diff = predicted_labels - gt
    TP = float(summ[summ > 3.5].size)
    TN = float(summ[summ < 2.5].size)
    FP = float(diff[diff > 0.5].size)
    FN = float(diff[diff < -0.5].size)
    p1 = float(summ[summ < 2.5].size) / gt[gt < 1.5].size
    p2 = float(summ[summ > 3.5].size) / gt[gt > 1.5].size
    p1 = TN / (TN + FP)
    p2 = TP / (TP + FN)
    f1_score = abs(p1 + p2 - 1) #our specific metric
    scores.append([TP, FP, FN, TN, f1_score])
  scores = np.array(scores)
  if len(scores) > 0:
    return sum(scores) / len(scores)
  return [0.0, 0.0, 0.0, 0.0, 0.0]


##################################
# data is list of Person objects
# output values are numpy matrices

def getSVMfeatures(data): #svm
  feature_matrix = [] #output matrix
  men_count = []
  women_count = []
  audio_count = []
  friends_count = []
  groups_count = []
  for person in data:
    feature_vector = []
    friends = person['friends']
    if len(friends) == 0:
      continue
    #getting some counters
    men_count.append(len(filter(lambda x: x['sex'] == 2, friends)))
    women_count.append(len(friends) - men_count[-1])
    audio_count.append(len(person['audio']))
    friends_count.append(len(person['friends']))
    groups_count.append(len(person['subscripts']))
    feature_vector.extend([women_count[-1] / float(men_count[-1]),
      audio_count[-1], groups_count[-1], friends_count[-1]])
    feature_matrix.append(feature_vector)
  bad_friends = len(data) - len(men_count)
  mean_men = sum(men_count) / float(len(men_count))
  mean_women = sum(women_count) / float(len(women_count))
  mean_groups = sum(groups_count) / float(len(groups_count))
  mean_audio = sum(audio_count) / float(len(audio_count))
  mean_friends = sum(friends_count) / float(len(friends_count))
  for i in range(bad_friends):
    feature_matrix.append([mean_women / mean_men, mean_audio,
          mean_groups, mean_friends])
  return np.array(feature_matrix)




##################################
# data is list of Person objects
# output is list of items of next structure:
# [np.array of band names, np.array of amounts of appearances]


def getNBfeatures(train_data): #naive Bayes
  n_users = len(train_data)

  result = []

  for i in range(n_users):                                            # creating of data stucture for each user
    buff_vocab = []
    buff_result_tokens = np.array([], dtype='|S5')
    buff_result_amount = np.array([])

    for g in train_data[i]["audio"]:                                  # normalization

      g = g.lower()
      g = re.sub(unicode(" "+unicode(stopwords.words('russian')[0]+" ", "UTF-8")), "", g, flags=re.U)
      g = re.sub(ur"the ", "", g)
      g = re.sub(ur"\W", "", g, flags=re.U)

      if ( g not in buff_vocab ):
        buff_vocab.append(g)
        buff_result_tokens = np.append(buff_result_tokens, g.encode("UTF-8"))
        buff_result_amount = np.append(buff_result_amount, np.zeros((1)))

      buff_result_amount[buff_vocab.index(g)] += 1

    buff_result = [buff_result_tokens, buff_result_amount]
    result.append(buff_result)

  return result


def getDTfeatures(data): #decision tree
    features = []
    for person in data:
        # features for person
        pfeatures = []

        # percent of male friends
        mfr = 0
        for friend in person[u'friends']:
            if friend[u'sex'] == 2:
                mfr += 1
        pfeatures.append(int(100 * float(mfr) / len(person[u'friends']) if len(person[u'friends']) else 0))

        # sum of likes, comments, reposts on a wall
        likes, comments, reposts = 0, 0, 0
        for post in person['wall']:
            likes += post[u'likes'][u'count']
            comments += post[u'comments'][u'count']
            reposts += post[u'reposts'][u'count']
        lw = len(person['wall'])
        pfeatures.append(int(likes / (float(lw) if lw else 1)))
        pfeatures.append(comments)
        pfeatures.append(reposts)

        # number of songs
        artists = set(person[u'audio'])
        pfeatures.append(len(artists))
        pfeatures.append(max([person['audio'].count(s) for s in artists]) if len(artists) else 0)

        # number of groups
        subs = len(person[u'subscripts'])
        pfeatures.append(subs)

        #some magic
        pfeatures.append(int(pfeatures[-2] / float(subs if subs else 1)))

        # number of friends
        pfeatures.append(int(len(person[u'friends']) / (float(subs) if subs else 1)))

        # number of albums and photos per album
        photos = 0
        la = len(person[u'albums'])
        for album in person[u'albums']:
            photos += len(album[u'photos'])
        pfeatures.append(len(person[u'albums']))
        pfeatures.append(int(float(photos) / (la if la else 1)))

        features.append(pfeatures)
    return np.array(features)


def getGDfeatures(data): #gradient descent
  groups = [[group_name[u'screen_name'] for group_name in friend['subscripts']] for friend in data]
  group_matrix = []
  header = set()
  for friend in data:
      header |= set([ group_name[u'screen_name'] for group_name in friend['subscripts'] ])
  header = list(header) #list of all_friend's subscriptions
  d = {key:i for i, key in enumerate(header)}
  h_len = len(header)
  for k in range(len(groups)):
    friend_groups = np.zeros(h_len)
    indices = [d[group_name] for group_name in groups[k]]
    friend_groups[indices] = 1
    group_matrix.append([header, friend_groups, np.array([len(data[k]['info']['first_name']) / float(len(data[k]['info']['last_name']))]) ])
  return group_matrix   #list, each element: [header,0 & 1 numpy vector, number]
