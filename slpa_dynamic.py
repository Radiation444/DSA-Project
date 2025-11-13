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

def show_graph_with_communities(G, communities, changed_edges=None, title=None):
    """
    Draw graph and overlay community list (C1:[...], C2:[...]) on the same figure.
    """
    plt.figure(figsize=(9, 6))
    pos = nx.spring_layout(G, seed=42)

    nx.draw_networkx_nodes(G, pos, node_size=400, node_color="#6baed6")
    nx.draw_networkx_labels(G, pos, font_size=8, font_color="white")

    default_edges, highlighted = [], []
    for u, v in G.edges():
        if changed_edges and ((u, v) in changed_edges or (v, u) in changed_edges):
            highlighted.append((u, v))
        else:
            default_edges.append((u, v))
    if default_edges:
        nx.draw_networkx_edges(G, pos, edgelist=default_edges, alpha=0.6)
    if highlighted:
        nx.draw_networkx_edges(G, pos, edgelist=highlighted, width=3.0, style='dashed', edge_color="red")

    comm_items = sorted(communities.items(), key=lambda x: (-len(x[1]), str(x[0])))
    lines = []
    seen=set()
    for idx, (lab, members) in enumerate(comm_items, start=1):
        members_list = sorted(members)
        members_str = ", ".join(map(str, members_list))
        members_str = shorten(members_str, width=180, placeholder="...")
        if(members_str not in seen):
            lines.append(f"C{idx}:[{members_str}]")
        seen.add(members_str)
    comm_text = "\n".join(lines) if lines else "No communities"

    plt.title(title or "Graph")
    plt.axis("off")
    ax = plt.gca()
    props = dict(boxstyle='round', facecolor='white', alpha=0.8)
    ax.text(1.02, 0.5, comm_text, transform=ax.transAxes, fontsize=9,
            verticalalignment='center', bbox=props)

    plt.subplots_adjust(right=0.75)
    plt.show()

def main():
    n, m = map(int, input("Enter n (nodes) and m (edges): ").split())
    G = nx.Graph()
    for i in range(m):
        x, y, w = map(int, input(f"Edge {i+1} (x y weight): ").split())
        G.add_edge(x, y, weight=w)

    communities, mem = run_slpa(G)
    show_graph_with_communities(G, communities, title="Initial Graph")

    change_buffer = []
    change_count = 0

    while True:
        cmd = input("\nEnter change (add_node u / remove_node u / add_edge u v w / remove_edge u v / change_weight u v w / exit): ").strip()
        if cmd == "exit":
            break

        parts = cmd.split()
        if parts[0] == "add_node":
            change_buffer.append(("add_node", int(parts[1])))
        elif parts[0] == "remove_node":
            change_buffer.append(("remove_node", int(parts[1])))
        elif parts[0] == "add_edge":
            u, v, w = map(int, parts[1:])
            change_buffer.append(("add_edge", (u, v, w)))
        elif parts[0] == "remove_edge":
            u, v = map(int, parts[1:])
            change_buffer.append(("remove_edge", (u, v)))
        elif parts[0] == "change_weight":
            u, v, w=map(int, parts[1:])
            change_buffer.append(("remove_edge",(u,v)))
            change_buffer.append(("add_edge",(u,v,w)))

        change_count += 1

        if change_count % 3 == 0:
            communities, mem = dynamic_slpa(G, mem, communities, change_buffer)
            show_graph_with_communities(G, communities, changed_edges=[
                c[1] for c in change_buffer if c[0] in ("add_edge", "remove_edge")
            ], title=f"Graph after {change_count} changes")
            change_buffer.clear()
main()