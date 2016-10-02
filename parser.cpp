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

struct grammer{
  string p;
  string prod;
} g[20];

class Item {       
  vector<string> stack;
  vector<string> queue;  
  vector<string> features;  
  vector<string> ans;
  int score;
  int flag;
public:
  void set_score(int s) {score = s;}
  void set_flag(int f) {flag = f;}
  int get_flag() {return flag;}
  int get_score() {return score;}
  string get_feature() {return features.back();}
  void set_stack(vector<string> s) {stack = s;}
  int get_ssize() {return stack.size();}
  string get_stack(int n) {return stack[n];}
  vector<string> get_stack() {return stack;}
  void set_queue(vector<string> q) {queue = q;}
  vector<string> get_queue() {return queue;}
  int get_qsize() {return queue.size();}
  string get_queue(int n) {return queue[n];}
  vector<string> get_ans() {return ans;}
  void set_ans(vector<string> a) {ans = a;}
  void print_stack() {
    cout << "stack";
    for (int i = 0; i < stack.size(); i++) {
      cout << stack[i];
    }  
  }
  void print_queue() {
    cout << "queue";
    for (int i = 0; i < queue.size(); i++) {
      cout << queue[i];
    }  
  }
  vector<string> construct_features() {
    if(!stack.empty()) {
      features.push_back("ST_w." + stack.back());
    } else {
      features.push_back("ST_e");
    }
    if(!queue.empty()) {
      features.push_back("N0_w." + queue.front());
      if (!stack.empty()) {
	features.push_back("ST_p_w_N0_w_." + stack.back() + queue.front());
      }
    }
    if(queue.size() > 1){
      features.push_back("N1_w." + queue[queue.size()-2]);
    }
    return features;
  }
  static bool compareItem(Item l, Item r) { return (l.score < r.score); }
  struct compareItemFunctor : public binary_function<Item, Item, bool>
  {
    bool operator()(Item l, Item r)
    {
      return (l.score < r.score);
    }
  };
};

vector<string> make_sdc(vector<string> ans, int m) {
  if ('A' > g[m].prod[0] || g[m].prod[0] > 'Z') {
    ans.push_back("( "+(string)g[m].p+" " + (string)g[m].prod+" )");
  } else {
    vector<string>::iterator it = ans.begin();  
    it = ans.insert(it,"( "+(string)g[m].p);  
    ans.push_back(" )");	
  }
  return ans;
}

vector<Item> shift(Item item) {
  vector<Item> items;
  vector<string> s = item.get_stack();
  vector<string> q = item.get_queue();
  if (!q.empty()) {
    s.push_back(q[0]);
    item.set_stack(s);
    q.erase(q.begin());
    item.set_queue(q);
  } else {
    item.set_flag(1);
  }
  items.push_back(item);
  return items;
}

vector<Item> reduce(Item item) {
  vector<string> s = item.get_stack();
  vector<Item> items;
  //concatinate the string
  int flag = 0;
  string ts = "";
  int i = s.size()-1;
  string ss = s[i];
  if (('A' > ss[0] || ss[0] > 'Z') && ss[0] != '(') {
    while (('A' >  ss[0] || ss[0] > 'Z')) {
      ts = s[i] + ts;
      s.pop_back();
      i--;
      if (i < 0){
	break;
      }
      ss = s[i];
    } 
  } else {
    if (i != 0) { 
      ts = s[i-1] + s[i];
      s.pop_back();
      s.pop_back();
    } else {
      ts = "X";
    }
  }
  for (int m = 0; m < sizeof(g)/ sizeof(g[0]); m++) {
    if (ts == g[m].prod) {
      s.push_back(g[m].p);
      item.set_stack(s);
      vector<string> a = item.get_ans();
      item.set_ans(make_sdc(a,m));
      items.push_back(item);
      s.pop_back();
      flag = 1;
    }
 }
  if(!flag) {
    item.set_flag(1);
    items.push_back(item);
  }
  return items;
} 

