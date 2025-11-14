import networkx as nx
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from textwrap import shorten
from collections import defaultdict
import slpa_dynamic
import recommend


# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Kind of a databse for the graph state (stores the entire graph in memory)
G = nx.Graph()
communities = {}
mem = {}

# Global variables for post
post_db = {}
post_creator_db = {}
post_likes_db = defaultdict(set) # post_id -> {user1, user2}
user_likes_db = defaultdict(set) # user_id -> {post1, post2}
next_post_id = 1
hidden_scores = defaultdict(int) 



# Helper function 
def get_full_graph_state(critical_nodes=None, changed_edges=None):
    """
    Creates a complete JSON-serializable snapshot of the current
    graph state, formatted for the vis.js frontend.
    (This function is unchanged)
    """
    if critical_nodes is None:
        critical_nodes = set()
    if changed_edges is None:
        changed_edges = set()

    vis_nodes = []
    comm_map = {node: i for i, members in enumerate(communities.values()) for node in members}

    for node in G.nodes():
        node_data = {
            "id": node,
            "label": str(node)
        }
        if node in critical_nodes:
            node_data["color"] = "#FF6B6B"
            node_data["size"] = 25
        if node in comm_map:
            node_data["group"] = comm_map[node]
        vis_nodes.append(node_data)

    vis_edges = []
    for u, v, data in G.edges(data=True):
        edge_data = {
            "from": u,
            "to": v,
            "label": str(data.get('weight', 1))
        }
        if (u, v) in changed_edges or (v, u) in changed_edges:
            edge_data["color"] = {"color": "#6BFF6B", "highlight": "#7CFF7C"}
            edge_data["width"] = 3
        vis_edges.append(edge_data)

    comm_list = []
    seen = set()
    for idx, (lab, members) in enumerate(sorted(communities.items(), key=lambda x: -len(x[1]))):
        members_str = ", ".join(map(str, sorted(members)))
        members_str_short = shorten(members_str, width=50, placeholder="...")
        if members_str not in seen:
            comm_list.append(f"Group {idx + 1}: [{members_str_short}]")
        seen.add(members_str)

    return {
        "nodes": vis_nodes,
        "edges": vis_edges,
        "community_list": comm_list
    }


def _increment_weight(u, v, amount):
    """
    Safely adds weight to the global graph G.
    (This function is unchanged)
    """
    u = int(u)
    v = int(v)

    if u == v:
        return
    if not G.has_node(u) or not G.has_node(v):
        print(f"Warning: Cannot add edge between non-existent nodes {u} and {v}")
        return

    if G.has_edge(u, v):
        current_weight = G[u][v].get('weight', 0)
    else:
        current_weight = 0

    new_weight = current_weight + amount
    G.add_edge(u, v, weight=new_weight)
    print(f"    -> Weight {u}-{v} updated to {new_weight}")


def _increment_hidden_score(u, v, amount):
    """
    Increments the hidden score for a pair of users.
    (This function is unchanged)
    """
    u = int(u)
    v = int(v)

    if u == v:
        return 

    key = tuple(sorted((u, v)))
    hidden_scores[key] += amount
    print(f"    -> Hidden score {key} updated to {hidden_scores[key]}")




# Api endpoints

@app.route('/')
def home():
    """Serves the frontend HTML page."""
    return render_template('index.html')

@app.route('/api/init', methods=['POST'])
def api_init_graph():
    """
    Initializes or resets the graph.
    Also resets the entire post system and hidden scores.
    """
    print("Initializing/Resetting Graph...")
    global G, communities, mem
    global post_db, post_creator_db, post_likes_db, user_likes_db, next_post_id, hidden_scores # <-- user_likes_db added

    # Reset Graph
    G = nx.Graph()
    data = request.json
    edge_data = data.get("edge_data", "")

    post_db = {}
    post_creator_db = {}
    post_likes_db.clear()
    user_likes_db.clear()  
    next_post_id = 1
    hidden_scores.clear() 
    # --- End New ---

    try:
        # Build graph (original logic)
        for line in edge_data.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) == 3:
                u, v, w = map(int, parts)
            else:
                u, v = map(int, parts)
                w = 1
            G.add_edge(u, v, weight=w)

        # Add nodes that might not have edges
        for line in edge_data.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split()
            for node in parts[:2]:
                if not G.has_node(int(node)):
                    G.add_node(int(node))

        communities, mem = slpa_dynamic.run_slpa(G)
        response = get_full_graph_state()
        return jsonify(response)

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 400


