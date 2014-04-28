import json
import random
import numpy as np

class Person(dict): #that is a simple dictionary
  def __hash__(self):
    return int(self['info']['uid'])
  def __eq__(self, ob):
    return self['info']['uid'] == ob['info']['uid']

# primary scticture which contains all data for each user and is saved to file
def create_dict(women = [], men = []):
  d = { '1': women,  #list of create_person() objects (female)
        '2': men   #list of create_person() objects (male)
      }
  return d


def create_person():
  d = Person([('info', {'first_name': '',
                        'last_name': '',
                        'sex': '',
                        'uid': ''}),
              ('subscripts', []),  #list of dictionaries with keys (from API):
                                  #'gid', 'name', 'type', 'is_closed', 'screen_name'
              ('audio', []),    #list of artists
              ('wall', []),     #list of dictionaries with keys (from API request):
                                  #'likes', 'text', 'comments', 'post_type',
                                  #'date', 'reports'
              ('friends', []),  #list of dictionaries with keys (from API):
                                  #'sex', 'uid'
              ('albums', [])    #list of create_album() objects
              ])
  return d


def create_album(aid = '', photos = []):
  d = { 'album_id': aid,
        'photos': photos  #list of dictionaries with keys (from API request):
                            #'created', 'pid', 'likes', 'comments', 'text'
      }
  return d


#merge two data pieces
def merge_data(*args):
  d = create_dict()
  s1 = set()
  s2 = set()
  for d_i in args:
    for person in d_i['1']:
      s1.add(Person(person))
    for person in d_i['2']:
      s2.add(Person(person))
  d['1'] = list(s1)
  d['2'] = list(s2)
  return d


def convert_data(d):
  data = d['1'] + d['2']
  labels = ['1'] * len(d['1']) + ['2'] * len(d['2'])
  return (data, labels)


#splitting feature matrix for cross-validation
def split_features(features, labels, nfold = 3):
  zipped = zip(features, labels)
  random.shuffle(zipped)
  features, labels = zip(*zipped)
  features = np.array(list(features))
  labels = list(labels)
  for i in range(nfold):
    low = i * len(labels) / nfold
    high = (i + 1) * len(labels) / nfold
    train_data = np.vstack((features[:low], features[high:]))
    train_labels = np.append(labels[:low], labels[high:])
    test_data = features[low:high]
    test_labels = labels[low:high]
    yield (train_data, train_labels, test_data, test_labels)
#format of (data, labels): tuple(array([[],...]), array([...]))


#splitting dicts for cross-validation
def split_dict(d, nfold = 3):
  data = d['1'] + d['2']
  labels = ['1'] * len(d['1']) + ['2'] * len(d['2'])
  shuf = zip(data, labels)
  random.shuffle(shuf)
  data, labels = zip(*shuf)
  data = list(data)
  labels = list(labels)
  for i in range(nfold):
    low = i * len(data) / nfold
    high = (i + 1) * len(data) / nfold
    train_data = data[:low] + data[high:]
    test_data = data[low:high]
    train_labels = labels[:low] + labels[high:]
    test_labels = labels[low:high]
    yield (train_data, train_labels, test_data, test_labels)
    #format of (data, labels) : tuple([Person, ...], ['1', '2', '1', ...])
  

def load_data(filename = "data.json"):
  f = open(filename, 'r')
  data = json.load(f)
  f.close()
  return data


def save_data(d, filename = "data.json"):
  f = open(filename, 'w')
  json.dump(d, f)
  f.close()


def load_params(filename = 'params.conf'):
  f = open(filename, 'r')
  params = json.load(f)
  f.close()
  return params
