/*#include <iostream>
#include <vector>
#include <array>

struct dest{
    int sat=0;
    int dist=0;
};

const long long int MAX_N=10e6+1;

std::array<std::vector<dest>,MAX_N> l;

std::array<bool,MAX_N> viz;

int distf=0;

int n,m;

int x,y;

void dfs(int nod,int dist){
    if(nod == y){
        distf=dist;
        return;
    }
    for(auto vec:l[nod]){
        if(viz[vec.sat]){
            continue;
        }
        viz[vec.sat]=true;
        if(vec.sat>nod){
            dfs(vec.sat,dist+vec.dist);
        }else{
            dfs(vec.sat,dist-vec.dist);
        }
    }
}

int main(){
    std::cin>>n>>m;
    std::cin>>x>>y;
    for(int i=0;i<m;i++){
        int s1,s2,d;
        std::cin>>s1>>s2>>d;
        l[s1].push_back({s2,d});
        l[s2].push_back({s1,d});
    }
    dfs(x,0);
    std::cout<<distf;
}*/ // mai devreme e un cod scris cu picioarele 

#include <iostream>
#include <vector>
#include <array>
#include <fstream>

struct Road{
    int destination_village=0;
    int distance=0;
};

class Solution{
    int village_count,road_count;
    int start_village,end_village;
    std::vector<std::vector<Road>> roads;
    std::vector<bool> visited;
    std::istream& input;
    std::ostream& output;
    int final_distance=0;

    void add_road(int first_village,int second_village,int distance){
        roads[first_village].push_back({second_village,distance});
        roads[second_village].push_back({first_village,distance});
    }
public:
    Solution(std::istream& input,std::ostream& output) : input(input), output(output){}
    void read(){
        input>>village_count>>road_count;
        input>>start_village>>end_village;
        roads.resize(village_count+1);
        visited.resize(village_count+1);
        for(int idx=0;idx<road_count;idx++){
            int first_village,second_village,distance;
            input>>first_village>>second_village>>distance;
            add_road(first_village,second_village,distance);
        }
    }
    void dfs(int curr_village,int curr_distance){
        if(curr_village == end_village){
            final_distance=curr_distance;
            return;
        }
        for(auto road:roads[curr_village]){
            int next_village=road.destination_village;
            int road_length=road.distance;
            if(visited[next_village]){
                continue;
            }
            visited[next_village]=true;
            bool is_previous_village=next_village<curr_village;
            if(is_previous_village){
                dfs(next_village,curr_distance-road_length);
            }else{
                dfs(next_village,curr_distance+road_length);
            }
        }
    }
    void run(){
        constexpr int initial_distance=0;
        dfs(start_village,initial_distance);
    }
    void print(){
        output<<final_distance;
    }
};

int main(){
    std::ifstream fin("sate.in");
    std::ofstream fout("sate.out");
    Solution sate(fin,fout);
    sate.read();
    sate.run();
    sate.print();
}