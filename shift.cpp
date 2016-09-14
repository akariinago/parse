#include<fstream>
#include<iostream>
#include<string>
#include<vector>
#include<stdio.h>
#include<string.h>
 
using namespace std;

struct grammer{
    char p[20];
    char prod[20];
} g[20];
 
int main(int argc, char *argv[]) {
  //ルールを読み込む
  std::ifstream ifs(argv[1]);
  if (ifs.fail()) {
    std::cerr << "Failed" << std::endl;
    return -1;
  }
  int i = 0;
  char ts[256];
  while (ifs.getline(ts,255)) {
    int n;
    for (int j = 0; j < 256; j++) {
      if (ts[j] == '-') {
	n = j;
	break;
      }
    }
    strncpy(g[i].p, ts, n);
    strcpy(g[i].prod, &ts[n+2]);
    //cout << g[i].p << " " << g[i].prod << endl;
    i++;
  }
  int np = i;
  char ip[50];
  cout << "\nEnter Input:";
  cin >> ip;
  
  int lip = strlen(ip);
 
  char stack[50];
  int stpos = 0;
  i = 0;
  
  //moving input
  stack[stpos] = ip[i];
  i++; stpos++;
  cout << "\n\nStack\tInput\tAction";
  int count = 0;
  vector<string> ans;
  do {
    int r = 1;
    while (r != 0) {
      cout<<"\n";
      for (int p = 0; p < stpos; p++) {
	cout << stack[p];
      }
      cout << "\t";
      for (int p = i; p < lip; p++) {
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
	for (l = 0; l < 10; l++) {
	  ts[l] = '\0';
	}
	
	int tspos = 0;
	for(l = k; l < stpos; l++) {//removing first character
	  ts[tspos] = stack[l];
	  tspos++;
	}
	//now compare each possibility with production
	for (int m = 0; m < np; m++) {
	  int cr = strcmp(ts,g[m].prod);
	  //if cr is zero then match is found
	  if (cr == 0) {
	    for (l = k; l < 10; l++) //removing matched part from stack
	      {
		stack[l] = '\0';
		stpos--;
	      }
	    stpos = k;
	      
	    //concatinate the string
	    strcat(stack,g[m].p);
	    if ('A' > g[m].prod[0] || g[m].prod[0] > 'Z') {
	      ans.push_back("( "+(string)g[m].p+" " + (string)g[m].prod+" )");
	    } else {
	      vector<string>::iterator it = ans.begin();  
	      it = ans.insert(it,"( "+(string)g[m].p);  
	      ans.push_back(" )");	
	    }
	    count++;
	    stpos += strlen(g[m].p);
	    r = 2;
	  } 
	}
      }
    }
    
    //moving input
    stack[stpos] = ip[i];
    i++; stpos++;
    
  } while(strlen(stack) != 1 && stpos != lip);
  
  if(strlen(stack) == 1) {
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
