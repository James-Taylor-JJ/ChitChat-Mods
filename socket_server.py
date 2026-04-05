import logging
import socket
import threading

logging.basicConfig(filename="chitchat_server.log", level=logging.INFO, format="%(asctime)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

class ServerThread(threading.Thread):
    def __init__(self, server, client_socket):
        super().__init__(daemon=True)
        self.server = server
        self.client_socket = client_socket
        self.name_label = None
        self.reader = client_socket.makefile(mode="r", buffering=1, encoding="utf-8")
        self.writer = client_socket.makefile(mode="w", buffering=1, encoding="utf-8")

    def send(self, message):
        self.writer.write(message + "\n")
        self.writer.flush()

    def run(self):
        try:
            self.name_label = self.reader.readline().strip()
            self.server.broadcast(f"**[{self.name_label}] Entered**")
            logging.info("CONNECT | %s", self.name_label)
            self.server.broadcast(f"**[{self.name_label}] Entered**")
            
            for data in self.reader:
                data = data.strip()
                if data == "/users":
                    with self.server.lock:
                        names = [c.name_label for c in self.server.clients]
                    self.send("**Users: " + ", ".join(names) + "**")
                else:
                    logging.info("MESSAGE | %s: %s", self.name_label, data)
                    self.server.broadcast(f"[{self.name_label}] {data}")
        except Exception as e:
            print(f"Error handling client communication: {e} ---->")
        finally:
            self.server.remove_thread(self)
            self.server.broadcast(f"**[{self.name_label}] Left**")
            logging.info("DISCONNECT | %s", self.name_label)
            try:
                print(f"{self.client_socket.getpeername()} - [{self.name_label}] Exit")
            except OSError:
                print(f"[{self.name_label}] Exit")
            try:
                self.reader.close()
                self.writer.close()
                self.client_socket.close()
            except Exception:
                pass


class SocketServer:
    def __init__(self, host="127.0.0.1", port=1234):
        self.host = host
        self.port = port
        self.clients = []
        self.lock = threading.Lock()

    def add_thread(self, thread):
        with self.lock:
            self.clients.append(thread)

    def remove_thread(self, thread):
        with self.lock:
            self.clients.remove(thread)

    def broadcast(self, message):
        print(message)
        logging.info("BROADCAST | %s", message)
        with self.lock:
            for client in self.clients:
                try:
                    client.send(message)
                except Exception:
                    pass

    def serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.host, self.port))
            server_socket.listen(50)
            print(f"\n Waiting for Client connection on {self.host}:{self.port}")

            while True:
                client_socket, addr = server_socket.accept()
                print(f"{addr} connect")
                logging.info("NEW CONNECTION | %s", addr)

                thread = ServerThread(self, client_socket)
                self.add_thread(thread)
                thread.start()


if __name__ == "__main__":
    SocketServer().serve()
