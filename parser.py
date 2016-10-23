#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Train a shift-reduce parser, parse SDC from command"""
import argparse
import codecs
import collections
from itertools import chain
import MeCab
import mojimoji
import nltk
from nltk.classify import MaxentClassifier
import os
import pickle
import pycrfsuite
import sklearn
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer
import sys
import time

class CorpusReader(object):

    def __init__(self, path):
        with codecs.open(path, encoding='utf-8') as f:
            sent = []
            sents = []
            for line in f:
                if line == '\n':
                    sents.append(sent)
                    sent = []
                    continue
                morph_info = line.strip().split('\t')
                sent.append(morph_info)
        train_num = int(len(sents) * 0.9)
        self.__train_sents = sents[:train_num]
        self.__test_sents = sents[train_num:]

    def iob_sents(self, name):
        if name == 'train':
            return self.__train_sents
        elif name == 'test':
            return self.__test_sents
        else:
            return None
def is_hiragana(ch):
    return 0x3040 <= ord(ch) <= 0x309F

def is_katakana(ch):
    return 0x30A0 <= ord(ch) <= 0x30FF

def get_character_type(ch):
    if ch.isspace():
        return 'ZSPACE'
    elif ch.isdigit():
        return 'ZDIGIT'
    elif ch.islower():
        return 'ZLLET'
    elif ch.isupper():
        return 'ZULET'
    elif is_hiragana(ch):
        return 'HIRAG'
    elif is_katakana(ch):
        return 'KATAK'
    else:
        return 'OTHER'

def get_character_types(string):
    character_types = map(get_character_type, string)
    character_types_str = '-'.join(sorted(set(character_types)))

    return character_types_str

def extract_pos_with_subtype(morph):
    idx = morph.index('*')

    return '-'.join(morph[1:idx])
def word2features(sent, i):
    word = sent[i][0]
    chtype = get_character_types(sent[i][0])
    postag = extract_pos_with_subtype(sent[i])
    features = [
        'bias',
        'word=' + word,
        'type=' + chtype,
        'postag=' + postag,
    ]
    if i >= 2:
        word2 = sent[i-2][0]
        chtype2 = get_character_types(sent[i-2][0])
        postag2 = extract_pos_with_subtype(sent[i-2])
        iobtag2 = sent[i-2][-1]
        features.extend([
            '-2:word=' + word2,
            '-2:type=' + chtype2,
            '-2:postag=' + postag2,
            '-2:iobtag=' + iobtag2,
        ])
    else:
        features.append('BOS')

    if i >= 1:
        word1 = sent[i-1][0]
        chtype1 = get_character_types(sent[i-1][0])
        postag1 = extract_pos_with_subtype(sent[i-1])
        iobtag1 = sent[i-1][-1]
        features.extend([
            '-1:word=' + word1,
            '-1:type=' + chtype1,
            '-1:postag=' + postag1,
            '-1:iobtag=' + iobtag1,
        ])
    else:
        features.append('BOS')

    if i < len(sent)-1:
        word1 = sent[i+1][0]
        chtype1 = get_character_types(sent[i+1][0])
        postag1 = extract_pos_with_subtype(sent[i+1])
        features.extend([
            '+1:word=' + word1,
            '+1:type=' + chtype1,
            '+1:postag=' + postag1,
        ])
    else:
        features.append('EOS')

    if i < len(sent)-2:
        word2 = sent[i+2][0]
        chtype2 = get_character_types(sent[i+2][0])
        postag2 = extract_pos_with_subtype(sent[i+2])
        features.extend([
            '+2:word=' + word2,
            '+2:type=' + chtype2,
            '+2:postag=' + postag2,
        ])
    else:
        features.append('EOS')

    return features


def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def sent2labels(sent):
    return [morph[-1] for morph in sent]


def sent2tokens(sent):
    return [morph[0] for morph in sent]

def bio_classification_report(y_true, y_pred):
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(list(chain.from_iterable(y_true)))
    y_pred_combined = lb.transform(list(chain.from_iterable(y_pred)))

    tagset = set(lb.classes_) - {'O'}
    tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {cls: idx for idx, cls in enumerate(lb.classes_)}

    return classification_report(
        y_true_combined,
        y_pred_combined,
        labels = [class_indices[cls] for cls in tagset],
        target_names = tagset,
    )

class grammer:
    def __init__(self):
        self.p = []
        self.prod = []

