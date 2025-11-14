# 🚀 Dynamic Social Network Analyzer

(NOTE TO THE USER: PLEASE ENSURE THAT EDGE WEIGHTS ARE GREATER THAN 30 IF YOU WANT TO SEE MEANINGFUL COMMUNITIES, BECAUSE THE ALGORITHM IS DESIGNED IN SUCH A WAY THAT EDGES BELOW 30 WEIGHT ARE NOT INCLUDED FOR LABEL PROPAGATION)

An interactive, full-stack platform for **visualizing**, **analyzing**, and **experimenting** with dynamic social networks. Easily manipulate graphs, detect communities, get recommendations, and analyze network vulnerabilities—all via a modern web interface.

---

## 🌟 Features

- **Dynamic Graph Visualization**
  - Add, remove, and modify nodes (users) and edges (friendships)
  - Edge weights update automatically based on user interactions
  - Built using [`vis.js`](https://visjs.org/) for interactive, real-time graph manipulation

- **Social Feed System**
  - Users can create text-based posts
  - Posts can be liked, affecting hidden affinity scores in the network

- **Community Detection (SLPA)**
  - Runs Speaker-Listener Label Propagation Algorithm for overlapping community detection
  - Visualizes communities live
  - (NOTE TO THE USER: PLEASE ENSURE THAT EDGE WEIGHTS ARE GREATER THAN 30 IF YOU WANT TO SEE MEANINGFUL COMMUNITIES, BECAUSE THE ALGORITHM IS      DESIGNED IN SUCH A WAY THAT EDGES BELOW 30 WEIGHT ARE NOT INCLUDED FOR LABEL PROPAGATION)
- **Hybrid Recommendation System**
  - **Friend Recommendations**
    - Jaccard similarity (mutual friends)
    - Plus weighted scores from post-like behaviors
  - **Post Recommendations**
    - Collaborative filtering: suggests posts liked by similar users

- **Network Vulnerability Analysis**
  - Detects and highlights articulation points (critical nodes)
  - Reveals nodes whose removal fragments the social network

- **Bipartite Graph Visualization**
  - Displays user–post interactions as a separate graph
  - Analyses engagement/interest patterns

---

## 🛠️ Technology Stack

**Backend**

- Python 3
- Flask
- NetworkX
- Flask-CORS
- Matplotlib (diagnostics/optional)

**Frontend**

- HTML5 / CSS3
- JavaScript (ES6+)
- vis.js for graph rendering

---

## 📁 Project Structure

```
/your-project-root
├── api_main.py         # Flask server entry point
├── recommend.py        # Recommendation algorithms
├── slpa_dynamic.py     # SLPA community detection engine
├── templates/
│   └── index.html      # Frontend UI
├── static/
│   └── graph.js        # Frontend JS for graph actions
└── README.md           # Project documentation
```

---

## ⚙️ Installation & Setup

1. **Clone the repository**
    ```bash
    git clone https://github.com/Radiation444/DSA-Project.git
    cd DSA-Project
    ```

2. **(Optional) Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate        # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**
    ```bash
    pip install Flask networkx Flask-Cors matplotlib
    ```
    Or with `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ Running the Application

Start the Flask server:
```bash
python api_main.py
```
Then visit [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 📖 API Documentation

### Main
- `GET /`  
  _Serves the main UI._

### Graph Management
- `POST /api/init`  
  Initializes or resets the social graph and clears post/score data.

- `POST /api/modify`  
  Adds or removes nodes/edges.

- `GET /api/bipartite-graph`  
  Returns user-post interaction graph.
-
(NOTE TO THE USER: PLEASE ENSURE THAT EDGE WEIGHTS ARE GREATER THAN 30 IF YOU WANT TO SEE MEANINGFUL COMMUNITIES, BECAUSE THE ALGORITHM IS DESIGNED IN SUCH A WAY THAT EDGES BELOW 30 WEIGHT ARE NOT INCLUDED FOR LABEL PROPAGATION)
### Analysis & Recommendations
- `GET /api/recommend/<node_id>`  
  Friend recommendations using Jaccard similarity.

- `GET /api/recommend-by-weight/<node_id>`  
  Hybrid friend recommendations combining Jaccard similarity and hidden scores.

- `GET /api/recommend-posts/<user_id>`  
  Post recommendations using collaborative filtering.

- `GET /api/attack`  
  Finds articulation points and returns graph annotated with critical nodes.

### Posts & Social Actions
- `GET /api/posts`  
  Fetch all posts.

- `POST /api/post/create`  
  Create a new post for a user.

- `POST /api/post/like`  
  Like a post; updates edge weights & hidden scores.
