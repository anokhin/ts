'''
Created on 10.04.2014

@author: archelan
'''
import json
import tree
from numpy import zeros, mean, vstack, hstack
import datetime
import re
import pydot
from sklearn import cross_validation

def quantity(key, data, i, number):
    if (raw_data[t].has_key(key)):
        data[i][number] = len(raw_data[t][key])
    else:
        data[i][number] = 0

if __name__ == '__main__':
    file_path = "users_data_merged.json"
    raw_data = {}    
    jfile = open(file_path, "r")
    raw_data = json.load(jfile)    
    jfile.close()    
    height = len(raw_data)
    width = 5
    data = zeros((height, width))
    target = zeros((height))
    i = 0
    work = {}
    for t in raw_data:        
        #print raw_data[t]
        #data[i][0] = raw_data[t]['birthday']
        if (raw_data[t].has_key('birthday')):
            date_str = raw_data[t]['birthday']
            parts = re.split("[/-]", date_str)
            if len(parts) == 3:
                if date_str.find("/") > 0:
                    date = datetime.date(int(parts[2]), int(parts[0]), int(parts[1]))
                else:
                    date = datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
                years = float((date.today() - date).days / 365.2425)
                if years > 80 or years < 5:
                    continue
                target[i] = years
            else:
                continue
        else:
            continue
        
        if (raw_data[t].has_key('location') and raw_data[t].has_key('hometown')):            
            if (raw_data[t]['location']['id'] == raw_data[t]['hometown']['id']):
                data[i][0] = 0
            else:
                data[i][0] = 1
        else:
            data[i][0] = 1
                    
        quantity('education', data, i, 1)
                        
        #quantity('sports', data, i, 4)
        
        quantity('work', data, i, 2)
        
        
    
        #quantity('languages', data, i, 4)
        
        j = 3
        if (raw_data[t].has_key('relationship_status')):
            a = {"Single": 1,
                 "It's complicated": 2,
                 "In a relationship": 3,
                 "In an open relationship": 4,
                 "Engaged": 5,
                 "In a domestic partnership": 6,
                 "Married": 7,
                 "Widowed": 8}
            if (a.has_key(raw_data[t]['relationship_status'])):
                data[i][j] = a[raw_data[t]['relationship_status']]
            else:
                data[i][j] = 9 #maybe they'll add something new
        else:
            data[i][j] = 0                
        
        if (work.has_key(data[i][0])):
            work[data[i][0]] += 1
        else:
            work[data[i][0]] = 1
          
        ''''j = 4
        if (raw_data[t].has_key('quotes')):
            data[i][j] = 1
        else:
            data[i][j] = 0'''
                 
        i += 1
        
    print work    
    X = data[:i]
    Y = target[:i]
    #print X
    #print Y
    graph = pydot.Dot(graph_type='digraph', rankdir='LR', resolution='200')
    graph.add_node(pydot.Node("0 ht == loc 0, != 2, unknwnn 1\n1 - education quantity\n\
    x - sports quantity\n2 - work quantity\nx - languages quantity\n\
    3 - relationship_status\nx - has_quotes", style="filled", fillcolor="#f6d4a3", shape='note'))    
        
    n = i
    i = 12
    j = 0
    RMSEsum = 0
    MAEsum = 0
    RSEsum = 0
    
    mytree = tree.Tree(graph)
    mytree.fit(X, Y)        
    
    
    
    correlationsum = 0    
    while i < 294:
        mytree = tree.Tree(graph)
        mytree.fit(vstack((X[0:i-11],X[i:n])), hstack((Y[0:i-11],Y[i:n])))        
        res = mytree.predict(X[i-11:i])
        #print res
        #print Y[i-11:i]        
        RMSE = mean((res - Y[i-11:i])**2)**(0.5)
        MAE = mean(abs(res - Y[i-11:i]))
        RSE = sum((res - Y[i-11:i])**2) / sum((Y[i-11:i] - mean(Y[i-11:i]))**2)
        sty = (sum((res - mean(res))*(Y[i-11:i] - mean(Y[i-11:i]))))
        sy = (sum((res - mean(res))**2))**(0.5)
        st = (sum((Y[i-11:i] - mean(Y[i-11:i]))**2))**(0.5)
        correlation = sty / (sy * st)
        #print "RMSE: ", RMSE
        #print "MAE: ", MAE
        #print "RSE: ", RSE
        print "correlation: ", correlation
        RMSEsum += RMSE
        MAEsum += MAE
        RSEsum += RSE
        correlationsum += correlation
        
        j += 1
        i += 11
    print "RMSE final: ", RMSEsum / j
    print "MAE final: ", MAEsum / j
    print "RSE final: ", RSEsum / j
    print "correlation final: ", correlationsum / j
    
    #print (round(elem, 0) for elem in Y.tolist)
    k = 0
    yround = Y.round(0)
    ages = {}
    
    for item in yround:
        if (ages.has_key(item)):
            ages[item] += 1
        else:
            ages[item] = 1
            
    print ages