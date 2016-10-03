#include <algorithm>
#include <fstream>
#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

int max(vector<int> classes, map<int, int> scores) {
  int c = 0;;
  int max = 0;
  for (int i = 0; i < classes.size(); i++) {
    if (max < scores[i]) {
      c = i;
    }
  }
  return c; 
}

int predict(map<string, vector<int> > weights, vector<string> features, int cl){
  /*Predict best class for a sample
    Keyword arguments:
    weights -- trained model
    features -- feature vector of a sample (list of strings)
    cl -- number of classes*/
  vector<int> classes;
  for (int i = 0; i < cl; i++) {
    classes.push_back(i);
  }
  map<int, int> scores;
  for (int i = 0; i < features.size(); i++) {
    string feat = features[i];
    if (weights.count(feat) == 0) {
      continue;
    }
    vector<int> weight = weights[feat];
    for (int j = 0; j < weight.size(); j++) {
      if (i == 0) {
	scores.insert(make_pair(j, weight[j]));
      } else {
	scores[j] += weight[j];
      }
    }
  }
  return max(classes, scores);
}

map<string, vector<int> > train(int n_iter,map <vector <string>, int > examples, map<string, vector<int> > weights, int cl, int learning_rate) {
  /*Train a model using perceptron algorithm
    Keyword arguments:
    n_iter -- number of iterations to be used
    examples -- set of training samples in (feature vector, label) shape
    weights -- empty weights
    cl -- number of classes
    learning_rate -- value by which the weights should be changed*/

      for (int i = 0; i < n_iter; i++) {
        float err = 0;
        for (map <vector <string>, int >::iterator it = examples.begin(); it != examples.end(); ++it) {
	  vector<string> features = it->first;
	  int t = it->second;
	  int guess = predict(weights, features, cl);
	  if (guess != t){
	    for (int j = 0; j < features.size(); j++) {
	      string f = features[j];
	      weights[f][t] += learning_rate;
	      weights[f][guess] -= learning_rate;
	    }
	    err += 1.0;
	  }
	}
	//mapはshuffleできないのでとりあえず保留
	//shuffle(examples.begin(), examples.end(),ofstram_iterator<int>(cout));
	cout <<  err/examples.size() << endl;
      }
    return weights;
}

map <vector <string>, int > load_examples (char *c) {
  std::ifstream ifs(c);
  if (ifs.fail()) {
    std::cerr << "Failed" << std::endl;
    exit(1);
  } 
  map <vector <string>, int > examples;
  char ts[256];
  vector<string> ip;
  vector<string> es;
  while (ifs.getline(ts,255)) {
    split(ts, ",", ip);
    int s = ip.size();
    for (int i = 0; i < s-1; i++) {
      es.push_back(ip[i]);
    }
    examples.insert(make_pair(es, atoi(ip[s-1].c_str())));
  }
  return examples;
}

map <string, vector<int> > load_empty_weights(char *c) {
  std::ifstream ifs(c);
  if (ifs.fail()) {
    std::cerr << "Failed" << std::endl;
    exit(1);
  }
  map<string, vector<int> > weights;
  char ts[256];
  vector<string> ip;
  vector<int> ws;
  while (ifs.getline(ts,255)) {
    split(ts, ",", ip);
    ws.push_back(atoi(ip[1].c_str()));
    ws.push_back(atoi(ip[2].c_str()));
    weights.insert(make_pair(ip[0], ws));
  }
  return weights;
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

int main(int argc, char *argv[]) {
  char *examples_file = argv[1]; 
  char *weights_file = argv[2]; 
  map <vector <string>, int > examples = load_examples(examples_file);
  map <string, vector<int> > empty_weights = load_empty_weights(weights_file);
  int n_iter = 100;
  int c = 2;
  int leaning_rate = 1;
  map <string, vector<int> > weights = train(n_iter, examples, empty_weights, c, leaning_rate);
  write_weights(weights, argv[3]);
  return 0;
}
