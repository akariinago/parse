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

template <typename List>
void split(const std::string& s, const std::string& delim, List& result)
{
    result.clear();
    string::size_type pos = 0;

    while(pos != string::npos )
    {
        string::size_type p = s.find(delim, pos);

        if(p == string::npos)
        {
            result.push_back(s.substr(pos));
            break;
        }
        else {
            result.push_back(s.substr(pos, p - pos));
        }

        pos = p + delim.size();
    }
}

int main(int argc, char *argv[]) {
  //ルールを読み込む
  std::ifstream ifs(argv[1]);
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

  int np = i;
  char input[50];
  cout << "\nEnter Input:";
  cin >> input;
  vector<string> ip;
  MeCab::Tagger *tagger = MeCab::createTagger("-Owakati");
  const char *result = tagger->parse(input);
  split(result, " ", ip);
  ip.pop_back();
  int lip = ip.size();
  for(int j = 0; j < ip.size(); j++){
    cout << ip[j] << " "; 
  }
  cout << lip << endl; 
  vector<string> stack;
  
  int stpos = 0;
  i = 0;
  
  //moving input
  stack.push_back(ip[i]);
  i++; stpos++;

  cout << "\n\nStack\tInput\tAction";
  int count = 0;
  vector<string> ans;
  do {
    int r = 1;
    while (r != 0) {
      cout << "\n"; 
      for (int p = 0; p < stack.size(); p++) {
	cout << stack[p];
      } 
      cout << "\t";
      for (int p = i; p < ip.size(); p++) {
	cout << ip[p];
	}
      if (r == 2) {
	cout << "\tReduced";
      } else {
	cout << "\tShifted";
      }
      r = 0;
      //try reducing
      int k,l;
      for (k=0; k<stpos; k++) {
	ts2 = "";
	for(l = k; l < stack.size(); l++) {//removing first character
	  ts2 += stack[l];
	  }
	//now compare each possibility with production
	for (int m = 0; m < np; m++) {
	  if (ts2 == g[m].prod) {
	    int ss =  stack.size();
	    for (l = k; l < ss; l++) {//removing matched part from stack
	      stack.pop_back();
	      stpos--;
	      }
	    stpos = k;
	      
	    //concatinate the string
	    stack.push_back(g[m].p);
	    if ('A' > g[m].prod[0] || g[m].prod[0] > 'Z') {
	      ans.push_back("( "+(string)g[m].p+" " + (string)g[m].prod+" )");
	    } else {
	      vector<string>::iterator it = ans.begin();  
	      it = ans.insert(it,"( "+(string)g[m].p);  
	      ans.push_back(" )");	
	    }
	    count++;
	    stpos++;
	    r = 2;
	  } 
	}
      }
    }
    
    //moving input
    if (i < lip) {
      cout << ip[i] << endl;
      stack.push_back(ip[i]);
    }
    i++; stpos++;
    cout << stack.size() << " " << stpos << " " << lip << endl; 
  } while(stack.size() != 1 && stpos != lip);
  
  if(stack.size() == 1) {
    cout << "\n String Accepted\n";
    for (int i = 0; i < ans.size(); i++) {
      cout << ans[i];
    }
  }
  cout << endl;
  return 0;
}
 
/* OUTPUT
 
 
Enter Number of productions:4
 
Enter productions:
E->E+E
E->E*E
E->(E)
E->a
 
Enter Input:(a+a)*a
 
 
Stack   Input   Action
(       a+a)*a  Shifted
(a      +a)*a   Shifted
(E      +a)*a   Reduced
(E+     a)*a    Shifted
(E+a    )*a     Shifted
(E+E    )*a     Reduced
(E      )*a     Reduced
(E)     *a      Shifted
E       *a      Reduced
E*      a       Shifted
E*a             Shifted
E*E             Reduced
E               Reduced
 String Accepted
 
*/
