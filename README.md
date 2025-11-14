🚀 Dynamic Social Network Analyzer

A full-stack, interactive platform for visualizing, analyzing, and experimenting with dynamic social networks.
The application supports real-time graph manipulation, community detection, hybrid recommendation systems, and network vulnerability analysis — all through a modern web interface.

(Tip: Add a screenshot or GIF demo here to showcase the UI!)

🌟 Features
🔹 Dynamic Graph Visualization

Add, remove, and modify nodes (users) and edges (friendships).

Weighted edges update automatically based on user interactions.

Built using vis.js for interactive graph manipulation.

🔹 Social Feed System

Users can create text-based posts.

Posts can be liked, which affects hidden affinity scores in the network graph.

🔹 Community Detection (SLPA)

Identifies overlapping communities using the Speaker-Listener Label Propagation Algorithm.

Communities are visualized in real-time.

🔹 Hybrid Recommendation System
👥 Friend Recommendations

Combines:

Jaccard similarity (mutual friends)

Hidden scores based on post-like behavior

📝 Post Recommendations

Collaborative filtering suggests posts liked by similar users.

🔹 Network Vulnerability Analysis

Detects articulation points (critical nodes).

Highlights nodes whose removal fragments the network.

🔹 Bipartite Graph Visualization

Separate graph showing user–post interactions.

Helps analyze engagement patterns.

🛠️ Technology Stack
Backend

Python 3

Flask

NetworkX

Flask-CORS

Matplotlib (optional/diagnostics)

Frontend

HTML5

CSS3

JavaScript (ES6+)

vis.js for graph rendering

📁 Project Structure

Your directory should look like this:

/your-project-root
├── api_main.py         # Flask server entry point
├── recommend.py        # Recommendation algorithms
├── slpa_dynamic.py     # SLPA community detection engine
├── templates/
│   └── index.html      # Frontend UI
├── static/
│   └── graph.js        # Frontend JS for graph actions
└── README.md           # Project documentation

⚙️ Installation & Setup
1️⃣ Clone the repo
git clone <your-repo-url>
cd your-project-root

2️⃣ (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

3️⃣ Install dependencies
pip install Flask networkx Flask-Cors matplotlib


Or use requirements.txt:

pip install -r requirements.txt

▶️ Running the Application

Start the Flask server:

python api_main.py


Then open your browser at:

http://127.0.0.1:5000

📖 API Documentation
Main

GET /
Serves the main UI.

Graph Management

POST /api/init
Initializes or resets the social graph and clears post/score data.

POST /api/modify
Adds or removes nodes/edges.

GET /api/bipartite-graph
Returns user-post interaction graph.

Analysis & Recommendations

GET /api/recommend/<node_id>
Friend recommendations using Jaccard similarity.

GET /api/recommend-by-weight/<node_id>
Hybrid friend recommendations combining Jaccard + hidden scores.

GET /api/recommend-posts/<user_id>
Post recommendations using collaborative filtering.

GET /api/attack
Finds articulation points and returns graph annotated with critical nodes.

Posts & Social Actions

GET /api/posts
Fetch all posts.

POST /api/post/create
Create a new post for a user.

POST /api/post/like
Like a post — updates edge weights & hidden scores.