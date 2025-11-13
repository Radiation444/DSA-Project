import recommend
import slpa_dynamic
import networkx as nx
import matplotlib.pyplot as plt
from textwrap import shorten
import sys

# ==========================================
# VISUALIZATION FUNCTIONS (SAFE / BLOCKING MODE)
# ==========================================

def plot_resilience_curve(stats):
    """ Plots the attack simulation results. """
    x = [s[0] for s in stats]
    y = [s[1] for s in stats]
    
    plt.figure(figsize=(8, 5))
    plt.plot(x, y, marker='o', linestyle='-', color='red', label='Targeted Attack')
    plt.title("Network Resilience Analysis")
    plt.xlabel("Critical Nodes Removed")
    plt.ylabel("Largest Connected Cluster Size")
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend()
    print(">> [System] Close the plot window to return to menu...")
    plt.show() 

def show_graph_with_communities(G, communities, changed_edges=None, title=None, critical_nodes=None):
    """ 
    Draws the graph. 
    Halts the program until you close the window (prevents freezing).
    """
    plt.figure(figsize=(11, 7)) 
    
    pos = nx.spring_layout(G, seed=42)

    # 1. Nodes
    node_colors = ["#6baed6"] * len(G.nodes())
    node_sizes = [400] * len(G.nodes())
    
    if critical_nodes:
        node_list = list(G.nodes())
        for i, node in enumerate(node_list):
            if node in critical_nodes:
                node_colors[i] = "red"
                node_sizes[i] = 800
    
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors)
    nx.draw_networkx_labels(G, pos, font_size=9, font_color="white", font_weight="bold")

    # 2. Edges
    default_edges, highlighted = [], []
    for u, v in G.edges():
        if changed_edges and ((u, v) in changed_edges or (v, u) in changed_edges):
            highlighted.append((u, v))
        else:
            default_edges.append((u, v))
    
    nx.draw_networkx_edges(G, pos, edgelist=default_edges, alpha=0.4)
    if highlighted:
        nx.draw_networkx_edges(G, pos, edgelist=highlighted, width=2.5, style='dashed', edge_color="green")

    # 3. Community Text Box
    comm_items = sorted(communities.items(), key=lambda x: (-len(x[1]), str(x[0])))
    lines = []
    seen = set()
    for idx, (lab, members) in enumerate(comm_items, start=1):
        members_str = ", ".join(map(str, sorted(members)))
        members_str = shorten(members_str, width=50, placeholder="...")
        if members_str not in seen:
            lines.append(f"Group {idx}: [{members_str}]")
        seen.add(members_str)
    
    comm_text = "\n".join(lines) if lines else "No communities detected"
    
    plt.title(title or "Network State")
    plt.axis("off")
    
    if critical_nodes:
        plt.plot([], [], 'o', color='red', label='Critical Point')
        plt.plot([], [], 'o', color='#6baed6', label='Normal Node')
        plt.legend(loc='upper left')

    ax = plt.gca()
    props = dict(boxstyle='round', facecolor='white', alpha=0.9)
    ax.text(1.02, 0.5, comm_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='center', bbox=props)
    plt.subplots_adjust(right=0.70)

    print(">> [System] Displaying Graph... Close the window to type more commands.")
    plt.show()

# ==========================================
# MAIN CONTROLLER
# ==========================================

