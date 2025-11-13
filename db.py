#in development database using json for now

import json
import os


class SocialDB:
	def __init__(self, path="db.json"):
		self.path = path
		self.profiles = {}
		self.adj = {}
		self._load()

	def _load(self):
		if os.path.exists(self.path):
			try:
				with open(self.path, "r", encoding="utf-8") as fh:
					data = json.load(fh)
				self.profiles = data.get("profiles", {}) or {}
				self.adj = data.get("adj", {}) or {}
			except Exception:
				self.profiles = {}
				self.adj = {}

	def _save(self):
		with open(self.path, "w", encoding="utf-8") as fh:
			json.dump({"profiles": self.profiles, "adj": self.adj}, fh, ensure_ascii=False)

	def get_profile(self, username):
		return self.profiles.get(username)

	def add_user(self, username, **metadata):
		if username in self.profiles:
			return False
		profile = {"username": username}
		profile.update(metadata)
		self.profiles[username] = profile
		self.adj[username] = {}
		self._save()
		return True

	def remove_user(self, username):
		if username not in self.profiles:
			return False
		for friends in list(self.adj.values()):
			if username in friends:
				del friends[username]
		del self.profiles[username]
		if username in self.adj:
			del self.adj[username]
		self._save()
		return True

	def add_friend(self, username, friend_username, weight=0):
		if username == friend_username:
			return False
		if username not in self.profiles:
			self.add_user(username)
		if friend_username not in self.profiles:
			self.add_user(friend_username)
		self.adj.setdefault(username, {})
		self.adj.setdefault(friend_username, {})
		self.adj[username].setdefault(friend_username, weight)
		self.adj[friend_username].setdefault(username, weight)
		self._save()
		return True

	def remove_friend(self, username, friend_username):
		changed = False
		if username in self.adj and friend_username in self.adj[username]:
			del self.adj[username][friend_username]
			changed = True
		if friend_username in self.adj and username in self.adj[friend_username]:
			del self.adj[friend_username][username]
			changed = True
		if changed:
			self._save()
		return changed

	def message_friend(self, username, friend_username):
		if username == friend_username:
			return False
		if username not in self.profiles:
			self.add_user(username)
		if friend_username not in self.profiles:
			self.add_user(friend_username)
		self.adj.setdefault(username, {})
		self.adj.setdefault(friend_username, {})
		self.adj[username][friend_username] = self.adj[username].get(friend_username, 0) + 1
		self.adj[friend_username][username] = self.adj[friend_username].get(username, 0) + 1
		self._save()
		return True

