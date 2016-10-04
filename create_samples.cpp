#include <algorithm>
#include<fstream>
#include<iostream>
#include<map>
#include<string>
#include <typeinfo>
#include<vector>
#include<stdio.h>
#include <stdlib.h>
#include<string.h>
#include<mecab.h>

using namespace std;

template <typename List>
void split(const std::string& s, const std::string& delim, List& result) {
  result.clear();
  string::size_type pos = 0;

  while(pos != string::npos ) {
    string::size_type p = s.find(delim, pos); 
    if(p == string::npos) {
      result.push_back(s.substr(pos));
      break;
    } else {
      result.push_back(s.substr(pos, p - pos));
    }
    pos = p + delim.size();
  }
}

map<string, vector<int> > init_weights (map <vector<string>, int > examples, int cl) {
  map <string, vector<int> > weights;
  for (map <vector <string>, int >::iterator it = examples.begin(); it != examples.end(); ++it){
    vector<string> example = it->first;
    for (int i = 0; i < example.size(); i++) {
      string f = example[i];
      if (weights.count(f) == 0){
	vector<int> v;
	weights.insert(make_pair(f, v));
	for (int j = 0; j < cl; j++) {
	  weights[f].push_back(0);
	}
      }
    }
  }
  return weights;
}

vector<int> load_labels (char *c) {
  std::ifstream ifs(c);
  if (ifs.fail()) {
    std::cerr << "Failed" << std::endl;
    exit(1);
  }
  string str;
  getline(ifs,str);
  vector<string> str_labels;
  vector<int> labels;
  split(str,",",str_labels);
  for (int i = 0; i < str_labels.size(); i++) {
    labels.push_back(atoi(str_labels[i].c_str()));
  }
  return labels;
}

vector<vector<string> > load_words (char *c) {
  std::ifstream ifs(c);
  if (ifs.fail()) {
    std::cerr << "Failed" << std::endl;
    exit(1);
  }
  string str;
  vector<vector<string> > words;
  while(getline(ifs,str)) {
    vector<string> word;
    split(str,",",word);
    words.push_back(word);
  }
  return words;
}

void write_weights(map <string, vector<int> > weights, char *c) {
  std::ofstream writing_file(c);
  for (map <string, vector<int> > ::iterator it = weights.begin(); it != weights.end(); ++it) {
    writing_file << it->first;
    vector<int> features = it->second;
    for (int i = 0; i < features.size(); i++) {
      writing_file << "," << features[i];
    }
    writing_file << endl;
  }
}

map <vector<string>, int > make_examples(vector <vector <string> > words, vector<int> labels) {
  map <vector<string>, int > examples;
  for (int i = 0; i < labels.size(); i++) {
    examples.insert(make_pair(words[i], labels[i]));
  }
}

int main(int argc, char *argv[]) {
  char *words_file = argv[1]; 
  char *labels_file = argv[2]; 
  char *sample_file = argv[3]; 
  int cl = 2;
  vector <vector <string> > words = load_words(words_file);
  vector<int> labels = load_labels(labels_file);
  map <vector<string>, int > examples = make_examples(words, labels);
  map <string, vector<int> > empty_weights = init_weights(examples, cl);
  write_weights(empty_weights, sample_file);
  return 0;
}
