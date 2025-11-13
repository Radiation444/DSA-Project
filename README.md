how to use db.py 

- Create/load DB:
  from db import SocialDB
  db = SocialDB('sample_db.json')  # loads file if present

- Add user:
  db.add_user('alice')

- Get profile:
  db.get_profile('alice')

- Add friend:
  db.add_friend('alice', 'bob')

- Message friend (increments message count):
  db.message_friend('alice', 'bob')

- Remove friend:
  db.remove_friend('alice', 'bob')

- Remove user:
  db.remove_user('alice')

