#-*- coding: utf-8 -*-
from itertools import chain
import pycrfsuite
import sklearn
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer
import sys
import codecs
import MeCab
import mojimoji

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
        list2 = []
        if (node.feature.split(",")[0]!="BOS/EOS"):
            list2.append(node.surface)
            for i in range(0,9):
                list2.append(node.feature.split(",")[i])
            list.append(list2)
        node = node.next
    return list

class grammer:
    def __init__(self):
        self.p = []
        self.prod = []

# 既知語の読み込み
i = 0
ts = []
gs = []
f = open(sys.argv[1],"rb")
for line in f:
    ts = list(line)
    n = 0
    for j in range(0, 256):
        if (ts[j] == "-"):
            n = j
            break
    g = grammer()
    g.p[:n] = ts[n:]
    g.prod = ts[n+2:]
    del  g.prod[len(g.prod)-1]
    gs.append(g)
    i += 1
inputs = list(sys.argv[3])
input = ""
for j in range(0, len(inputs)):
    input += inputs[j]
    for k in range(0, len(gs)):
        gpr = ""
        for l in range(0, len(gs[k].prod)):
            gpr += gs[k].prod[l]
        if input == gpr:
            input = ""
            
if(input!=""):
    # 訓練データの読み込み
    c = CorpusReader(sys.argv[2])
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
    
    example_sent = analyse(sys.argv[3])
    print(' '.join(sent2tokens(example_sent)))
    labels = tagger.tag(sent2features(example_sent))
    words = sent2tokens(example_sent)
    pretag = ""
    unknown_word = ""
    rule_file=open(sys.argv[1],"a+")
    for j in range(2,len(list(labels[0]))):
        pretag += list(labels[0])[j]
    unknown_word += words[0]
    i = 1
    for label in labels[1:]:
        labell = list(label)
        tag = ""
        for j in range(2,len(labell)):
            tag += labell[j]
        if(pretag != tag or i == len(labels)):
            flag = 0
            for k in range(0, len(gs)):
                gpr = ""
                for l in range(0, len(gs[k].prod)):
                    gpr += gs[k].prod[l]
                if unknown_word == gpr:
                    flag = 1 
            if flag == 0:
                rule_file.write(pretag+"->"+unknown_word+"\n")
            pretag = tag
            unknown_word = words[i]
        else:
            unknown_word += words[i]
        i += 1
            
    print("Predicted:", ' '.join(tagger.tag(sent2features(example_sent))))
    #print("Correct:  ", ' '.join(sent2labels(example_sent)))
    
    #y_pred = [tagger.tag(xseq) for xseq in X_test]
    
    #print(bio_classification_report(y_test, y_pred))
