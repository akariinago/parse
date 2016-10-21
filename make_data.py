#!/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import codecs
import sys
import pickle
import MeCab
import mojimoji

def analyse(text):
    mecab = MeCab.Tagger() ## MeCabのインスタンス作成

    node = mecab.parseToNode(text) ## 解析を実行
    morphs = []
    poses = []
    while node:
        # surface : 形態素の文字列情報
        # feature : 素性情報
        
        """
        #そのまま出力
        print node.surface, node.feature
        
        """
        
        hinsi  = node.feature.split(",")[0]
        hinsi1 = node.feature.split(",")[1]
        genkei = node.feature.split(",")[6]
        #print "[原形]",genkei,"\t","[品詞]",hinsi,"\t","[品詞細分類1]",hinsi1
        poses.append(hinsi)
        if (genkei == "*"):
            morphs.append(node.surface)
        else:
            morphs.append(genkei)
        node = node.next
    poses.pop(0)
    poses.pop()
    morphs.pop(0)
    morphs.pop()
    return morphs, poses

def make_train_data(morph, words, labels, pos):
    features = []
    print morph[0],pos[0]
    j = 0
    for i in range(0, len(morph)):
            
        features.append("ST_p." + pos[i])
        features.append("ST_w." + morph[i])
        features.append("ST_p_w." + pos[i] + morph[i])
        if (i != len(morph) - 1):
            features.append("Q0_p." + pos[i + 1])
            features.append("Q0_w." + morph[i + 1])
            features.append("Q0_p_w." + pos[i + 1] + morph[i + 1])
        
            features.append("ST_p_w_Q0_p_w." + pos[i] + morph[i] + "_" + pos[i + 1] + morph[i + 1])
            features.append("ST_p_w_Q0_w_." + pos[i] + morph[i] +"_" + morph[i + 1])
            features.append("ST_p_Q0_p." + pos[i] + "_" + pos[i + 1])
            
            if (i != len(morph) - 2):
                features.append("Q1_p." + pos[i + 2])
                features.append("Q1_w." + morph[i + 2])
                features.append("Q1_p_w." + pos[i + 2] + morph[i + 2])
                features.append("Q0_p_Q1_p." + pos[i + 1] + "_" + pos[i + 2])
            
                if (i != len(morph) - 3):
                    features.append("Q0_p_Q1_p_Q2_p." + pos[i + 1] + "_" + pos[i + 2] + "_" + pos[i + 3])
        if (words[j] == morph[i]):
            features.append("\tR-" + labels[j] + "\n")
            features.append("ST_p.")
            features.append("ST_w." + labels[j])
            features.append("ST_p_w." + labels[j])
            if (i != len(morph) - 1):
                features.append("ST_p_w_Q0_p_w." + labels[j] + "_" + pos[i + 1] + morph[i + 1])
                features.append("ST_p_w_Q0_w_." + labels[j] + "_" + morph[i + 1])
                features.append("ST_p_Q0_p." + labels[j] + "_" + pos[i + 1])
            j += 1
        features.append("\tS\n")
    return features

def make_feature(morph, words, labels, pos):
    features = []
    print morph[0],pos[0]
    j = 0
    for i in range(0, len(morph)):
            
        features.append("ST_p." + pos[i])
        features.append("ST_w." + morph[i])
        features.append("ST_p_w." + pos[i] + morph[i])
        if (i != len(morph) - 1):
            features.append("Q0_p." + pos[i + 1])
            features.append("Q0_w." + morph[i + 1])
            features.append("Q0_p_w." + pos[i + 1] + morph[i + 1])
        
            features.append("ST_p_w_Q0_p_w." + pos[i] + morph[i] + "_" + pos[i + 1] + morph[i + 1])
            features.append("ST_p_w_Q0_w_." + pos[i] + morph[i] +"_" + morph[i + 1])
            features.append("ST_p_Q0_p." + pos[i] + "_" + pos[i + 1])
            
            if (i != len(morph) - 2):
                features.append("Q1_p." + pos[i + 2])
                features.append("Q1_w." + morph[i + 2])
                features.append("Q1_p_w." + pos[i + 2] + morph[i + 2])
                features.append("Q0_p_Q1_p." + pos[i + 1] + "_" + pos[i + 2])
            
                if (i != len(morph) - 3):
                    features.append("Q0_p_Q1_p_Q2_p." + pos[i + 1] + "_" + pos[i + 2] + "_" + pos[i + 3])
        if (words[j] == morph[i]):
            features.append("\n")
            features.append("ST_p.")
            features.append("ST_w." + labels[j])
            features.append("ST_p_w." + labels[j])
            if (i != len(morph) - 1):
                features.append("ST_p_w_Q0_p_w." + labels[j] + "_" + pos[i + 1] + morph[i + 1])
                features.append("ST_p_w_Q0_w_." + labels[j] + "_" + morph[i + 1])
                features.append("ST_p_Q0_p." + labels[j] + "_" + pos[i + 1])
            j += 1
        features.append("\n")
    return features

