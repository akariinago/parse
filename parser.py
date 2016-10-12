#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Train a shift-reduce parser, parse SDC from command"""
import pickle
import os
import nltk
from nltk.classify import MaxentClassifier
import collections
import time
import sys
import argparse
import MeCab

class Item(object):
    """"Class representing a state of a parser"""
    def __init__(self, stack, queue, pos, features, score, res):
        self.stack = stack
        self.queue = queue
        self.pos = pos
        self.features = features[:]
        self.score = score
        self.res = res[:]

        # Features are constructed in every state
        self.features.append(self.construct_features(pos, stack, queue))

    def construct_features(self, pos, stack, queue):
        """Construct features for current state of the parser
        Keyword arguments:
        phrase -- natural language utterance
        pos -- list of POS tags
        stack -- current state of the parser stack
        queue-- current state of the parser queue
        dag -- current state of the parser DAG
        sequence -- actions taken so far
        """
        features = []

        # Properties of stack top
        if len(stack) != 0 :
            head = stack[-1]
            # HeadがSDCラベルの場合posは多分何もつかない
            features.append("ST_p." + pos[head])
            features.append("ST_w." + head)
            features.append("ST_p_w." + pos[head] + head)

        # If stack is empty
        else:
            features.append("ST_e")

        # Properties of queue head
        if len(queue) != 0 :
            next = queue[0]
            features.append("Q0_p." + pos[next])
            features.append("Q0_w." + next)
            features.append("Q0_p_w." + pos[next] + next)

            # Conjunction of stack top and queue head
            if len(stack) != 0:
                head = stack[-1]
                features.append("ST_p_w_N0_p_w." + pos[head] + head + "_" + pos[next] + next)
                features.append("ST_p_w_N0_w_." + pos[head] + head + "_" + next)
                features.append("ST_p_N0_p."+pos[head] + "_" + pos[next])

        # Properties of next item in queue
        if len(queue) > 1:
            next = queue[1]
            features.append("N1_p." + pos[next])
            features.append("N1_w." + next)
            features.append("N1_p_w." + pos[next] + next)
            features.append("N0_p_N1_p." + pos[queue[0]] + "_" + pos[next])
            if len(queue) > 2:
                features.append("N0_p_N1_p_N2_p."+pos[queue[0]]+"_"+pos[next]+"_"+pos[queue[2]][:-1])

        return features

def shift(item, p, prod):
    """Take shift action as required by the shift-reduce parser
    Keyword arguments:
    item -- current state of the parser
    """
    items = []
    if (q != []) :
        q = item.queue[0]
        s = item.stack[:]
        s.append(q)
    items.append(Item(s, item.queue[1:], item.pos,  item.feature, item.res))
    return items

def reduce(item, p, prod):
    """Take reduce action as required by the shift-reduce parser
    Keyword arguments:
    item -- current state of the parser
    """
    items = []
    ts = ""
    s = item.stack[:]
    if (isAlphabet(s[0]) == False && s[0] != '('):
        while not (isAlphabet(s[0])) :
            ts = s[-1] + ts
            s.pop()
            if (s is None) :
                break
    else :
        if (len(s) > 2) :
            ts = s[-2] + s[-1]
            s.pop()
            s.pop()
        else :
            ts = "X"
    for i in range (0, len(p)) :
        if (ts == prod[i]):
            s.append(p[i])
            res = item.res[:]
            res = make_sdc(res, i)
            items.append(Item(s, item.queue, item.pos,  item.feature, item.res))
            s.pop()
    return items

