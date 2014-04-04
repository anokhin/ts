from nb import myNBclassifier
model = myNBclassifier()
import numpy as np
model.fit(np.array([['a','b','a'],['ba','ba','ba'],['b','c','c']]), np.array([1,2,1]))
print model.predict(np.array(['b','a','c']))
print model.predict_proba(np.array(['b','a','c']))
print model.score(np.array([['a','b','a'],['ba','ba','ba'],['b','c','c']]), np.array([1,2,1]))
