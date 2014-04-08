"""
An implementation of Stochastic Gradient by Nadezhda Chirkova
"""

import csv
import xlrd
import string
import random
import math
import matplotlib
import pylab
import numpy

PARAMS = 5 #number of params

class classifier():

    def __init__(self):
        self.w = [0 for i in range(PARAMS)]

    @staticmethod
    def DotProduct(x,y):
        dotprod = 0
        for j in range(PARAMS):
            dotprod += x[j]*y[j]
        return dotprod

    def fit(self,x,y):
        lambd = 0.1
        k = 0
        leng = len(x)
        w = [random.uniform(-1/float(2*leng),1/float(2*leng)) for i in range(PARAMS)]
        print w
        Q = 0
        for i in range(leng):
            M = self.DotProduct(x[i],w)
            Q += self.L(M)
        for stepper in range(100):
            k += 1
            l = random.randint(0,leng-1)
            elem = x[l]
            a = self.DotProduct(elem,w)
            M = y[l][0]*a
            epsi = self.L(M)
            mult = self.eta(k)*self.dLda(a,y[l][0])
            grad = [mult*el for el in elem]
            for i in range(PARAMS):
                w[i] = w[i] - grad[i]
            Q = (1 - lambd)*Q + lambd*epsi
            print w
        self.w = w
        return w

    def predict(self,x):
        cl = []
        for item in x:
            if self.DotProduct(item,self.w)>0:
                cl.append(1)
            else:
                cl.append(-1)
        return cl

    @staticmethod
    def norm(a):
        n = 0
        n = 0
        for elem in a:
            n += elem*elem
        n = math.sqrt(n)
        return n

    def dLda(self,a,yi):
        return -2*math.exp(yi*a)*yi/((1+math.exp(yi*a))*(1+math.exp(yi*a)))
        #return -1/float(1+math.exp(-yi*a))*math.exp(-yi*a)*yi

    def L(self,M):
        print M
        return 2/(1+math.exp(M))
        #return math.log(1+math.exp(-M))

    @staticmethod
    def eta(k):
        return 1/(float(k)*float(k))

def main():
    data = open('features3.csv',"r")
    reader = csv.reader(data, dialect = 'excel')
    classes = open('classes3.csv',"r")
    reader2 = csv.reader(classes, dialect = 'excel')

    M = []
    for my in reader:
        x = [float(elem)/100 for elem in my]
        x.insert(0,1)
        M.append(x)


    P = []
    for p in reader2:
        if (p[0] == '1'):
            P.append([1])
        else:
            P.append([-1])

    clf = classifier()

    a = clf.fit(M,P)

if __name__ == "__main__":
    main()



