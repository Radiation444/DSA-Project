#include<bits/stdc++.h>
using namespace std;

std::random_device rd;
std::mt19937 gen(rd());

class Network{
    private:
    int n;
    vector<set<int>> adj;
    vector<vector<int>> memos;
    vector<vector<int>> label_counts;
    public:
    void SLPA(int t, int cutoff){
        int n=adj.size()-1;
        std::uniform_int_distribution<> distrib(1, n);
        while(t--){
            for(int i=1;i<=n;i++){
                vector<int> opts;
                for(auto nx:adj[i]){
                    int rnum=distrib(gen)%(memos[nx].size());
                    opts.push_back(memos[nx][rnum]);
                }
                int rnum=distrib(gen)%(opts.size());
                memos[i].push_back(opts[rnum]);   
                label_counts[i][opts[rnum]]++;
            }
        }
        for(int i=1;i<=n;i++){
            vector<int> mem=memos[i];
            for(auto it=mem.begin();it!=mem.end();it++){
                if(label_counts[i][*it]<cutoff*mem.size()){
                    mem.erase(it);
                    label_counts[i][*it]--;
                }
            }
        }
    }
    void update(vector<array<int,3>>& changes){
        set<int> affected_nodes;
        for(auto change:changes){
            if(change[0]==0){
                adj.push_back({});
                memos.push_back({});
                label_counts.push_back({});
                n++;
            }
            else if(change[0]==1){
                adj[change[1]].insert(change[2]);
                adj[change[2]].insert(change[1]);
                affected_nodes.insert(change[1]);
                affected_nodes.insert(change[2]);
            }
            else{
                adj[change[1]].erase(adj[change[1]].find(change[2]));
                adj[change[2]].erase(adj[change[2]].find(change[1]));
                affected_nodes.insert(change[1]);
                affected_nodes.insert(change[2]);
            }
        }
        for(auto& them:affected_nodes){
            for(auto& mem:memos[them]){
                 
            }
        }
    }

    
};




int main(){    
    int n, m;
    std::cin >> n >> m;
    vector<vector<int>> adj(n+1);
    while(m--){
        int x,y,w;
        std::cin >> x >> y >>w;
        adj[x].push_back(y);
        adj[y].push_back(x);
    }


}