def shift_reduce(sentence, pos, p, prod, size, dic_data, classify):
    """Perform a shift-reduce parsing of a question using a beam search
    Keyword arguments:
    sentence -- list of words
    pos -- list of POS tags
    weights -- trained models
    size -- size of the beam
    """

    actions = [shift, reduce]
    deque = []

    # Construct the starting item
    start_item = type('TestItem',  (),  {})()
    start_item.queue = range(len(sentence))
    start_item.stack = []
    start_item.features = []
    start_item = shift(start_item)
    start_item.score = 1
    deque.append(start_item)

    result = None
    score = 0
    while deque:
        lst = []
        for item in deque:
            # Perform all possible actions on item taken from agenda
            for i in range(len(actions)):
                new_items = actions[i](item, p, prod)
                for new_item in new_items :
                    if new_item is None:
                        continue
                    new_score = compute_score(new_item, classify, dic_data)
                    new_item.score = new_score

                    # Item is finished; compare it to current candidate
                    s = new_item.stack
                    if s[0] == "E" && len(s) == 1: 
                        if result is None or new_score > score:
                            result = new_item
                            score = new_score
                        else:
                            lst.append(new_item)
        # Only best B items are chosen as the new agenda
        lst.sort(key=lambda x: x.score,  reverse=True)
        deque = lst[:size]
    return result

def isAlphabet(char):
	#引数がアルファベットならTrue,さもなければFalseを返す
	if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
		return True
	return False

def parse(text):
    mecab = MeCab.Tagger() ## MeCabのインスタンス作成
    node = mecab.parseToNode(text) ## 解析を実行
    ips = []
    poses = {}
    while node:
        # surface : 形態素の文字列情報
        # feature : 素性情報
        ips.append(surface)
        poses[surface]=feature
        node = node.next
    return ips, poses

def train(train_data, algorithm, max_iter, dic_data):
    train = []
    for t in train_data:
        dd = dic_data.copy()
        length = len(t)
        #There is a space before label, so it is removed by lstrip().
        label = t[length]
        for token in t[0:length-1]:
            dd[token]=1
        tp = (dd,label) # label shift or reduce1 or reduce2...
        train.append(tp)
    try:
        classifier = nltk.classify.MaxentClassifier.train(train, algorithm, trace=0, max_iter)
    except Exception as e:
        print('Error: %r' % e)
        return
    return classifier

def compute_score(item, classifier, dic_data):
    """Compute score a sample has for certain class
    Keyword arguments:
    features -- feature vector of a sample (list of strings)
    weights -- trained model
    index -- desired class
    """
    new_score = item.score
    dd = dic_data.copy()
    for feat in item.features:
        if feat in dic_data:
            dd[dic_data[feat]] = 1

    featureset = (dd)
    pdist = classifier.prob_classify(featureset)
    """ shift S
        Reduce-O R-O
        
    """
    act_list = []
    b_score = pdist.prob(act_list[0])
    b_action = act_list[0]

    for act in actlist:
        if (pdist.prob(act) > b_score):
            b_score = pdist.prob(act)
            b_action = act
    new_score *= pdist.prob(b_action) * 10
    return Item(s, item.queue, item.pos, item.feature, new_score, item.res)

def make_sdc(res, i):
    if not isAlphabet(prod[i][0]):
        res.append("(" + p[i] + " " + prod[i] + " )")
    else:
        ans.insert(0, "( " + p[i])
        ans.append(" )")
    return res

def output_res(res):
    for r in res:
        sys.stdout.write(r)
    print
    
if __name__ == "__main__":
    # Mode for training a log-linear model
    #[[1:"feature1", 2:"feature2", 3:"feature3"]]
    dic_data = pickle.load(open("dic_data.pickle"))
    #[[feature1, feature2, feature3, feature4, S],[..., R-O],[..., R-L]]
    train_data = pickle.load(open("train_data.pickle"))
    classifier = train(train_data, "iis", 1)

    # Mode for parsing all questions and evaluating model
    sys.stdout.write("Enter Input:")
    input = raw_input()
    phrases, pos = parse(input.encode("utf-8"))
    p, prod = pickle.load(open("rules.pickle"))
    beam_size = 20
    res = shift_reduce(phrases, pos, p, prod, beam_size, classifier, dic_data)
    output_res(res)

