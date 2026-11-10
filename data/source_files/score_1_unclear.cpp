#include <iostream>
using namespace std;
int main(){int x=13,y=0,z=1;
while(x>0){if(x%2==0){y=y+x*3;}else{if(x>7){y=y+5;}else{y=y-2;}}
if(y>40){z=z+1;}else{z=z+2;}x=x-1;}
cout<<y<<" "<<z<<endl;return 0;}