vector<Item> apply(int i,Item item) {
  if (i == 0) {
    //cout << "shift" << endl;
    return shift(item);
  } else {
    //cout << "reduce" << endl;
    return reduce(item);
  }
}

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

vector<string> parse(const char *input, vector<string> ip) {
  MeCab::Tagger *tagger = MeCab::createTagger("-Owakati");
  const char *result = tagger->parse(input);
  split(result, " ", ip);
  ip.pop_back();
  return ip;
}

void load_rule(char *c) {
  std::ifstream ifs(c);
  if (ifs.fail()) {
    std::cerr << "Failed" << std::endl;
    exit(1);
  }
  int i = 0;
  char ts[256];
  string ts2 = "";
  while (ifs.getline(ts,255)) {
    int n;
    for (int j = 0; j < 256; j++) {
      if (ts[j] == '-') {
	n = j;
	break;
      }
    }
    ts2 = "";
    for (int j = 0; j < n; j++) {
      ts2 +=  ts[j];
    }
    g[i].p = ts2;
    ts2 = "";
    for (int j = n+2; j < strlen(ts); j++) {
      ts2 +=  ts[j];
    }
    g[i].prod = ts2;
    cout << g[i].p << " " << g[i].prod << endl;
    i++;
  }
}

map<string, vector<int> > load_model(char *c) {
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

void output_result(vector<string> ans) {
  for (int i = 0; i < ans.size(); i++) {
    cout << ans[i];
  }
  cout << endl;
}

int compute_score(vector<string> features, map<string, vector<int> > weights, int index) {
  /*Keyword arguments:
    features -- feature vector of a sample (list of strings)
    weights -- trained model
    index -- desired class*/
  int score = 0;
  for (int i = 0; i < features.size(); i++) {
    string feat = features[i];
    if (weights.count(feat) == 0) {
      continue;
    }
    score +=  weights[feat][index];
  }
  return score;
}

int main(int argc, char *argv[]) {
  //モデルを読み込む
  char *model_file = argv[1]; 
  map<string, vector<int> > weights = load_model(model_file);
  char *rule_file = argv[2]; 
  load_rule(rule_file);
  char input[50];
  cout << "\nEnter Input:";
  cin >> input;
  vector<string> ip;
  ip = parse(input,ip);
  int lip = ip.size();
  int stpos = 0;
  int i = 0;
  Item start_item;
  vector<string> s;
  vector<string> f;
  vector<string> a;
  start_item.set_queue(ip);
  start_item.set_stack(s);
  start_item.set_score(0);
  start_item.set_flag(0);
  //moving input
  start_item = shift(start_item)[0];    
  //cout << "\n\nStack\tInput\tAction" << endl;
  vector<Item> deque; //agenda
  Item res; //candidate_output
  int score = 0;
  deque.push_back(start_item);
  while (!deque.empty()) {
    vector<Item> lst;
    for (int i = 0; i < deque.size(); i++) {
      Item item = deque[i];
      for (int j = 0; j < 2; j++) {
	vector<Item> new_items = apply(j,item);
	for (int k = 0; k < new_items.size(); k++) {
	  Item new_item = new_items[k];
	  if (new_item.get_flag()) {// もしactionがitemに適用できなかったらスルー
	    continue;
	  }
	  int new_score = item.get_score() + compute_score(new_item.construct_features(),weights,j);
	  new_item.set_score(new_score);
	  vector<string> s = new_item.get_stack();
	  if (s[0] == "E" && s.size()) {     
	    if (res.get_stack().empty() || new_score > score) {
	      res = new_item; // candidate_outputを更新
	      score = new_score; 
	    }
	  } else {
	    lst.push_back(new_item); // 途中経過なのでリストにitemを追加
	  }
	}
      }
    }
    sort(lst.begin(), lst.end(), Item::compareItem); // scoreの高い順に並べる
    while (lst.size() > 10) lst.pop_back(); 
    deque.clear();
    deque = lst; //プロセスが全て終わった時lstは空のままになる
  } 
  output_result(res.get_ans());
  return 0;
}