@app.route('/api/modify', methods=['POST'])
def api_modify_graph():
    """
    Handles all graph modifications (add/remove node/edge).
    (Original logic, unchanged)
    """
    global G, communities, mem
    data = request.json
    action = data.get("action")
    action_data = data.get("data")
    change_buffer = []
    highlight_edges = set()

    try:
        if action == "add_node":
            u = int(action_data[0])
            change_buffer.append(("add_node", u))
        elif action == "remove_node":
            u = int(action_data[0])
            change_buffer.append(("remove_node", u))
        elif action == "add_edge":
            u, v, w = map(int, action_data)
            change_buffer.append(("add_edge", (u, v, w)))
            highlight_edges.add((u, v))
        elif action == "remove_edge":
            u, v = map(int, action_data)
            change_buffer.append(("remove_edge", (u, v)))
            highlight_edges.add((u, v))
        elif action == "change_weight":
            u, v, w = map(int, action_data)
            change_buffer.append(("remove_edge", (u, v)))
            change_buffer.append(("add_edge", (u, v, w)))
            highlight_edges.add((u, v))
        else:
            return jsonify({"error": "Invalid action"}), 400

        if change_buffer:
            communities, mem = slpa_dynamic.dynamic_slpa(G, mem, communities, change_buffer)

        return jsonify(get_full_graph_state(changed_edges=highlight_edges))
    except Exception as e:
        return jsonify({"error": f"Error processing {action}: {e}"}), 400


@app.route('/api/recommend/<int:node_id>', methods=['GET'])
def api_recommend(node_id):
    """
    Gets friend recommendations (Jaccard).
    (Original logic, unchanged)
    """
    if node_id not in G:
        return jsonify({"recommendations": [], "message": f"Node {node_id} not in graph."})

    possible_candidates = recommend.get_friend_recommendations(G, node_id)
    return jsonify({
        "node": node_id,
        "recommendations": possible_candidates,
        "message": "Jaccard analysis complete."
    })


@app.route('/api/attack', methods=['GET'])
def api_attack():
    """
    Runs the full attack simulation.
    """
    if len(G.nodes) < 3:
        return jsonify({"error": "Graph too small to analyze."}), 400

    tester = recommend.NetworkResilience(G)
    critical_nodes = tester.get_articulation_points()

    if not critical_nodes:
        return jsonify({
            "message": "System is Robust (No Cut Vertices).",
            "critical_nodes": [], "simulation_stats": [],
            "graph_state": get_full_graph_state(critical_nodes=[])
        })

    stats = tester.simulate_ap_attack(critical_nodes)
    chart_data = {
        "labels": [s[0] for s in stats],
        "data": [s[1] for s in stats]
    }

    return jsonify({
        "message": f"Detected {len(critical_nodes)} Critical Nodes: {critical_nodes}",
        "critical_nodes": critical_nodes,
        "simulation_stats": chart_data,
        "graph_state": get_full_graph_state(critical_nodes=set(critical_nodes))
    })


# Post system endpoints ---

@app.route('/api/posts', methods=['GET'])
def get_all_posts():
    """
    Gets all posts for the feed.
    (Original logic, unchanged)
    """
    posts_list = []
    for post_id, text in post_db.items():
        creator = post_creator_db.get(post_id, "Unknown")
        likes = len(post_likes_db.get(post_id, set()))
        posts_list.append({
            "id": post_id,
            "text": text,
            "creator": creator,
            "likes": likes
        })
    posts_list.sort(key=lambda x: int(x["id"][1:]), reverse=True)
    return jsonify(posts_list)


@app.route('/api/post/create', methods=['POST'])
def create_post():
    """
    Creates a new post.
    Also updates user_likes_db
    """
    global next_post_id
    data = request.json
    user = int(data.get("user"))
    text = data.get("text")

    if not G.has_node(user):
        return jsonify({"error": f"User {user} does not exist in the graph."}), 400
    if not text:
        return jsonify({"error": "Post text cannot be empty."}), 400

    post_id = f"P{next_post_id}"
    next_post_id += 1

    post_db[post_id] = text
    post_creator_db[post_id] = user
    post_likes_db[post_id].add(user)  # Creator is the first "liker"
    user_likes_db[user].add(post_id) #  Add to reverse mapping

    print(f"User {user} created post {post_id}")

    return jsonify({
        "id": post_id,
        "text": text,
        "creator": user,
        "likes": 1
    })


