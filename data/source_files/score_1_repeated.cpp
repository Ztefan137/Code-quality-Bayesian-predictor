#include <iostream>
using namespace std;
int main(){
int a[5]={4,7,2,9,3};int total=0;
for(int i=0;i<5;i++){
if(a[i]>5){
if(a[i]%2==0){total=total+a[i]*2;}
else{total=total+a[i]*3;}
}else{
if(a[i]==2){total=total+10;}
else{total=total-1;}
}
}
cout<<total<<endl;
return 0;
}
