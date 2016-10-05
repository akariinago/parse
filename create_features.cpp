#include <algorithm>
#include<fstream>
#include<iostream>
#include<map>
#include<sstream>
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

vector <string> load_commands(char *commands_file) {
  ifstream ifs(commands_file);
  if(!ifs){
    cout<<"Faild";
    exit(1);
  }
  string str;
  vector<string> commands;
  int count = 0;
  while(getline(ifs,str)){
    string token;
    istringstream stream(str);
    //1行のうち、文字列とコンマを分割する
    //cout << str << endl;
    while(getline(stream,token,',')){
      if(count%5==4) {
	cout<<token<<endl;
	commands.push_back(token);
      }
      count++;
    }
  }
}

vector <vector <pair<string, string > > > make_postagged (vector <string> commands) {
  vector <vector <pair <string, string > > > tagged;
  MeCab::Tagger *tagger = MeCab::createTagger("");
  for (int i = 0; i < commands.size(); i++) {
    const char *result = tagger->parse(commands[i].c_str());
    vector<string> lines;
    vector<string> line;
    vector<string> pos;
    vector <pair<string, string> > t;
    split(result, "\n", lines);
    for (int j = 0; j < lines.size()-2; j++) {
      split(lines[j], "\t", line);
      split(line[1], ",", pos);
      t.push_back(make_pair(line[0],pos[0]));
    }
    tagged.push_back(t);
  }
    delete tagger;
    return tagged;
}

vector<string> uni_bi_tri(string type, vector<pair <string, string> > tags, int j) {
  vector<string> feature;
  if (type == "w") {
    feature.push_back(type + "_u." + tags[j].first);
    feature.push_back(type + "_b0." + tags[j-1].first + "_" + tags[j].first);
    feature.push_back(type + "_b1." + tags[j].first + "_" + tags[j+1].first);
    feature.push_back(type + "_t0." + tags[j-2].first + "_" + tags[j-1].first + "_" + tags[j].first);
    feature.push_back(type + "_t0." + tags[j-1].first + "_" + tags[j].first + "_" + tags[j+1].first);
    feature.push_back(type + "_t0." + tags[j].first + "_" + tags[j+1].first + "_" + tags[j+2].first);
  } else {
    feature.push_back(type + "_u." + tags[j].second);
    feature.push_back(type + "_b0." + tags[j-1].second + "_" + tags[j].second);
    feature.push_back(type + "_b1." + tags[j].second + "_" + tags[j+1].second);
    feature.push_back(type + "_t0." + tags[j-2].second + "_" + tags[j-1].second + "_" + tags[j].second);
    feature.push_back(type + "_t0." + tags[j-1].second + "_" + tags[j].second + "_" + tags[j+1].second);
    feature.push_back(type + "_t0." + tags[j].second + "_" + tags[j+1].second + "_" + tags[j+2].second);
  }
  return feature;
}

vector<string> construct_feature(vector<pair <string,string> > pos_tag, int j) {
  vector<string> feature;
  vector<string> w_f = uni_bi_tri("w", pos_tag, j);
  vector<string>  p_f = uni_bi_tri("p", pos_tag, j);
  copy(w_f.begin(),w_f.end(),std::back_inserter(feature));
  copy(p_f.begin(),p_f.end(),std::back_inserter(feature));
  return feature;
}

vector <vector <string > > create_features (vector <string> commands, vector <vector <pair<string, string > > > pos_tagged) {
  vector <vector <string> > features;
  for (int i = 0; i < commands.size(); i++) {
    vector <pair<string, string > > poses =  pos_tagged[i];
    for (int j = 0; j < poses.size(); j++) {
      features.push_back(construct_feature(poses, j));
    }
  }
  return features;
}

int main(int argc, char *argv[]) {
  char *commands_file = argv[1];
  char *features_file = argv[2];
  vector <string> commands = load_commands(commands_file);
  vector <vector <pair <string, string > > > pos_tagged = make_postagged(commands); 
  vector <vector <string> > features = create_features(commands, pos_tagged);
  //write_features(features, features_file);
  return 0;
}
