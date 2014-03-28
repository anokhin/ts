import tree
from numpy import *

def inte(t):
    return t.__int__()

#generates table filled with random numbers, having 'width' colums,
#where last one is summ of all previous colums.
heightTrain = 100
heightPredict = 100
width = 5

data = random.random((heightTrain, width))

i = 0
while (i < heightTrain):
    summ = reduce(lambda x, y: x+y, data[i])    
    data[i][width-1] = summ - data[i][width-1]    
    i += 1    

train = data[:,0:width-1]
target = data[:,width-1:width].ravel()

mytree = tree.Tree()
mytree.fit(train, target)
data2 = random.random((heightPredict, width))

i = 0
while (i < heightPredict):
    summ = reduce(lambda x, y: x+y, data2[i])    
    data2[i][width-1] = summ - data2[i][width-1]    
    i += 1    

train2 = data2[:,0:width-1]
target2 = data2[:,width-1:width].ravel()


res = mytree.predict(train2)
print res
print target2
print mean((res - target2)**2)
