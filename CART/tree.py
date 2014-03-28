from numpy import *
import pydot

class Tree:
    def __init__(self):
        None
        
    def fit(self, train, target):
        self.graph = pydot.Dot(graph_type='digraph', rankdir='LR', resolution='200')            
        self.train = train
        self.target = target
        self.root = Node(train, target, 0, None, self.graph)        
        self.root.process()                
        self.graph.add_node(pydot.Node(":Leaf Node", style="filled", fillcolor="#b3f487", shape='note'))
        self.graph.add_node(pydot.Node(":Inner Node", style="filled", fillcolor="#98d1d8", shape='note'))        
        self.graph.write_jpg('example1_graph.jpg')
        
    def predict(self, test):
        result = empty(len(test))
        i = 0                        
        for q in test:             
            result[i] = self.root.predict(q)            
            i += 1            
        return result
        
class Node:
    def __init__(self, train, target, level, parent, graph):
        self.graph = graph
        self.parent = parent
        self.train = train
        self.target = target
        self.level = level
        self.n = len(self.train)        
        self.impurity = self.calculateImpurity()            
    
    def predict(self, test):
        if self.leaf:            
            return self.value
        else:
            if test[self.bestFeature] < self.bestSplitValue:
                return self.nodeL.predict(test)                
            else:
                return self.nodeR.predict(test)                
    
    def process(self):        
        if self.n <= 5 or self.train.shape[1] == 0:
            self.stop()
        else:
            self.split()        
    
    def stop(self):
        self.leaf = True
        self.value = mean(self.target)
        if self.parent is not None:
            exp1 = "N=%d Imp=%f\n X[%d]<=%f" % (self.parent.n, self.parent.impurity, \
                self.parent.bestFeature, self.parent.bestSplitValue) 
            exp2 = "N=%d Imp=%f Value=%f\n" % (self.n, self.impurity, self.value)
            for t in self.target:
                exp2 += str(t) + " "
            self.graph.add_node(pydot.Node(exp1, style="filled", fillcolor="#98d1d8", shape='box'))
            self.graph.add_node(pydot.Node(exp2, style="filled", fillcolor="#b3f487", shape='box'))            
            edge = pydot.Edge(exp1, exp2)
            self.graph.add_edge(edge)
    
    def split(self):
        self.leaf = False                
        bestImpurityDelta = -1
        i = 0       
        while i < self.train.shape[1]:
            #iterating through features            
            feature = self.train[:,i:i+1].ravel()            
            ind = argsort(feature)
            feature = array([feature[k] for k in ind])            
            j = 0
            trainSorted = array([self.train[k] for k in ind])
            while j < self.n:
                #searching for best split
                targetSorted = array([self.target[k] for k in ind])
                nodeL = Node(trainSorted[:j], targetSorted[:j], self.level + 1, self, self.graph)
                nodeR = Node(trainSorted[j:], targetSorted[j:], self.level + 1, self, self.graph)
                impurityDelta = self.impurity - j * nodeL.impurity / self.n   \
                - (self.n - j) * nodeR.impurity / self.n
                if impurityDelta > bestImpurityDelta:
                    bestImpurityDelta = impurityDelta
                    bestNodeL = nodeL
                    bestNodeR = nodeR
                    self.bestSplit = j
                    if j == self.n - 1:
                        self.bestSplitValue = feature[j]
                    else:
                        self.bestSplitValue = (feature[j] + feature[j+1])/2
                    self.bestFeature = i
                j += 1
            i += 1
        self.nodeL, self.nodeR = bestNodeL, bestNodeR 
        if self.parent is not None:
            exp1 = "N=%d Imp=%f\n X[%d]<=%f" % (self.parent.n, self.parent.impurity, \
                self.parent.bestFeature, self.parent.bestSplitValue)            
            exp2 = "N=%d Imp=%f\n X[%d]<=%f" % (self.n, self.impurity, \
                self.bestFeature, self.bestSplitValue)            
            node1 = pydot.Node(exp1, style="filled", fillcolor="#98d1d8", shape='box')
            node2 = pydot.Node(exp2, style="filled", fillcolor="#98d1d8", shape='box')
            self.graph.add_node(node1)
            self.graph.add_node(node2)
            edge = pydot.Edge(node1, node2)
            self.graph.add_edge(edge)
        self.nodeL.process()
        self.nodeR.process()        
            
    def calculateImpurity(self):
        self.impurity = 0.
        if self.n != 0:                      
            mean = self.target.sum()/self.n                           
            for y in self.target:
                self.impurity += (y - mean)**2
        return self.impurity