from server import server
import hashlib

class tree:
    def __init__(self, l, r):
        self.l = l
        self.r = r
        self.hash = 0
        if r-l == 1: return
        mid = (l + r) / 2
        self.lnode = tree(l, mid)
        self.rnode = tree(mid, r)


    def insert(self, hash, index):
        self.hash ^= hash
        if self.r-self.l > 1:
            if index < self.lnode.r:
                self.lnode.insert(hash, index)
            else:
                self.rnode.insert(hash, index)

    def remove(self, hash, index):
        self.insert(hash, index)

    def get_hash(self, index):
        if self.r-self.l == 1:
            return [self.hash]

        res = [self.hash]
        if index < self.lnode.r: res.extend(self.lnode.get_hash(index))
        else: res.extend(self.rnode.get_hash(index))
        return res



class client:
    def __init__(self):
        self.tree = tree(0, 128)


    def save_data(self, message, index):
        path_hash = server.save(message, index) # faktiskt säkert och via nätverk måste fixas

        hash = int(hashlib.sha256(message.encode()).hexdigest(), 16)
        self.tree.insert(hash, index)
        if hash != path_hash:
            print("Imposter!!")
            self.tree.remove(hash, index)


    def get_data(self, index):
        data, path_hash = server.get(index)
        if path_hash != self.tree.get_hash(index):
            print("Imposter!")
            return None
        return data



client = client()
client.save_data("Hello", 0)
client.save_data("Hello 2", 1)
print(client.get_data(1))
print(client.get_data(0))