def csv_read(filename, encoding):
    """CSV ファイルを文字コードを指定して読み込む
    """
    with open(filename, "rU") as f:
        csvfile = csv.reader(f)
        rows = [[c.decode(encoding) for c in r] for r in csvfile]
    return rows

def rows_read(rows, words, labels, output_file):
    """CSV ファイルを文字コードを指定して読み込む """
    for row in rows:
        morphemes = []
        poses = []
        features = []
        morphemes, poses = analyse(mojimoji.han_to_zen(row[4]).encode("utf-8"))
        features = make_train_data(morphemes, words, labels, poses)
        for feature in features:
            output_file.write(feature+",")

def rows_read2(rows, words, labels, output_file):
    """CSV ファイルを文字コードを指定して読み込む """
    for row in rows:
        morphemes = []
        poses = []
        features = []
        morphemes, poses = analyse(mojimoji.han_to_zen(row[4]).encode("utf-8"))
        features = make_feature(morphemes, words, labels, poses)
        for feature in features:
            output_file.write(feature+",")


def make_labels(f):
    ls = []
    ws = []
    for line in f:
            #line.rstrip('rn')
            labels = line.split(",")
            print labels[1]
            ws.append(labels[0])
            l =labels[1].replace('\n','')
            l =l.replace('\r','')
            ls.append(l)
    return ws, ls

if __name__ == "__main__":
    args = sys.argv
    f = open(args[2], 'r')

    # make a rule
    if (args[1] == 'r'):
        rules = []
        p = []
        prod = []
        for line in f:
            line = line[:-1].split('->')
            p.append(line[0])
            prod.append(line[1])
        print line[0],line[1]
        rules.append(p)
        rules.append(prod)
        f.close()
        pickle.dump(rules, open("rules.pickle", "wb"))
    
    # make a dic
    # fetature1, feature2,feature3
    # → 1,2,3
    if (args[1] == 'd'):
        dic = {}
        num = 1
        for line in f:
            line.rstrip("\n")
            features = line.split(",")
            for feature in features:
                if feature in dic :
                    continue
                dic[feature] = num
                print num, feature
                num += 1
        pickle.dump(dic, open("dic_data.pickle", "wb"))
        
    # make a train data
    # fetature1, feature2,feature3\t0
    # → 1,2,3, 
    if (args[1] == 't'):
        train = []
        dic = pickle.load(open("dic_data.pickle"))
        output_file = open("train_data.txt","w")
        num = 1
        for line in f:
            t = []
            line.rstrip("\n")
            print line
            line = line.split("\t")
            if len(line) != 2:
                continue
            features = line[0]
            action = line[1]
            action = action.replace('\n','')
            action = action.replace('\r','')
            #print features
            #print action
            features = features.split(",")
            for feature in features:
                if feature in dic :
                    t.append(dic[feature])
            t.append(action)
            train.append(t)
            for i in range(0, len(t) - 1):
                output_file.write(str(t[i]) + ',')
            output_file.write(str(t[len(t) - 1]) + '\n')
        pickle.dump(train, open("train_data.pickle", "wb"))
        
    if (args[1] == 'f'):
        encoding = 'sjis'
        output_file = open("feature.txt","w")
        # [["に,L"], [""],
        labels_file = open(args[3], 'r')
        words, labels = make_labels(labels_file)
        csv_rows = csv_read(args[2], encoding)
        rows_read2(csv_rows, words, labels, output_file)

    if (args[1] == 'tr'):
        encoding = 'sjis'
        output_file = open("train.txt","w")
        # [["に,L"], [""],
        labels_file = open(args[3], 'r')
        words, labels = make_labels(labels_file)
        csv_rows = csv_read(args[2], encoding)
        rows_read(csv_rows, words, labels, output_file)
