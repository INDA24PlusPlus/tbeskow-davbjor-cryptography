import hashlib

class tree:
    def __init__(self, l, r):
        self.l = l
        self.r = r
        self.hash = ""
        self.data = None
        if r-l == 1: return
        mid = (l + r) / 2
        self.lnode = tree(l, mid)
        self.rnode = tree(mid, r)


    def insert(self, data, hash, index):
        if self.r-self.l == 1:
            self.hash = hash
            self.data = data
        else:
            if index < self.lnode.r:
                self.lnode.insert(data, hash, index)
            else:
                self.rnode.insert(data, hash, index)
            self.hash = hashlib.sha256((self.lnode.hash + self.rnode.hash).encode()).hexdigest()

    def remove(self, hash, index):
        self.insert(hash, index)

    def get_hash(self, index):

        if self.r-self.l > 1:
            if index < self.lnode.r: self.lnode.get_hash(index)
            else: self.rnode.get_hash(index)
        return self.hash

    
    def get_data(self, index):
        if self.r-self.l == 1:
            return self.data
        if index < self.lnode.r: return self.lnode.get_data(index)
        else: return self.rnode.get_data(index)


class server:
    def __init__(self):

        self.tree = tree(0, 128)

    def save(self, data, index):
        hash = hashlib.sha256(data).hexdigest()
        self.tree.insert(data, hash, index)
        return hash


    def get(self, index):
        return self.tree.get_data(index), self.tree.get_hash(index)



server = server()
