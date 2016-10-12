#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import pickle
if __name__ == "__main__":
    args = sys.argv
    f = open(args[2], 'r')

    # make a rule
    if (args[1] == 'r'):
        rules = []
        for line in f:
            itemList = [l.decode('utf-8') for l in line[:-1].split('->')]
            print itemList
            rules.append(itemList)
        f.close()
        pickle.dump(rules, open("rules.pickle", "wb"))
        #rules = pickle.load(open("rules.pickle"))
    
    # make a dic
    if (args[1] == 'd'):
        dic = {}
        num = 1
        for line in f:
        features = line.split(",")
        for feature in features:
            if feature in dic :
                continue
            dic[feature] = num
            num += 1
        pickle.dump(rules, open("dic_data.pickle", "wb"))
