import socket
from .Game import settings
import json

class AppClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.client_socket = None

    def connect_server(self,player_name):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            init_message = json.dumps({
                "type": "player_join",
                "name": player_name
            })
            self.send_message(init_message)
            print(f"Conectado ao servidor em {self.host}:{self.port}")
        except Exception as e:
            print(f"Erro ao conectar ao servidor: {e}")

    def send_message(self, message):
        """
        Sends a message to the server.
        """
        try:
            self.socket.sendall((message + "\n").encode())
        except Exception as e:
            print(f"Error sending message to server: {e}")

    def receive_messages(self):
        """
        Receives messages from the server.
        """
        try:
            data = self.socket.recv(1024).decode()
            return json.loads(data)
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            return None
        except Exception as e:
            print(f"Error receiving message from server: {e}")
            return None