class Item(object):
    """"Class representing a state of a parser"""
    def __init__(self, stack, queue, pos, features, score, res):
        self.stack = stack[:]
        self.queue = queue[:]
        self.pos = pos
        self.score = score
        self.res = res[:]
        self.features = features[:]
        self.features.append(self.construct_features(pos, stack, queue))
        # Features are constructed in every state
        #self.features.append(self.construct_features(pos, stack, queue))

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
            if (pos.get(head)): 
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
            if (pos.get(next)):
                features.append("Q0_p." + pos[next])
                features.append("Q0_w." + next)
                features.append("Q0_p_w." + pos[next] + next)

                # Conjunction of stack top and queue head
                if len(stack) != 0:
                    head = stack[-1]
                    if (pos.get(head)):
                        features.append("ST_p_w_Q0_p_w." + pos[head] + head + "_" + pos[next] + next)
                        features.append("ST_p_w_Q0_w_." + pos[head] + head + "_" + next)
                        features.append("ST_p_Q0_p."+pos[head] + "_" + pos[next])

        # Properties of next item in queue
        if len(queue) > 1:
            next = queue[1]
            if (pos.get(next)):
                features.append("Q1_p." + pos[next])
                features.append("Q1_w." + next)
                features.append("Q1_p_w." + pos[next] + next)
                features.append("Q0_p_Q1_p." + pos[queue[0]] + "_" + pos[next])
                if len(queue) > 2:
                    features.append("Q0_p_Q1_p_Q2_p."+pos[queue[0]]+"_"+pos[next]+"_"+pos[queue[2]])

        return features

def shift(item, p, prod):
    """Take shift action as required by the shift-reduce parser
    Keyword arguments:
    item -- current state of the parser
    """
    items = []
    if (item.queue != []) :
        q = item.queue[0]
        s = item.stack[:]
        s.append(q)
        items.append(Item(s, item.queue[1:], item.pos, item.features, item.score, item.res)) 
    else :
        items.append(Item([], [], item.pos, item.features, item.score, item.res))
    return items

def reduce(item, p, prod):
    """Take reduce action as required by the shift-reduce parser
    Keyword arguments:
    item -- current state of the parser
    """
    items = []
    ts = ""
    s = item.stack[:]
    item0 = item
    if (isAlphabet(s[-1]) == False and s[-1][-1] != ')'):
        i = len(s) - 1
        while (isAlphabet(s[i]) ==False and s[i][-1] != ')') :
            ts = s[-1] + ts
            s.pop()
            i -= 1
            if (i < 0) :
                break
    else :
        if (len(s) > 1) :
            ts = s[-2] + s[-1]
            s.pop()
            s.pop()
        else :
            ts = "X"
    flag = 0

    for i in range (0, len(p)) :
        if (ts == prod[i]):
            flag = 1
            s.append(p[i])
            res = make_sdc(item.res, i)
            
            items.append(Item(s, item.queue, item.pos,  item.features, item.score, res))
            s.pop()
            item.res.pop()
    if flag == 0:
        items.append(Item([], item.queue, item.pos, item.features, item.score, item.res))
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
    start_item.queue = sentence
    start_item.stack = []
    start_item.features = []
    start_item.pos = pos
    start_item.score = 1
    start_item.flag = 0
    start_item.res = []
    start_item = shift(start_item, p, prod)[0]
    deque.append(start_item)

    result = None
    score = 0
    candidate_lst = []
    while deque:
        lst = []
        for item in deque:
            # Perform all possible actions on item taken from agenda
            for i in range(len(actions)):
                new_items = actions[i](item, p, prod)
                if (len(new_items) != 0):
                    for new_item in new_items :
                        if new_item.stack == []:
                            continue
                        new_score = compute_score(new_item, dic_data, classify)
                        new_item.score = new_score

                        # Item is finished; compare it to current candidate
                        if new_item.stack[0] == "E" and len(new_item.stack) == 1: 
                            #print "finish!"
                            if result is None or new_score > score:
                                result = new_item
                                score = new_score
                                #print result.res
                        else:
                            lst.append(new_item)
                            if (new_item.queue == []):
                                candidate_lst.append(new_item)
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
    node = node.next
    while node:
        # surface : 形態素の文字列情報
        # feature : 素性情報
        ips.append(node.surface)
        poses[node.surface]=node.feature.split(",")[0]
        node = node.next
    ips.pop()
    return ips, poses

def make_dinitial():
    dinitial={}
    # The number of features is 4627.
    #for i in range(1,4628):
    for i in range(1,5):
    #for i in range(1,56):
        if not i in dinitial:
            dinitial[str(i)] = int()
            dinitial[str(i)] = 0
    return dinitial

