#include<fstream>
#include<iostream>
#include<string>
#include<vector>
#include<stdio.h>
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
public:
  void set_stack(vector<string> s) {stack = s;}
  int get_ssize() {return stack.size();}
  string get_stack(int n) {return stack[n];}
  vector<string> get_stack() {return stack;}
  void set_queue(vector<string> q) {queue = q;}
  vector<string> get_queue() {return queue;}
  int get_qsize() {return queue.size();}
  string get_queue(int n) {return queue[n];}
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
};

Item shift(Item item) {
  vector<string> s = item.get_stack();
  vector<string> q = item.get_queue();
  s.push_back(q[0]);
  cout << q[0] << endl;
  item.set_stack(s);
  q.erase(q.begin());
  item.set_queue(q);
  return item;
}

Item reduce(Item item, int k, int l, int m) {
  int ss =  item.get_ssize();
  vector<string> s = item.get_stack();
  for (l = k; l < ss; l++) {//removing matched part from stack
    s.pop_back();
  }
  //concatinate the string
  s.push_back(g[m].p);
  item.set_stack(s);
  return item;
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

int load_rule(char *c) {
  std::ifstream ifs(c);
  if (ifs.fail()) {
    std::cerr << "Failed" << std::endl;
    return -1;
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
    cout << g[i].p << ":" << g[i].prod << endl;
    i++;
  }
  return i;
}

void output_result(vector<string> ans, vector<string> stack) {
  if(stack.size() == 1) {
    cout << "\n String Accepted\n";
    for (int i = 0; i < ans.size(); i++) {
      cout << ans[i];
    }
  }
  cout << endl;
}

int main(int argc, char *argv[]) {
  //ルールを読み込む
  char *rule_file = argv[1]; 
  int np = load_rule(rule_file);

  char input[50];
  cout << "\nEnter Input:";
  cin >> input;
  vector<string> ip;
  ip = parse(input,ip);
  int lip = ip.size();

  int stpos = 0;
  int i = 0;
  Item item;
  vector<string> s;
  item.set_queue(ip);
  item.set_stack(s);
  //moving input
  item = shift(item);    
    // stack.push_back(ip[i]);
  i++; stpos++;

  cout << "\n\nStack\tInput\tAction";
  vector<string> res;
  do {
    int r = 1;
    while (r != 0) {
      cout << "\n";
      item.print_stack();
      cout << "\t";
      item.print_queue();
      if (r == 2) {
	cout << "\tReduced";
      } else {
	cout << "\tShifted";
      }
      r = 0;
      //try reducing
      int k,l;
      for (k=0; k<stpos; k++) {
	string ts2 = "";
	for(l = k; l < item.get_ssize(); l++) {//removing first character
	  ts2 += item.get_stack(l);
	  }
	//now compare each possibility with production
	for (int m = 0; m < np; m++) {
	  if (ts2 == g[m].prod) {
	    item = reduce(item, k, l, m);
	    stpos = k;
	    res = make_sdc(res,m);
	    stpos++;
	    r = 2;
	  } 
	}
      }
    }
    //moving input
    cout << i << lip << endl;
    if (i < lip) {
      item = shift(item);
    }
    i++; stpos++;
  } while(item.get_ssize() != 1 && stpos != lip);

  output_result(res, item.get_stack());
  return 0;
}
