import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import SGDClassifier
from sklearn import cross_validation


def do():  
  f = open('/home/islam/gd/data.txt') #path to file with data

  fb_data = {
    "data": [],
    "target": []
  }

  data = []
  for line in f:
      data = line.split('\t')
      line = line[:-1]
      
      if data[0] == "male":
        fb_data["target"].append(0)
      else: fb_data["target"].append(1)
      
      features = []
      for n in range(5):
        features.append(float(data[n+1]))
        
      fb_data["data"].append(features)
        
  return np.array(fb_data["data"]), np.array(fb_data["target"])
  
#action starts  
x, y = do()

scaler = StandardScaler()
scaler.fit(x)
x = scaler.transform(x)

clf = SGDClassifier(loss="hinge", penalty="l2")

scores = cross_validation.cross_val_score(clf, x, y, cv=5)

print scores.mean()
