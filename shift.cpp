#include<iostream>
#include<fstream>
#include<stdio.h>
#include<string.h>
#include<string>
#include<vector>
 
using namespace std;

struct grammer{
    char p[20];
    char prod[20];
}g[10];
 
int main()
{
    int i,stpos,j,k,l,m,o,p,f,r;
    int np,tspos,cr;
    int count = 0;
    vector<string> ans;
    cout<<"\nEnter Number of productions:";
    cin>>np;
    //なぜかtsに日本語が入るとnpの値が0になるので定義
    const int a = np; 	  
    char sc,ts[10];
 
    cout<<"\nEnter productions:\n";
    for(i=0;i<a;i++)
    {
        cin>>ts;
	int n;
	for(int j = 0;j<10;j++){
	  if(ts[j]=='-'){
	    n=j;
	  }
	}
        strncpy(g[i].p,ts,n);
        strcpy(g[i].prod,&ts[n+2]);
	cout << g[i].p << " " << g[i].prod << endl;
    }
 
    char ip[50];
    cout<<"\nEnter Input:";
    cin>>ip;
 
    int lip=strlen(ip);
 
    char stack[10];
     
    stpos=0;
    i=0;
     
    //moving input
    sc=ip[i];
    stack[stpos]=sc;
    i++;stpos++;
 
    cout<<"\n\nStack\tInput\tAction";
    do
    {
        r=1;
        while(r!=0)
        {
            cout<<"\n";
            for(p=0;p<stpos;p++)
            {
                cout<<stack[p];
            }
            cout<<"\t";
            for(p=i;p<lip;p++)
            {
                cout<<ip[p];
            }
 
            if(r==2)
            {
                cout<<"\tReduced";
            }
            else
            {
                cout<<"\tShifted";
            }
            r=0;
             
            //try reducing
            getchar();
            for(k=0;k<stpos;k++)
            {
                f=0;
 
                for(l=0;l<10;l++)
                {
                    ts[l]='\0';
                }
 
                tspos=0;
                for(l=k;l<stpos;l++) //removing first character
                {
                    ts[tspos]=stack[l];
                    tspos++;
                }
 
                //now compare each possibility with production
                for(m=0;m<np;m++)
                {
                    cr = strcmp(ts,g[m].prod);
 
                    //if cr is zero then match is found
                    if(cr==0)
                    {
                        for(l=k;l<10;l++) //removing matched part from stack
                        {
                            stack[l]='\0';
                            stpos--;
                        }
 
                        stpos=k;
         
                        //concatinate the string
                        strcat(stack,g[m].p);
			//cout << g[m].p << endl;
			//cout << g[m].prod << endl;
			if('A' > g[m].prod[0] || g[m].prod[0] > 'Z'){
			  ans.push_back("( "+(string)g[m].p+" "+(string)g[m].prod+" )");
			}
			else{
			  vector<string>::iterator it = ans.begin();  
			  it = ans.insert(it,"( "+(string)g[m].p);  
			  ans.push_back(" )");

			}
			count++;
                        stpos+=strlen(g[m].p);
                        r=2;
                    }
                }
            }
        }
         
        //moving input
        sc=ip[i];
        stack[stpos]=sc;
        i++;stpos++;
 
    }while(strlen(stack)!=1 && stpos!=lip);
 
    if(strlen(stack)==1)
    {
        cout<<"\n String Accepted\n";
	for (int i = 0; i < ans.size(); i++) {
	  cout << ans[i];
	}
    }
 
    getchar();
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
