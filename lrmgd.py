import numpy
import argparse
from sklearn import cross_validation

class FriendsPredictor(object):
    """
    Model used to predict age of users in VK
    """
    a = []
    @staticmethod
    def gradient_descent(x, y, a=numpy.array([]), step0=1000.0):
        def gradJ(a, x, y):
            res = []
            tmp = []
            for j in range(0, len(x)):
                s = 0
                for i in range(0, len(x[j])):
                    s += x[j][i]*a[i];
                tmp.append(s - y[j])

            for i in range(0, len(a)):
                s = 0
                for j in range(0, len(x)):
                    s += 2*x[j][i]*tmp[j]
                res.append(s)
            return numpy.array(res)

        if(len(a) == 0):
            a = numpy.array([1.0]*len(x[0]))
        else:
            a = numpy.array(a)
        step = step0
        v = 1.0
        while v > 0.00001:
            da = gradJ(a, x, y)
            #da = da/numpy.sqrt(numpy.sqrt(numpy.dot(da, da)))
            v = step
            vlen = numpy.dot(da, da)
            if(vlen > 0.00001):
                da = da/numpy.sqrt(vlen)

            #print(str(a)+ str(da)+ str(step)+" v:"+ str(v))
            a = a - da*numpy.sqrt(step)
            #if(numpy.dot(da, daold)<0):
            step /= 1.02
        return a


    def predict(self, X):
        res = []
        for x in X:
            res.append(numpy.dot(self.a, x))
        return res

    def fit(self, X, y):
        self.a = self.gradient_descent(X, y)
        self.a = self.gradient_descent(X, y, self.a, 10)
    def get_params(self, deep = True):
        return {}
    def score(self, X, y):
        y_pred = numpy.array(self.predict(X))
        y_pred = y_pred - numpy.array(y)
        return numpy.sqrt(numpy.dot(y_pred, y_pred)/len(y_pred))
def readCSV(fname):
    f = open(fname, "r")
    x = []
    y = []
    line=f.readline();
    while(line and len(line) > 1):
        try:
            tk = line.split(',')
            x.append([float(tk[3]),float(tk[4]),float(tk[6]), float(tk[7]), float(tk[8]), 1.0])
            y.append(float(tk[-1]))
        except:
            print(line)
        line=f.readline()
    f.close()
    return x, y
def friends(flearn, ftest):
    f = open(flearn, "r")
    x, y = readCSV(flearn)
    #print(str(x))
    est = FriendsPredictor()
    est.fit(x, y)

    f = open(ftest, "r")
    line=f.readline();
    sumsq = 0
    i = 0
    print("Prediction:\n")
    while(line and len(line) > 1):
        try:
            tk = line.split(',')
            t = numpy.array([float(tk[3]),float(tk[4]),float(tk[6]), float(tk[7]), float(tk[8]), 1.0])
            print(str([float(tk[-1]), est.predict([t])]))
            sumsq = sumsq + (float(tk[-1])-est.predict([t])[0])**2
            i = i + 1
        except:
            print(line)
        line=f.readline()
    print(str(est.a))
    print("Standard deviation: " + str(numpy.sqrt(sumsq/i)))
    f.close()
def crossVal(fname):
    x, yl = readCSV(fname)
    scores = cross_validation.cross_val_score(FriendsPredictor(), x, numpy.array(yl), cv=5)
    print("Standard deviation: " + str(sum(scores)/len(scores)))

def parse_args():
    parser = argparse.ArgumentParser(description='Linear regression method of gradient descent\nFinding number of friends')
    parser.add_argument('learn_path', nargs=1)
    parser.add_argument('test_path', nargs=1)
    return parser.parse_args()

def main():
    args = parse_args()
    if args.learn_path[0] == 'cross-val':
        crossVal(args.test_path[0])
    else:
        friends(args.learn_path[0], args.test_path[0])

if __name__ == "__main__":
    main()