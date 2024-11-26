import pygame
from .Settings import *
from .Player import Player
from .Objects import SugarCube
from .SQL import load_player_score, load_last_player, save_player_data, save_player_score
from .Particles import WaterEffect, LoadingEffect
from .Server import AppServer
from .Client import AppClient
import threading
import json

class Game:
    def __init__(self):
        self.screen = settings.get_screen()
        self.clock = settings.clock
        self.collision_time = None
        self.music_volume_reduced = False

        self.cup = Player(settings)
        self.player_2 = Player(settings, is_player_2=True)
        self.players = [{"name": "", "points": 0, "position": (0, 0)}]

        self.sugar_cubes = [SugarCube(settings) for _ in range(5)]

        # Cria o grupo de partículas
        self.particle_group = pygame.sprite.Group()  
        self.water_effect = WaterEffect(self.screen, self.particle_group)

        # Opções do menu
        self.menu_options = ["Continar", "Novo Game", "Multiplayer", "Sair"]
        self.selected_option = 0
        # Opções do submenu Multiplayer
        self.multiplayer_options = ["Criar Sala", "Entrar Sala", "Voltar"]
        self.selected_multiplayer_option = 0

        # Partículas de fundo
        self.loading_effect = LoadingEffect(self.screen)

    
    def display_menu(self):
        while True:
            # Renderiza o menu
            self.screen.blit(settings.menu_background, (0, 0))
            settings.stop_background_music()

            # Renderiza as opções
            for i, option in enumerate(self.menu_options):
                color = settings.highlight_color if i == self.selected_option else settings.menu_text_color
                option_text = settings.menu_font.render(option, True, color)
                option_rect = option_text.get_rect(center=(settings.WIDTH // 2, 300 + i * 70))
                self.screen.blit(option_text, option_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    settings.menu_sound.play(0,100,100)
                    if event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        return self.selected_option + 1

    def run(self):
        while True:
            menu_option = self.display_menu()
            if menu_option == 1:  # Continue
                self.player_name, self.player_points = load_last_player()
                settings.multiplayer = False
                if not self.player_name:
                    self.start_game()
                else:
                    self.players = [{"name": self.player_name, "points": self.player_points, "position":(self.cup.rect.x, self.cup.rect.y)}]
                    self.main_loop()
            elif menu_option == 2:  # New Game
                settings.multiplayer = False
                self.start_game()
            elif menu_option == 3:  # Multiplayer
                settings.multiplayer = True
                self.multiplayer()
            elif menu_option == 4:  # Exit
                self.exit_game()

    def display_multiplayer_menu(self):
        while True:
            # Renderiza o submenu
            self.screen.blit(settings.menu_background, (0, 0))
            # Renderiza o título do submenu
            title_text = settings.title_font.render("Multiplayer", True, (0, 255, 0))
            title_rect = title_text.get_rect(center=(settings.WIDTH // 2, 230))
            self.screen.blit(title_text, title_rect)
            # Renderiza as opções do submenu
            for i, option in enumerate(self.multiplayer_options):
                color = settings.highlight_color if i == self.selected_multiplayer_option else settings.menu_text_color
                option_text = settings.menu_font.render(option, True, color)
                option_rect = option_text.get_rect(center=(settings.WIDTH // 2, 300 + i * 70))
                self.screen.blit(option_text, option_rect)

            pygame.display.flip()

            # Lida com entradas do usuário
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    settings.menu_sound.play(0,100,100)
                    if event.key == pygame.K_DOWN:
                        self.selected_multiplayer_option = (self.selected_multiplayer_option + 1) % len(self.multiplayer_options)
                    elif event.key == pygame.K_UP:
                        self.selected_multiplayer_option = (self.selected_multiplayer_option - 1) % len(self.multiplayer_options)
                    elif event.key == pygame.K_RETURN:
                        return self.selected_multiplayer_option + 1
     #MULTPLAYER       
    def multiplayer(self):
        while True:
            submenu_option = self.display_multiplayer_menu()
            if submenu_option == 1:  # Criar Sala (virar servidor)
                # server   
                settings.server = True
                threading.Thread(target=self.server_thread).start()
                self.start_game()
            elif submenu_option == 2:  # Entrar Sala (virar cliente)
                settings.client = True

                self.player_name = self.get_player_name()
                self.player_points = 0
                save_player_data(self.player_name, self.player_points)
                self.players = [{"name": self.player_name, "points": self.player_points, "position":(self.cup.rect.x, self.cup.rect.y)}]

                threading.Thread(target=self.client_thread).start()
                self.start_game()
            elif submenu_option == 3:  # Voltar
                return  # Volta ao menu principal

    # Server
    def server_thread(self):
        settings.server_socket = AppServer("localhost", 5001)
        threading.Thread(target=settings.server_socket.server_listen).start()
    # Client
    def client_thread(self):
        settings.client_socket = AppClient("localhost", 5001)
        settings.client_socket.connect_server(self.player_name)

    def update_game_state(self, state):
        """
        Updates the local game state with data received from the server.
        """
        if "players" in state:
            for player_data in state["players"]:
                if player_data["name"] != self.player_name:
                    self.player_2.name = player_data["name"]
                    self.player_2.points = player_data["points"]
                    self.player_2.rect.x, self.player_2.rect.y = player_data["position"]

        if "sugar_cubes" in state:
            for i, position in enumerate(state["sugar_cubes"]):
                self.sugar_cubes[i].rect.x, self.sugar_cubes[i].rect.y = position

    def handle_multiplayer_communication(self):
        """
        Handles sending and receiving game state data.
        """
        try:
            # Send local game state to the server
            self.send_game_state()

            # Receive updated game state from the server
            if settings.client:
                data = settings.client_socket.receive_messages()
                if data:
                    self.update_game_state(json.loads(data))
            elif settings.server:
                data = settings.server_socket.receive_messages()
                if data:
                    self.update_game_state(json.loads(data))
        except Exception as e:
            print(f"Error in multiplayer communication: {e}")


    def start_game(self):
        # Solicita o nome do jogador
        if settings.multiplayer:
            if settings.server:    
                self.player_name = self.get_player_name()
                self.player_points = 0
                save_player_data(self.player_name, self.player_points)
                self.players = [{"name": self.player_name, "points": self.player_points, "position":(self.cup.rect.x, self.cup.rect.y)}]
        else:
            self.player_name = self.get_player_name()
            self.player_points = 0
            save_player_data(self.player_name, self.player_points)
            self.players = [{"name": self.player_name, "points": self.player_points, "position":(self.cup.rect.x, self.cup.rect.y)}]

        settings.play_background_music() 
        self.main_loop() 
    
    def get_player_name(self):
        input_active = True
        self.player_name = ""
        cursor_visible = True
        cursor_timer = pygame.time.get_ticks()
        
        while input_active:
            self.screen.fill((0, 0, 0))
            
            # Texto de prompt
            prompt = settings.menu_font.render("Digite seu nome:", True, (255, 255, 255))
            prompt_rect = prompt.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 - 50))
            self.screen.blit(prompt, prompt_rect)
            
            # Texto digitado pelo usuário em verde
            name_text = settings.menu_font.render(self.player_name, True, (0, 255, 0))
            name_rect = name_text.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2))
            self.screen.blit(name_text, name_rect)
            
            # Cursor piscante
            if cursor_visible:
                cursor = settings.menu_font.render("|", True, (0, 255, 0))
                cursor_rect = cursor.get_rect(midleft=(name_rect.right + 5, name_rect.centery))
                self.screen.blit(cursor, cursor_rect)
            
            # Alterna a visibilidade do cursor a cada 500 ms
            if pygame.time.get_ticks() - cursor_timer > 500:
                cursor_visible = not cursor_visible
                cursor_timer = pygame.time.get_ticks()

            pygame.display.flip()

            # Lida com eventos de entrada de texto
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    input_active = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_name = self.player_name[:-1]
                    else:
                        self.player_name += event.unicode  # Adiciona o caractere digitado

        return self.player_name

    def send_game_state(self):
        """
        Envia o estado local do jogador para o servidor.
        """
        try:
            local_state = {
                "type": "player_update",
                "name": self.player_name,
                "points": self.player_points,
                "position": (self.cup.rect.x, self.cup.rect.y),
            }
            message = json.dumps(local_state)
            self.client_socket.sendall((message + "\n").encode())
        except Exception as e:
            print(f"Erro ao enviar estado do jogo: {e}")


    def main_loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return

            self.update()
            self.draw()

            if settings.multiplayer:
                self.handle_multiplayer_communication()
                
            self.draw_scoreboard()
            self.water_effect.update(self.clock.get_time() / 1000)
            self.water_effect.draw()
            
            pygame.display.flip()
            self.clock.tick(30)

    def update_local_player(self):
        for player in self.players:
            if player["name"] == self.player_name:  # Identifica pelo nome do jogador
                player["points"] = self.player_points  # Atualiza os pontos
                player["position"] = (self.cup.rect.x, self.cup.rect.y)  # Atualiza a posição
                pass

    def update(self):
        self.cup.move(keys=pygame.key.get_pressed())
        self.update_local_player()
        for sugar_cube in self.sugar_cubes:
            sugar_cube.update()

        self.check_collisions()

        if self.collision_time:
            elapsed_time = pygame.time.get_ticks() - self.collision_time
            if elapsed_time >= 800:
                settings.collision_sound.stop()
                pygame.mixer.music.set_volume(0.6)
                self.collision_time = None
                self.music_volume_reduced = False

    def check_collisions(self):
        for sugar_cube in self.sugar_cubes:
            if self.cup.rect.colliderect(sugar_cube.rect):
                sugar_cube.reset_position()

                # Incrementa os pontos do jogador
                self.player_points += 1
                save_player_score(self.player_name, self.player_points)  # Salva a nova pontuação no banco de dados

                if settings.multiplayer:
                    self.send_collision_update(sugar_cube)

                # Toca o som e reduz o volume
                settings.collision_sound.play()
                pygame.mixer.music.set_volume(0.3)
                self.collision_time = pygame.time.get_ticks()
                self.music_volume_reduced = True

                # Gera o efeito de gotas ao colidir
                self.water_effect.spawn_water_particles((self.cup.rect.centerx, self.cup.rect.top))
    
    def send_collision_update(self, sugar_cube):
        collision_data = {
            "type": "collision",
            "player_name": self.player_name,
            "points": self.player_points,
            "sugar_cube_position": (sugar_cube.rect.x, sugar_cube.rect.y),
        }
        message = json.dumps(collision_data)
        try:
            if settings.server:
                settings.server_socket.send_message(message)
            elif settings.client:
                settings.client_socket.send_message(message)
        except Exception as e:
            print(f"Erro ao enviar colisão: {e}")


    def draw_scoreboard(self):
        board_width, board_height = 300, 50 + len(self.players) * 30
        board_x = settings.WIDTH - board_width - 20
        board_y = 20

        pygame.draw.rect(self.screen, (200, 220, 220), (board_x, board_y, board_width, board_height), border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), (board_x, board_y, board_width, board_height), 2, border_radius=10)

        name_header = settings.headers_font.render("Player", True, (0, 0, 0))
        points_header = settings.headers_font.render("Points", True, (0, 0, 0))
        self.screen.blit(name_header, (board_x + 10, board_y + 5))
        self.screen.blit(points_header, (board_x + 200, board_y + 5))

        pygame.draw.line(self.screen, (0, 0, 0), (board_x, board_y + 30), (board_x + board_width, board_y + 30), 2)

        for i, player in enumerate(self.players):  # Ajuste aqui para trabalhar com tuplas
            row_y = board_y + 35 + i * 30
            name_text = settings.font.render(player["name"], True, (0, 0, 0))
            points_text = settings.font.render(str(player["points"]), True, (0, 0, 0))

            self.screen.blit(name_text, (board_x + 10, row_y))
            self.screen.blit(points_text, (board_x + 200, row_y))

    def draw(self):
        self.screen.blit(settings.map_background, (0, 0))
       
        self.cup.draw(self.screen)

        if settings.client_connected:
            self.player_2.draw(self.screen)
            
        for sugar_cube in self.sugar_cubes:
            sugar_cube.draw(self.screen)

    def exit_game(self):
        pygame.quit()
        exit()


class MenuStarted:
    def draw_menu(self):
        """Desenha o menu na tela."""
        self.screen.blit(self.background, (0, 0))

        # Renderiza o título do jogo
        title_text = self.title_font.render("Café com Açúcar", True, (41, 132, 189))
        title_rect = title_text.get_rect(center=(settings.WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)

        # Renderiza as opções do menu
        for i, option in enumerate(self.options):
            color = settings.highlight_color if i == self.selected_option else settings.menu_text_color
            option_text = self.font.render(option, True, color)
            option_rect = option_text.get_rect(center=(settings.WIDTH // 2, 300 + i * 70))
            self.screen.blit(option_text, option_rect)

        pygame.display.flip()

    def handle_input(self):
        """Gerencia a entrada do usuário para navegar no menu."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    return self.selected_option + 1
        return None

    def run(self):
        """Executa o loop do menu."""
        while True:
            self.draw_menu()
            selected = self.handle_input()
            if selected:
                return selected
            
if __name__ == "__main__":
    game = Game()
    game.run()
