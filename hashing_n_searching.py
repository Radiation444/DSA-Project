table_size = 10**7 + 7
pr = 37

def poly_roll_hash(s, p):
    h = 0
    for char in s:
        h = (h * p + ord(char)) % table_size
    return h

def next_idx(s, i):
    h1 = poly_roll_hash(s, 31)
    h2 = poly_roll_hash(s, pr)
    if h2 == 0:
        h2 = 1
    return (h1 + i * h2) % table_size

class Node:
    def __init__(self, value):
        self.value = value
        self.probe_dist = 0
        self.deleted = 0

class Table:
    def __init__(self, size = table_size):
        self.size = size
        self.table = [None] * size

    def ins(self, s):
        home = poly_roll_hash(s, pr) % self.size
        pd = 0
        i = 0
        new_entry = Node(s)
        curr = None

        while True:
            idx = next_idx(s, i)
            curr = self.table[idx]

            if curr is None or curr.deleted:
                new_entry.probe_dist = pd
                self.table[idx] = new_entry
                return True

            if curr.value == s:
                return False

            if new_entry.probe_dist > curr.probe_dist:
                self.table[idx], new_entry = new_entry, curr

            i += 1
            pd += 1
            new_entry.probe_dist += 1