def main():
    print("--- DYNAMIC COMMUNITY SYSTEM (MANUAL SHOW MODE) ---")
    
    try:
        # 1. INPUT PHASE
        line = input("Enter n (nodes) and m (edges): ")
        if not line: return
        n, m = map(int, line.split())
        G = nx.Graph()
        for i in range(m):
            line = input(f"Edge {i+1} (x y weight): ")
            x, y, w = map(int, line.split())
            G.add_edge(x, y, weight=w)
    except ValueError:
        print("Invalid input. Please restart.")
        return

    # 2. INITIAL CALCULATION
    communities, mem = slpa_dynamic.run_slpa(G)
    
    print("\n[System] Initial setup complete.")
    print("The graph will now pop up. CLOSE IT to start entering commands.")
    show_graph_with_communities(G, communities, title="Initial Network State")

    change_buffer = []

    print("\n--- COMMAND MENU ---")
    print(" 1. add_edge u v w         5. attack")
    print(" 2. remove_edge u v        6. recommend u")
    print(" 3. add_node u             7. show")
    print(" 4. remove_node u          8. exit")
    print(" 9. change_weight u v w")

    while True:
        try:
            cmd = input("\nCommand > ").strip()
        except EOFError:
            break
            
        if cmd == "exit":
            break
        
        parts = cmd.split()
        if not parts: continue

        # --- FEATURE 1: ATTACK SIMULATION ---
        # --- FEATURE 1: ATTACK SIMULATION ---
        if parts[0] == "attack":
            # 1. AUTO-UPDATE: Apply any pending changes to G before attacking
            if change_buffer:
                print(f"[System] Applying {len(change_buffer)} buffered changes before analysis...")
                # This updates G and the community memory 'mem'
                communities, mem = slpa_dynamic.dynamic_slpa(G, mem, communities, change_buffer)
                change_buffer = [] # Clear buffer since we just applied them

            # 2. Safety Check
            if len(G.nodes) < 3:
                print("Graph too small.")
                continue
            
            # 3. Create a FRESH instance of the class with the UPDATED G
            # This ensures 'recommend.py' gets the latest edges
            tester = recommend.NetworkResilience(G)
            
            critical_nodes = tester.get_articulation_points()
            
            if not critical_nodes:
                print("System is Robust (No Cut Vertices).")
            else:
                print(f"Detected {len(critical_nodes)} Critical Nodes: {critical_nodes}")
                
                # Show Red Nodes
                show_graph_with_communities(G, communities, title="CRITICAL VULNERABILITIES", critical_nodes=critical_nodes)
                
                confirm = input("Run Simulation? (y/n): ")
                if confirm.lower() == 'y':
                    stats = tester.simulate_ap_attack(critical_nodes)
                    plot_resilience_curve(stats)
                    
                    # Restore View (Show the graph destroyed or recovered)
                    show_graph_with_communities(G, communities, title="Post-Simulation State")
            continue

        # --- FEATURE 2: RECOMMENDATION ---
        if parts[0] == "recommend":
            if len(parts) < 2:
                print("Usage: recommend <node_id>")
                continue
            try:
                target = int(parts[1])
                recommend.get_friend_recommendations(G, target)
            except ValueError:
                print("Node ID must be an integer.")
            continue

        # --- FEATURE 3: DYNAMIC UPDATES & SHOW ---
        try:
            if parts[0] == "add_node":
                change_buffer.append(("add_node", int(parts[1])))
                print(f"   -> Buffered: Add Node {parts[1]}")
            
            elif parts[0] == "remove_node":
                change_buffer.append(("remove_node", int(parts[1])))
                print(f"   -> Buffered: Remove Node {parts[1]}")
            
            elif parts[0] == "add_edge":
                u, v, w = map(int, parts[1:])
                change_buffer.append(("add_edge", (u, v, w)))
                print(f"   -> Buffered: Add Edge {u}-{v}")
            
            elif parts[0] == "remove_edge":
                u, v = map(int, parts[1:])
                change_buffer.append(("remove_edge", (u, v)))
                print(f"   -> Buffered: Remove Edge {u}-{v}")

            # <<< NEW FEATURE ADDED HERE >>>
            elif parts[0] == "change_weight":
                u, v, w = map(int, parts[1:])
                # Simulate change by removing then adding
                change_buffer.append(("remove_edge", (u, v)))
                change_buffer.append(("add_edge", (u, v, w)))
                print(f"   -> Buffered: Change Weight {u}-{v} to {w}")
            
            elif parts[0] == "show":
                highlight_edges = []
                
                # Only run processing if there is something in the buffer
                if change_buffer:
                    print(f"[System] Processing {len(change_buffer)} buffered changes...")
                    communities, mem = slpa_dynamic.dynamic_slpa(G, mem, communities, change_buffer)
                    highlight_edges = [c[1] for c in change_buffer if c[0] in ("add_edge", "remove_edge")]
                    change_buffer = [] 
                else:
                    print("[System] No new changes. Showing current state...")
                
                show_graph_with_communities(G, communities, changed_edges=highlight_edges, title="Updated Network State")
            
            else:
                print("Unknown command.")

        except ValueError:
            print("Invalid format. Usage example: change_weight 1 2 50")

if __name__ == "__main__":
    main()