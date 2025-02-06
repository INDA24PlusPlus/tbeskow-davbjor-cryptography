from server import server
import hashlib
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class tree:
    def __init__(self, l, r):
        self.l = l

        self.r = r
        self.hash = ""
        if r-l == 1: return
        mid = (l + r) / 2
        self.lnode = tree(l, mid)
        self.rnode = tree(mid, r)


    def insert(self, hash, index):
        if self.r-self.l == 1:
            self.hash = hash
        else:
            if index < self.lnode.r:
                self.lnode.insert(hash, index)
            else:
                self.rnode.insert(hash, index)
            self.hash = hashlib.sha256((self.lnode.hash+self.rnode.hash).encode()).hexdigest()

    def remove(self, hash, index):
        self.insert(hash, index)

    def get_hash(self, index):
        if self.r-self.l == 1:
            return self.hash

        if index < self.lnode.r: self.lnode.get_hash(index)
        else: self.rnode.get_hash(index)
        return self.hash


class client:
    def __init__(self, password):
        self.tree = tree(0, 128)
        self.salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=1000000
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(self.key)



    def save_data(self, data, index):
        data = self.fernet.encrypt(data.encode())
        server_hash = server.save(data, index) # faktiskt säkert och via nätverk måste fixas

        client_hash = hashlib.sha256(data).hexdigest()
        self.tree.insert(client_hash, index)
        if client_hash != server_hash:


            print("Imposter!!")

            self.tree.remove(hash, index)


    def get_data(self, index):
        data, server_hash = server.get(index)
        if server_hash != self.tree.get_hash(index):
            print("Imposter!")
            return None

        return self.fernet.decrypt(data).decode()



client = client("password")
client.save_data("Hello", 0)
client.save_data("Hello 2", 1)
print(client.get_data(1))
print(client.get_data(0))
