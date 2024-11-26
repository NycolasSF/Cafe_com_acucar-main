import socket
import threading
from .Settings import settings
import json

class AppServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = []  # Lista de clientes conectados (socket, endereço)
        self.players = []  # Lista de estados dos jogadores

    def server_listen(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Servidor iniciado em {self.host}:{self.port}")

            while True:
                client_socket, addr = self.server_socket.accept()
                print(f"Novo cliente conectado: {addr}")
                self.clients.append(client_socket)

                # Inicializa o estado do jogador
                player_state = {"name": f"Player_{len(self.clients)}", "points": 0, "position": (0, 0)}
                self.players.append(player_state)

                # Envia o estado inicial para o novo cliente
                initial_state = json.dumps({"players": self.players})
                self.send_message(client_socket, initial_state)

                # Inicia uma thread para gerenciar o cliente
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
        except Exception as e:
            print(f"Erro no servidor: {e}")

    def send_message(self, client_socket, message):
        try:
            client_socket.sendall((message + "\n").encode())  # Adiciona '\n' como delimitador
        except Exception as e:
            print(f"Erro ao enviar mensagem: {e}")

    def update_player_state(self, message):
        player_name = message["name"]
        for player in self.players:
            if player["name"] == player_name:
                player["points"] = message["points"]
                player["position"] = message["position"]
                return

        # Adiciona o jogador se ele ainda não existir
        self.add_new_player(player_name)

    def add_new_player(self, player_name):

        if not any(player["name"] == player_name for player in self.players):
            self.players.append({
                "name": player_name,
                "points": 0,
                "position": (0, 0),
            })
            print(f"Novo jogador adicionado: {player_name}")

    def remove_disconnected_player(self, player_name):
        self.players = [player for player in self.players if player["name"] != player_name]
        print(f"Jogador removido: {player_name}")

    def broadcast_state(self):
        """
        Broadcasts the current game state to all connected clients.
        """
        state = {
            "players": self.players,
            "sugar_cubes": [(0, 0) for _ in range(5)],  # Mocking cube positions for now
        }
        message = json.dumps(state)
        for client in self.clients:
            try:
                client.sendall((message + "\n").encode())
            except Exception as e:
                print(f"Error sending game state to client: {e}")

    def handle_client(self, client_socket):
        """
        Handles communication with a single client.
        """
        buffer = ""
        player_name = None
        try:
            while True:
                data = client_socket.recv(1024).decode()
                if not data:
                    break

                buffer += data
                if "\n" in buffer:
                    messages = buffer.split("\n")
                    buffer = messages.pop()

                    for message in messages:
                        try:
                            parsed_message = json.loads(message)
                            if parsed_message["type"] == "player_update":
                                player_name = parsed_message["name"]
                                self.update_player_state(parsed_message)
                                self.broadcast_state()
                        except json.JSONDecodeError as e:
                            print(f"JSON decoding error: {e}")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            print("Client disconnected")
            if player_name:
                self.remove_disconnected_player(player_name)
            if client_socket in self.clients:
                self.clients.remove(client_socket)
            client_socket.close()
