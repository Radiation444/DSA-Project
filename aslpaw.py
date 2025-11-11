import random
import json
from collections import defaultdict, Counter

def ASLPAw(graph: dict, iterations: int = 30):
    comm_labels = defaultdict(list)
    for node in graph.keys():
        comm_labels[node].append(node)
    for _t in range(iterations):
        nodes_list = list(graph.keys())
        random.shuffle(nodes_list)
        for node in nodes_list:
            label_votes = defaultdict(float)
            if node not in graph:
                continue
            # --- Speaker Part ---
            for neighbor, weight_of_edge in graph[node]:
                if neighbor in comm_labels and comm_labels[neighbor]:
                    spoken_label = random.choice(comm_labels[neighbor])
                    label_votes[spoken_label] += weight_of_edge
            # --- Listener Part ---
            if label_votes:
                best_label = max(label_votes, key=label_votes.get)
            else:
                best_label = comm_labels[node][0] 
            
            comm_labels[node].append(best_label)

    result_graph = defaultdict(dict)
    for node, all_labels in comm_labels.items():
        label_frequencies = Counter(all_labels)
        total_labels = len(all_labels) 
        if total_labels == 0: 
            continue
        for label, count in label_frequencies.items():
            weight = count / total_labels
            result_graph[str(node)][str(label)] = {'weight': weight}
    return dict(result_graph)

def infer_overlapping_communities(results: dict, threshold: float = 0.1) -> dict:
    final_communities = defaultdict(list)
    for node, labels in results.items():
        if not labels:
            final_communities[node] = []
            continue
            
        for label, data in labels.items():
            if data['weight'] >= threshold:
                final_communities[node].append(label)
                
    return dict(final_communities)

def print_communities_by_member(overlapping_results: dict):
    community_members = defaultdict(list)
    for node, community_list in overlapping_results.items():
        for community_label in community_list:
            community_members[community_label].append(str(node))
            
    for community_label in sorted(community_members.keys(), key=int):
        members = community_members[community_label]
        members.sort(key=int)
        member_string = ", ".join(members)
        print(f"community {community_label} has members: {member_string}")

def add_edge(graph, edge_list, weight):
    for u, v in edge_list:
        graph[u].append((v, weight))
        graph[v].append((u, weight))

def main():
    random.seed(42)
    G_example = defaultdict(list)
    engineering_clique = [(0, 1), (0, 2), (1, 2)]
    marketing_clique = [(3, 4), (3, 5), (4, 5)]
    sales_clique = [(6, 7), (6, 8), (7, 8)]
    add_edge(G_example, engineering_clique, 5)
    add_edge(G_example, marketing_clique, 5)
    add_edge(G_example, sales_clique, 5)
    add_edge(G_example, [(9, 1)], 3)
    add_edge(G_example, [(9, 3)], 3)
    add_edge(G_example, [(10, 2)], 2)
    add_edge(G_example, [(10, 4)], 2)
    add_edge(G_example, [(10, 6)], 2)
    G_example = dict(G_example)
    raw_community_results = ASLPAw(G_example, iterations=30)

    overlapping_communities = infer_overlapping_communities(
        raw_community_results, 
        threshold=0.1 
    )
    print_communities_by_member(overlapping_communities)
main()