def train(train_data, algorithm, max_iter, dic_data):
    train = []
    dinitial = make_dinitial()
    for t in train_data:
        dd = dinitial.copy()
        length = len(t)
        #There is a space before label, so it is removed by lstrip().
        label = t[-1]
        for token in t[0:-2]:
            dd[token]=1
        tp = (dd,label) # label shift or reduce1 or reduce2...
        train.append(tp)
    try:
        classifier = nltk.classify.MaxentClassifier.train(train, algorithm, trace=0, max_iter=1)
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
    dinitial = make_dinitial()
    new_score = item.score
    dd = dinitial.copy()
    #print item.stack
    for feature in item.features:
        for feat in feature:
            if feat in dic_data:
                #print feat
                dd[dic_data[feat]] = 1

    featureset = (dd)
    pdist = classifier.prob_classify(featureset)
    
    """ shift S
        Reduce-O R-O
    """

    act_list = ["S", "R-O", "R-L", "R-(O\L)", "R-O\(O/O)", "R-L\(O/O)", "R-(O/O)", "R-(L\E)",  "R-(O\E)"]
    b_score = pdist.prob(act_list[0])
    b_action = act_list[0]

    for act in act_list:
        if (pdist.prob(act) > b_score):
            b_score = pdist.prob(act)
            b_action = act
    new_score *= (pdist.prob(b_action) * 10.0)
    return new_score

def make_sdc(res, i):
    #print p[i],prod[i]
    if isAlphabet(prod[i][0]) == False and prod[i][0] != "(" :
        res.append("(" + p[i] + " " + prod[i] + " )")
    else:
        res.insert(0, "( " + p[i])
        res.append(" )")
    return res

def output_res(res):
    for r in res:
        sys.stdout.write(r)
    print

def analyse(text):
    list = []
    mecab = MeCab.Tagger() ## MeCabのインスタンス作成
    node = mecab.parseToNode(text) ## 解析を実行
    while node:
        # surface : 形態素の文字列情報
        # feature : 素性情報
        
        """
        #そのまま出力
        print node.surface, node.feature
        
        """
        sub_list = []
        if (node.feature.split(",")[0]!="BOS/EOS"):
            sub_list.append(node.surface)
            for i in range(0,9):
                sub_list.append(node.feature.split(",")[i])
            list.append(sub_list)
        node = node.next
    return list
    
def predict_word(input):
    c = CorpusReader("corpus.txt")
    train_sents = c.iob_sents('train')
    test_sents = c.iob_sents('test')

    # 文からの素性抽出
    X_train = [sent2features(s) for s in train_sents]
    y_train = [sent2labels(s) for s in train_sents]
    
    X_test = [sent2features(s) for s in test_sents]
    y_test = [sent2labels(s) for s in test_sents]
    
    # モデルの学習
    trainer = pycrfsuite.Trainer(verbose=False)

    for xseq, yseq in zip(X_train, y_train):
        trainer.append(xseq, yseq)

    trainer.set_params({
        'c1': 1.0,   # coefficient for L1 penalty
        'c2': 1e-3,  # coefficient for L2 penalty
        'max_iterations': 50,  # stop earlier
        
        # include transitions that are possible, but not observed
        'feature.possible_transitions': True
    })
        
    trainer.train('model.crfsuite')
    
    # 未知語の予測
    tagger = pycrfsuite.Tagger()
    tagger.open('model.crfsuite')
    
    example_sent = analyse(input)
    print(' '.join(sent2tokens(example_sent)))
    labels = tagger.tag(sent2features(example_sent))
    words = sent2tokens(example_sent)
    pretag = ""
    unknown_word = ""

    for j in range(2,len(list(labels[0]))):
        pretag += list(labels[0])[j]
    unknown_word += words[0]
    i = 1
    for label in labels[1:]:
        label_list = list(label)
        tag = ""
        for j in range(2,len(label_list)):
            tag += label_list[j]
        if(pretag != tag or i == len(labels)):
            flag = 0
            for k in range(0, len(p)):
                gpr = ""
                for l in range(0, len(prod)):
                    gpr += prod[l]
                if unknown_word == gpr:
                    flag = 1 
            if flag == 0:
                print pretag, unknown_word
                p.append(pretag)
                prod.append(unknown_word)
            pretag = tag
            unknown_word = words[i]
        else:
            unknown_word += words[i]
        i += 1
            
    print("Predicted:", ' '.join(tagger.tag(sent2features(example_sent))))
    return p, prod

if __name__ == "__main__":
    # Mode for training a log-linear model
    #[[1:"feature1", 2:"feature2", 3:"feature3"]]
    dic_data = pickle.load(open("dic_data.pickle"))
    #[[1, 2, 3, 4, S],[..., R-O],[..., R-L]]
    train_data = pickle.load(open("train_data.pickle"))
    classifier = train(train_data, "iis", 1, dic_data)

    # Mode for parsing all questions and evaluating model
    sys.stdout.write("Enter Input:")
    input = raw_input()
    phrases, pos = parse(input)
    p, prod = pickle.load(open("rules.pickle"))

    #未知語の追加
    p, prod = predict_word(input)

    beam_size = 20
    res = shift_reduce(phrases, pos, p, prod, beam_size, classifier, dic_data)

    #SDCが作られなかった場合未知語の処理をする
    if (res is None):
        print "Not_found"
    else:
        output_res(res.res)
