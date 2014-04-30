import tree
from numpy import *

def inte(t):
    return t.__int__()

height = 1000
width = 5

data = random.random((height, width))
'''data2 = zeros((height, width), int)
for row in range(len(data)):
    for col in range(len(data[0])):
        #data2[row][col] = int(round(data[row][col]))
        data2[row][col] = 0
data = data2
print data'''

i = 0
while (i < height):    
    j = 0
    while (j < width):
        data[i][j] = int(round(data[i][j]))
        j += 1    
    i += 1    

i = 0
while (i < height):    
    summ = reduce(lambda x, y: x+y, data[i])    
    data[i][width-1] = summ - data[i][width-1]    
    i += 1    

train = data[:,0:width-1]
target = data[:,width-1:width].ravel()
print data
mytree = tree.Tree()
mytree.fit(train, target)
data2 = random.random((height, width))

i = 0
while (i < height):    
    j = 0
    while (j < width):
        data2[i][j] = int(round(data2[i][j]))
        j += 1    
    i += 1    

i = 0
while (i < height):
    summ = reduce(lambda x, y: x+y, data2[i])    
    data2[i][width-1] = summ - data2[i][width-1]    
    i += 1    

train2 = data2[:,0:width-1]
target2 = data2[:,width-1:width].ravel()


res = mytree.predict(train2)
print res
print target2
print mean((res - target2)**2)