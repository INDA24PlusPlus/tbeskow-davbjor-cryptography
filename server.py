import hashlib
import socket
import threading
import pickle

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
        if self.r-self.l == 1:
            self.hash = ""
            self.data = None
        else:
            if index < self.lnode.r:
                self.lnode.remove(hash, index)
            else:
                self.rnode.remove(hash, index)
            self.hash = hashlib.sha256((self.lnode.hash+self.rnode.hash).encode()).hexdigest()


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
    def __init__(self, host="127.0.0.1", port = 4004):
        self.treeList = [tree(0, 128)]
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(6)
        self.nextConnection = 0

        print(f"Server listening on {self.host}:{self.port}")


    def save(self, data, index, client_index):
        hash = hashlib.sha256(data).hexdigest()
        self.treeList[client_index].insert(data, hash, index)
        return hash


    def get(self, index, client_index):
        return self.treeList[client_index].get_data(index), self.treeList[client_index].get_hash(index)


    def handle_client(self, client_socket, client_index):
        while True:
            try:
                data = client_socket.recv(4096)
                if not data:
                    print("Client disconnected")
                    break

                request = pickle.loads(data)

                command = request.get("command")
                index = request.get("index")

                if command == "save":
                    data = request.get("data")
                    hash_value = self.save(data, index, client_index)
                    response = {"status": "ok", "hash": hash_value}

                elif command == "get":
                    data, hash_value = self.get(index, client_index)
                    response = {"status": "ok", "hash": hash_value, "data": data} # Vill vi skicka okrypterad data här?
                    
                else:
                    response = {"status": "error", "message": "No valid command"}
                
                client_socket.sendall(pickle.dumps(response))
                
            except (EOFError, pickle.UnpicklingError) as e:
                print(f"Error decoding data: {e}")
                break  # Stop processing this client

            except Exception as e:
                print(f"Server error: {e}")
                break  # Exit loop on unexpected errors

        client_socket.close()


    def start(self):
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection incoming from {address}")
            self.treeList.append(tree(0, 128))
            client_handler = threading.Thread(target = self.handle_client, args =(client_socket, self.nextConnection))
            client_handler.start()
            self.nextConnection += 1

if __name__ == "__main__":
    server = server()
    server.start()
