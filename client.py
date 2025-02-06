#from server import server
import hashlib
import os
import socket
import pickle
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


    def remove(self, index):
        if self.r-self.l == 1:
            self.hash = ""
        else:
            if index < self.lnode.r:
                self.lnode.remove(hash, index)
            else:
                self.rnode.remove(hash, index)
            self.hash = hashlib.sha256((self.lnode.hash+self.rnode.hash).encode()).hexdigest()


    def get_hash(self, index):
        if self.r-self.l == 1:
            return self.hash

        if index < self.lnode.r: self.lnode.get_hash(index)
        else: self.rnode.get_hash(index)
        return self.hash


class client:
    def __init__(self, password, host="127.0.0.1", port = 4004):
        self.tree = tree(0, 128)
        self.salt = os.urandom(16)
        self.port = port
        self.host = host
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))  # Keep connection open

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=1000000
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(self.key)


    def send_request(self, request):
        try:
            self.socket.sendall(pickle.dumps(request))

            response_data = self.socket.recv(4096)
            
            if not response_data:
                print("Empty response from server")
                return None

            response = pickle.loads(response_data)
            return response

        except (EOFError, pickle.UnpicklingError) as e:
            print(f"Error decoding server response: {e}")
            return None

        except Exception as e:
            print(f"Client error: {e}")
            return None


    def save_data(self, data, index):
        encr_data = self.fernet.encrypt(data.encode())
        request = {"command": "save", "data": encr_data, "index": index}
        response = self.send_request(request)
        #server_hash = server.save(encr_data, index) # faktiskt säkert och via nätverk måste fixas

        if response["status"] == "ok":
            server_hash = response["hash"]
            client_hash = hashlib.sha256(encr_data).hexdigest()
            self.tree.insert(client_hash, index)
            
            if client_hash != server_hash:
                print("Imposter!!")
                self.tree.remove(index)
            
        if "message" in response:
            msg = response["message"]
            print(f"Error reading data, {msg}")


    def get_data(self, index):
        request = {"command": "get", "index": index}
        response = self.send_request(request)

        if response["status"] == "ok":
            encr_data = response["data"]
            server_hash = response["hash"]

            if server_hash != self.tree.get_hash(index):
                print("Imposter!")
                return None

            return self.fernet.decrypt(encr_data).decode()

        if "message" in response:
            msg = response["message"]
            print(f"Error reading data, {msg}")
        return None


    def close(self):
        self.socket.close()

    
    def cli(self):
        print("Client started. Type 'save [index] [message]' or 'get [index]'. Type 'exit' to quit.")
        while True:
            try:
                command = input("> ").strip()
                if command.lower() == "exit":
                    print("Closing connection...")
                    self.close()
                    break
            
                parts = command.split(" ", 2)
                if len(parts) < 2:
                    continue
            
                # Parse the input
                action, index = parts[0], parts[1]
                if not index.isdigit():
                    print("Invalid index. Must be a number.")
                    continue
                index = int(index)

                # Save the message to the index
                if action.lower() == "save":
                    if len(parts) < 3:
                        print("Missing message. Usage: save [index] [message]")
                        continue
                    message = parts[2]
                    self.save_data(message, index)
    
                # Get the data at the index
                elif action.lower() == "get":
                    print(self.get_data(index))

                else:
                    print("Try again...")

            except KeyboardInterrupt:
                print("\nClosing connection...")
                self.close()
                break


client = client("password")
client.cli()