@app.route('/api/post/like', methods=['POST'])
def like_post():
    """
    Likes a post and updates graph weights OR hidden scores based on new logic.
    Also updates user_likes_db
    """
    data = request.json
    user_id = int(data.get("user"))
    post_id = data.get("post_id")

    if not G.has_node(user_id):
        return jsonify({"error": f"Liker {user_id} does not exist."}), 400
    if post_id not in post_db:
        return jsonify({"error": f"Post {post_id} does not exist."}), 400

    if user_id in post_likes_db[post_id]:
        return jsonify({"error": "User has already liked this post."}), 400

    creator_id = post_creator_db[post_id]
    other_likers = post_likes_db[post_id] - {user_id}

    print(f"--- Liking Post {post_id} (User: {user_id}) ---")

    # Liker-to-Creator Logic
    if user_id != creator_id: 
        if G.has_edge(user_id, creator_id):
            _increment_weight(user_id, creator_id, 10)
        else:
            _increment_hidden_score(user_id, creator_id, 10)

    # Liker-to-Mutuals Logic
    for other_liker in other_likers:
        if user_id == other_liker: continue
        
        if G.has_edge(user_id, other_liker):
            _increment_weight(user_id, other_liker, 5)
        else:
            _increment_hidden_score(user_id, other_liker, 5)

    # 3. Save the new like
    post_likes_db[post_id].add(user_id)
    user_likes_db[user_id].add(post_id) #Add to reverse mapping

    print(f"--- Like Complete ---")

    # 4. Return new graph state to refresh vis.js
    return jsonify(get_full_graph_state())


@app.route('/api/recommend-by-weight/<int:node_id>', methods=['GET'])
def recommend_by_weight(node_id):
    """
    Returns Jaccard recs AND users with hidden score > 50.
    """
    if not G.has_node(node_id):
        return jsonify({"error": f"Node {node_id} not in graph."}), 404

    recommendations = {}

    # 1. Get Jaccard Recs
    jaccard_recs = recommend.get_friend_recommendations(G, node_id)
    for rec_id in jaccard_recs:
        if rec_id not in recommendations:
            recommendations[rec_id] = {"user": rec_id, "weight": 0, "reason": "Jaccard"}

    # 2. Get Hidden Score Recs
    for (u, v), score in hidden_scores.items():
        if score <= 50:
            continue
            
        target_rec = -1
        if u == node_id:
            target_rec = v
        elif v == node_id:
            target_rec = u
        
        if target_rec != -1:
            if target_rec in recommendations:
                recommendations[target_rec]["weight"] = score
                recommendations[target_rec]["reason"] += " & Hidden Score"
            else:
                recommendations[target_rec] = {"user": target_rec, "weight": score, "reason": "Hidden Score"}

    final_list = list(recommendations.values())
    final_list.sort(key=lambda x: x["weight"], reverse=True)

    return jsonify(final_list)


# Post recommendation endpoint
@app.route('/api/recommend-posts/<int:user_id>', methods=['GET'])
def api_recommend_posts(user_id):
    """
    Gets post recommendations for a user based on similar users' likes.
    """
    if not G.has_node(user_id):
        return jsonify({"error": f"User {user_id} does not exist."}), 404

    recs = recommend.get_post_recommendations(user_id, user_likes_db)
    
    return jsonify({"recommendations": recs})


@app.route('/api/bipartite-graph', methods=['GET'])
def api_get_bipartite_graph():
    """
    Generates and returns the node/edge list for the user-post bipartite graph.
    """
    vis_nodes = []
    vis_edges = []
    
    users = set()
    posts = set()
    
    for user_id, liked_posts in user_likes_db.items():
        users.add(user_id)
        posts.update(liked_posts)
        for post_id in liked_posts:
            vis_edges.append({
                "from": f"u_{user_id}", 
                "to": f"p_{post_id}"
            })
            
    for u in users:
        vis_nodes.append({
            "id": f"u_{u}",
            "label": f"User {u}",
            "group": 0, # User group
            "shape": "dot",
            "color": "#4ecdc4"
        })
        
    for p in posts:
        vis_nodes.append({
            "id": f"p_{p}",
            "label": p,
            "group": 1, # Post group
            "shape": "box",
            "color": "#FF6B6B"
        })

    return jsonify({"nodes": vis_nodes, "edges": vis_edges})


if __name__ == "__main__":
    print("Flask server running...")
    print("Access the frontend at: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)