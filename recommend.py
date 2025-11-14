import networkx as nx
from collections import Counter, defaultdict, deque
import sys
import copy

sys.setrecursionlimit(10000)

class NetworkResilience:
    def __init__(self, graph):
        self.original_graph = nx.to_dict_of_lists(graph)
        self.time = 0

    #  Tarjan's Algorithm for Articulation Points (Removing it would break the netwrok into disconnected components)
    def _find_articulation_points_util(self, u, visited, disc, low, parent, ap_set, current_graph):
        children = 0
        visited[u] = True
        disc[u] = self.time
        low[u] = self.time
        self.time += 1

        #If root has 2+ children, it is AP
        # If a non-root satisfies low[v] >= disc[u], then u is AP
        for v in current_graph.get(u, []):
            if v == parent[u]:
                continue
            
            if visited[v]:
                low[u] = min(low[u], disc[v])
            else:
                children += 1
                parent[v] = u
                self._find_articulation_points_util(v, visited, disc, low, parent, ap_set, current_graph)
                low[u] = min(low[u], low[v])

                if parent[u] == -1 and children > 1:
                    ap_set.add(u)
                if parent[u] != -1 and low[v] >= disc[u]:
                    ap_set.add(u)

    def get_articulation_points(self, graph_snapshot=None):
        if graph_snapshot is None:
            graph_snapshot = self.original_graph
            
        self.time = 0
        visited = {node: False for node in graph_snapshot}
        disc = {node: float('inf') for node in graph_snapshot} #discovery time of node
        low = {node: float('inf') for node in graph_snapshot}
        parent = {node: -1 for node in graph_snapshot}
        ap_set = set() #set of articulation points

        for node in graph_snapshot:
            if not visited[node]:
                self._find_articulation_points_util(node, visited, disc, low, parent, ap_set, graph_snapshot)
        return list(ap_set)

    # This runs a bfs for every unvisited node and finds component size return size of largest connected components 
    def get_giant_component_size(self, graph_snapshot):
        visited = set()
        max_size = 0
        nodes = list(graph_snapshot.keys())
        if not nodes: return 0

        for node in nodes:
            if node not in visited:
                curr_size = 0
                q = deque([node])
                visited.add(node)
                while q:
                    curr = q.popleft()
                    curr_size += 1
                    for neighbor in graph_snapshot.get(curr, []):
                        if neighbor not in visited and neighbor in graph_snapshot:
                            visited.add(neighbor)
                            q.append(neighbor)
                max_size = max(max_size, curr_size)
        return max_size

    # --- Simulation Loop ---
    def simulate_ap_attack(self, aps):
        print("\nSimulating Network Collapse...")
        current_graph = copy.deepcopy(self.original_graph)
        
        # Sort APs by Degree (Attack the biggest Hubs first)
        aps.sort(key=lambda x: len(current_graph.get(x, [])), reverse=True)
        
        initial_size = len(current_graph)
        initial_lcc = self.get_giant_component_size(current_graph)
        
        stats = [(0, initial_lcc)] 
        nodes_removed_count = 0
        
        for target in aps:
            if target not in current_graph: continue
            
            del current_graph[target]
            for node in current_graph:
                if target in current_graph[node]:
                    current_graph[node].remove(target)
            
            nodes_removed_count += 1
            
            current_lcc = self.get_giant_component_size(current_graph)
            stats.append((nodes_removed_count, current_lcc))
            
            print(f" -> Destroyed Critical Node {target}. Giant Component Size: {current_lcc}")
            
            if current_lcc < (0.1 * initial_size):
                print("[SYSTEM] Network Shattered.")
                break
                
        return stats



#Give friend recommendation for a given node using jaccard coefficient
def get_friend_recommendations(G, target_node):
    """
    Uses Jaccard Coefficient to find people with high overlap in friends.
    Score = (Intersection of Friends) / (Union of Friends)
    """
    if target_node not in G:
        print(f"Error: Node {target_node} does not exist.")
        return

    current_friends = set(G.neighbors(target_node))
    candidates = []

    print(f"\nAnalyzing network for Node {target_node}...")
    
    for node in G.nodes():
        if node == target_node or node in current_friends:
            continue
            
        others_friends = set(G.neighbors(node))
        
        # Intersection: Mutual friends
        mutual_friends = current_friends.intersection(others_friends)
        
        if not mutual_friends:
            continue
            
        # Jaccard Index Calculation
        union_size = len(current_friends.union(others_friends))
        score = len(mutual_friends) / union_size if union_size > 0 else 0
        
        candidates.append((node, score, list(mutual_friends)))
    
    # Sort by score (highest probability first)
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    possible_candidates=[]
    if not candidates:
        print("No suitable recommendations found (no mutual friends).")
    else:
        for i, (cand, score, mutuals) in enumerate(candidates[:3], 1):
            possible_candidates.append(cand)
            print(f"{i}. Node {cand} (Similarity Score: {score:.2f})")
    return possible_candidates




def _jaccard(a, b):
    """
    Helper function for Jaccard similarity.
    (a and b are sets)
    """
    if not a and not b:
        return 0
    try:
        return len(a & b) / len(a | b)
    except ZeroDivisionError:
        return 0


# Post recommendation
def get_post_recommendations(target_user, user_likes_db, k=3):
    """
    Recommends posts to a user based on likes from similar users.
    
    :param target_user: The int ID of the user to get recommendations for.
    :param user_likes_db: A dict {user_id: {set_of_post_ids}}
    :param k: How many similar users to consider.
    :return: A list of recommended post IDs (e.g., ["P1", "P5"]).
    """
    
    target_posts = user_likes_db.get(target_user, set())
    sims = [] # Stores (similarity_score, other_user_id)

    for other_user, posts in user_likes_db.items():
        if other_user == target_user:
            continue
            
        sim = _jaccard(target_posts, posts)
        if sim > 0:
            sims.append((sim, other_user))

    sims.sort(reverse=True)
    similar_users = [u for _, u in sims[:k]]

    rec_posts = set()
    for u in similar_users:
        for p in user_likes_db.get(u, set()):
            if p not in target_posts:
                rec_posts.add(p)
                
    return list(rec_posts)