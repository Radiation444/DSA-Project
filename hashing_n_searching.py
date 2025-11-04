table_size = 10**7 #for hash table
p = 37 #for polynomial rolling hash

def poly_roll_hash(s):
    h = 0
    m = len(s)
    m -= 1
    for char in s:
        h+= ord(char) * (p**m) % table_size
        m-= 1
    return h

class Node:
    def __init__(self,value):
        self.value = value
        self.nx = None

    def update_next(self,nxt):
        self.nx = nxt


class Table:
    def __init__(self,size = table_size):
        self.size = size
        self.table = [None] * size

    def ins(self,s):
        index = poly_roll_hash(s)
        curr = self.table[index]
        if curr:
            while curr.nx:
                curr = curr.nx
            nd = Node(s)
            curr.nx = nd
        else:
            curr = Node(s)
            self.table[index] = curr
