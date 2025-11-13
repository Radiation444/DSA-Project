import networkx as nx
import random
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from textwrap import shorten

def run_slpa(G, T=20, r=0.25, update_nodes=None):
    """
    Standard or restricted SLPA (Speaker-Listener Label Propagation Algorithm).
    If update_nodes is given, restricts propagation to those nodes (used in dynamic updates).
    This version weights speaker influence by edge_weight)
    """
    nodes = list(G.nodes())
    mem = {v: Counter({v: 1}) for v in nodes}

    for t in range(T):
        random.shuffle(nodes)
        for listener in nodes:
            if update_nodes is not None and listener not in update_nodes:
                continue  
            speakers = list(G.neighbors(listener))
            if not speakers:
                continue
            weighted_labels = Counter()  
            for s in speakers:
                if not mem[s]: continue  
        
                label = random.choices(
                    population=list(mem[s].keys()),
                    weights=list(mem[s].values()), k=1)[0]
                edge_data = G.get_edge_data(listener, s)
                edge_weight = edge_data.get('weight', 1) if edge_data else 1
                if edge_weight>30:
                    influence = (edge_weight + 1e-6)
                    weighted_labels[label] += influence
            if not weighted_labels:
                continue
            pop, weights = list(weighted_labels.keys()), list(weighted_labels.values())
            chosen = random.choices(population=pop, weights=weights, k=1)[0]
            mem[listener][chosen] += 1

    communities = defaultdict(list)
    for v in nodes:
        if v not in mem: continue
        total = sum(mem[v].values())
        if total == 0: continue
            
        for label, count in mem[v].items():
            if count / total >= r:
                communities[label].append(v)
    return dict(communities), mem

def dynamic_slpa(G, mem, communities, changes):
    removed_nodes = set()
    update_nodes = set()

    for typ, data in changes:
        if typ == "add_edge":
            u, v, w = data
            G.add_edge(u, v, weight=w)
            update_nodes.update([u, v])
        elif typ == "remove_edge":
            u, v = data
            if G.has_edge(u, v):
                G.remove_edge(u, v)
                update_nodes.update([u, v])
        elif typ == "add_node":
            u = data
            G.add_node(u)
            mem[u] = Counter({u: 1})
            update_nodes.add(u)
        elif typ == "remove_node":
            u = data
            if u in G:
                G.remove_node(u)
                removed_nodes.add(u)
                if u in mem:
                    del mem[u]
                
                for cid in list(communities.keys()):
                    if u in communities[cid]:
                        communities[cid].remove(u)
                        if not communities[cid]:
                            del communities[cid]
    for v in mem:
        for r in removed_nodes:
            mem[v].pop(r, None)

    for c_nodes in communities.values():
        if update_nodes.intersection(c_nodes): 
            update_nodes.update(c_nodes)

    for u in list(update_nodes):
        if u in G: 
            update_nodes.update(G.neighbors(u))
    
    update_nodes.difference_update(removed_nodes)
    
    if not update_nodes:
        return communities, mem

    for u in update_nodes:
        if u in G:
            mem[u] = Counter({u: 1})

    H = G.subgraph(update_nodes).copy()
    sub_communities, sub_mem = run_slpa(H, T=20, r=0.25, update_nodes=update_nodes) 

    for u in sub_mem:
        if u in mem: 
            mem[u] = sub_mem[u]

    new_communities = defaultdict(list)
    final_threshold = 0.25
    
    for v in G.nodes():
        if v not in mem or not mem[v]:
            continue
        
        total = sum(mem[v].values())
        if total == 0:
            continue
            
        for label, count in mem[v].items():
            if count / total >= final_threshold:
                new_communities[label].append(v)
                
    return dict(new_communities), mem
