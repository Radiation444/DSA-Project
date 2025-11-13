from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

class Recommender:
    def __init__(self):
        self.user_to_posts = defaultdict(set)
        self.post_to_users = defaultdict(set)
        self.post_text = {}
        self.next_post_id = 1   # posts will be P1, P2, P3...

    # -------------------------------
    # POST CREATION + INTERACTIONS
    # -------------------------------
    def create_post(self, user, text):
        post_id = f"P{self.next_post_id}"
        self.next_post_id += 1

        self.post_text[post_id] = text
        self.add_interaction(user, post_id)
        return post_id

    def add_interaction(self, user, post):
        """
        user → int
        post → "P1", "P2", ...
        """
        self.user_to_posts[user].add(post)
        self.post_to_users[post].add(user)

    def input_interactions(self):
        print("Enter interactions in the format: user post")
        print("Example: 1 P2  (meaning user 1 interacts with post P2)")
        print("Type 'done' to stop.\n")

        while True:
            s = input("interaction > ").strip()
            if s.lower() == "done":
                break
            try:
                user, post = s.split()
                user = int(user)        # convert to numeric user id
                self.add_interaction(user, post)
            except:
                print("Invalid format. Use: 1 P2")

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

    # -------------------------------
    # FRIEND RECOMMENDATION (NEW)
    # -------------------------------
    def recommend_friends(self, user, k=3):
        """
        Recommend similar users (friend suggestions)
        based on Jaccard similarity of post interactions.
        """
        if user not in self.user_to_posts:
            return []

        target = self.user_to_posts[user]
        sims = []

        for other_user, posts in self.user_to_posts.items():
            if other_user == user:
                continue

            sim = self.jaccard(target, posts)
            if sim > 0:
                sims.append((sim, other_user))

        sims.sort(reverse=True)
        return [u for _, u in sims[:k]]

    # -------------------------------
    # VISUALIZATION
    # -------------------------------
    def visualize(self):
        G = nx.Graph()

        users = list(self.user_to_posts.keys())
        posts = list(self.post_to_users.keys())

        G.add_nodes_from(users, bipartite=0)
        G.add_nodes_from(posts, bipartite=1)

        for u in users:
            for p in self.user_to_posts[u]:
                G.add_edge(u, p)

        pos = {}
        pos.update((u, (0, i)) for i, u in enumerate(users))
        pos.update((p, (1, i)) for i, p in enumerate(posts))

        plt.figure(figsize=(7, 5))
        nx.draw(G, pos, with_labels=True, node_size=1400)
        plt.title("User-Post Bipartite Graph")
        plt.show()


# -----------------------------------------
# MAIN EXECUTION
# -----------------------------------------
if __name__ == "__main__":
    R = Recommender()

    print("=== Add Interactions ===")
    R.input_interactions()

    print("\n=== Graph Visualization ===")
    R.visualize()

    print("\n=== Post Recommendations ===")
    user = int(input("Enter user number (e.g., 1): "))
    print("Recommended posts:", R.recommend(user))

    print("\n=== Friend Recommendations ===")
    user = int(input("Enter user number (e.g., 1): "))
    print("Recommended friends:", R.recommend_friends(user))
