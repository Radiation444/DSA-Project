from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS


# --- Your Recommender Class (Unchanged) ---

class Recommender:
    def __init__(self):
        self.user_to_posts = defaultdict(set)
        self.post_to_users = defaultdict(set)
        self.post_text = {}
        self.next_post_id = 1  # posts will be P1, P2, P3...

    # -------------------------------
    # POST CREATION + INTERACTIONS
    # -------------------------------
    def create_post(self, user, text):
        post_id = f"P{self.next_post_id}"
        self.next_post_id += 1

        self.post_text[post_id] = text
        self.add_interaction(user, post_id)  # The creator also "interacts"
        return post_id

    def add_interaction(self, user, post):
        """
        user → int
        post → "P1", "P2", ...
        """
        # Ensure user is int for consistency
        self.user_to_posts[int(user)].add(post)
        self.post_to_users[post].add(int(user))

    # -------------------------------
    # SIMILARITY (Jaccard)
    # -------------------------------
    def jaccard(self, a, b):
        if not a and not b:
            return 0
        return len(a & b) / len(a | b)

    # -------------------------------
    # POST RECOMMENDATION
    # -------------------------------
    def recommend(self, user, k=3):
        if user not in self.user_to_posts:
            return []

        target_posts = self.user_to_posts[user]
        sims = []

        # compute similarity with all other users
        for other_user, posts in self.user_to_posts.items():
            if other_user == user:
                continue

            sim = self.jaccard(target_posts, posts)
            if sim > 0:
                sims.append((sim, other_user))

        sims.sort(reverse=True)
        similar_users = [u for _, u in sims[:k]]

        # recommend posts interacted by similar users
        rec_posts = set()
        for u in similar_users:
            for p in self.user_to_posts[u]:
                if p not in target_posts:
                    rec_posts.add(p)

        return list(rec_posts)

    # Note: recommend_friends and visualize are not used by the API
    # but are fine to keep.


# -----------------------------------------
# FLASK API SERVER
# -----------------------------------------

app = Flask(__name__)
CORS(app)  # Allows the frontend (browser) to call the backend

# Create a single, global instance of the recommender
R = Recommender()


# --- Seed Data (Create some users and posts on startup) ---
def seed_data():
    print("Seeding initial data...")
    # Create posts (P1 to P6)
    p1 = R.create_post(1, "Love the new Star Wars movie!")
    p2 = R.create_post(2, "Just finished a 10k run.")
    p3 = R.create_post(3, "Baking sourdough is my new hobby.")
    p4 = R.create_post(1, "This new sci-fi book is amazing.")
    p5 = R.create_post(2, "Training for a marathon is tough.")
    p6 = R.create_post(3, "My sourdough starter is named 'Doughbi-Wan'.")

    # Add initial likes to create similarities
    # Users 1 and 3 are similar (both like baking and sci-fi)
    # User 2 is different (running)
    R.add_interaction(1, p3)  # User 1 (sci-fi) also likes baking post
    R.add_interaction(3, p4)  # User 3 (baking) also likes sci-fi post

    # User 4 is a new user with no posts
    R.add_interaction(4, p1)  # User 4 likes Star Wars
    print("Seed data created.")


# --- API Endpoints ---

@app.route('/')
def home():
    """Serves the frontend HTML page."""
    # Flask looks for this file in a folder named 'templates'
    return render_template('index.html')


@app.route('/users', methods=['GET'])
def get_users():
    """Returns a list of all users who have interacted."""
    users = sorted(list(R.user_to_posts.keys()))
    return jsonify(users)


@app.route('/posts', methods=['GET'])
def get_posts():
    """Returns all posts in the system."""
    # R.post_text is {"P1": "text", ...}
    return jsonify(R.post_text)


@app.route('/like', methods=['POST'])
def like_post():
    """Adds a 'like' (interaction) from a user for a post."""
    data = request.json
    user_id = data.get('user')
    post_id = data.get('postId')

    if not user_id or not post_id:
        return jsonify({"error": "User and PostID are required"}), 400

    R.add_interaction(int(user_id), post_id)
    print(f"Interaction added: User {user_id} liked {post_id}")
    return jsonify({"status": "success"})


@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """Gets post recommendations for a specific user."""
    rec_ids = R.recommend(user_id, k=5)

    # Convert the recommended post IDs back into text
    recommended_posts = []
    for pid in rec_ids:
        text = R.post_text.get(pid, "Unknown Post")
        recommended_posts.append({"id": pid, "text": text})

    return jsonify(recommended_posts)


# --- Main execution ---
if __name__ == "__main__":
    seed_data()
    app.run(debug=True, port=5000)