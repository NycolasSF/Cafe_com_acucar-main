import pygame
from .Settings import Settings
from .Player import Player
from .Objects import SugarCube
from .SQL import load_player_data, load_player_score, load_last_player, save_player_data, save_player_score

class Game:
    def __init__(self):
        self.settings = Settings()
        self.screen = self.settings.get_screen()
        self.clock = self.settings.clock
        self.cup = Player(self.settings)
        self.sugar_cubes = [SugarCube(self.settings) for _ in range(5)]
        self.collision_time = None
        self.music_volume_reduced = False

        self.players = []  # List to store player names and scores
        self.player_name, self.player_points = load_last_player()
        #print("Aqui tem coisa", self.player_name)

    def display_menu(self):
        background = self.settings.menu_background
        font = self.settings.menu_font  
        title_font = self.settings.title_font  

        # Menu 
        menu_options = ["Continue", "New Game", "Exit"]
        selected_option = 0

        while True:
            self.screen.blit(background, (0, 0))
            title_font.render("Café com Açúcar", True, (41, 132, 189))
            
            for i, option in enumerate(menu_options):
                text_font = title_font if i == selected_option else font
                color = self.settings.highlight_color if i == selected_option else self.settings.menu_text_color
                option_text = text_font.render(option, True, color)

                text_rect = option_text.get_rect(center=(self.settings.WIDTH // 2, 300 + i * 70))
                self.screen.blit(option_text, text_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        selected_option = (selected_option + 1) % len(menu_options)
                    elif event.key == pygame.K_UP:
                        selected_option = (selected_option - 1) % len(menu_options)
                    elif event.key == pygame.K_RETURN:
                        return selected_option + 1

    def run(self):
        while True:
            menu_option = self.display_menu()
            if menu_option == 1:  # Continue
                if not self.player_name:  
                    self.start_game()
                else:
                    self.main_loop()
            elif menu_option == 2:  # Start Game
                self.start_game()
            elif menu_option == 3:  # Exit
                self.exit_game()

    def start_game(self):
        # Solicita o nome do jogador
        self.player_name = self.get_player_name()
        self.player_points = 0
        
        save_player_data(self.player_name, 0)

        # Inicia o loop principal do jogo com o nome do jogador atual
        self.players = [(self.player_name, 0)]  
        self.settings.play_background_music() 
        self.main_loop() 
    
    def get_player_name(self):
        input_active = True
        self.player_name = ""
        cursor_visible = True
        cursor_timer = pygame.time.get_ticks()
        
        while input_active:
            self.screen.fill((0, 0, 0))
            
            # Texto de prompt
            prompt = self.settings.menu_font.render("Digite seu nome:", True, (255, 255, 255))
            prompt_rect = prompt.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT // 2 - 50))
            self.screen.blit(prompt, prompt_rect)
            
            # Texto digitado pelo usuário em verde
            name_text = self.settings.menu_font.render(self.player_name, True, (0, 255, 0))
            name_rect = name_text.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT // 2))
            self.screen.blit(name_text, name_rect)
            
            # Cursor piscante
            if cursor_visible:
                cursor = self.settings.menu_font.render("|", True, (0, 255, 0))
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
            self.draw_scoreboard()

            pygame.display.flip()
            self.clock.tick(30)

    def update(self):
        self.cup.move()
        for sugar_cube in self.sugar_cubes:
            sugar_cube.update()

        self.check_collisions()

        if self.collision_time:
            elapsed_time = pygame.time.get_ticks() - self.collision_time
            if elapsed_time >= 800:
                self.settings.collision_sound.stop()
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

                # Toca o som e reduz o volume
                self.settings.collision_sound.play()
                pygame.mixer.music.set_volume(0.3)
                self.collision_time = pygame.time.get_ticks()
                self.music_volume_reduced = True

    def draw(self):
        self.screen.blit(self.settings.map_background, (0, 0))
        self.cup.draw(self.screen)
        for sugar_cube in self.sugar_cubes:
            sugar_cube.draw(self.screen)

    def draw_scoreboard(self): 
        # Carrega a pontuação atualizada do jogador antes de desenhar
        self.player_points = load_player_score(self.player_name)  

        # Exibe o quadro de pontuação atualizado
        board_width, board_height = 200, 70
        board_x = self.settings.WIDTH - board_width - 20
        board_y = 20

        pygame.draw.rect(self.screen, (200, 220, 220), (board_x, board_y, board_width, board_height), border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), (board_x, board_y, board_width, board_height), 2, border_radius=10)

        # Títulos
        name_header = self.settings.headers_font.render("Player", True, (0, 0, 0))
        points_header = self.settings.headers_font.render("Points", True, (0, 0, 0))

        self.screen.blit(name_header, (board_x + 10, board_y + 5))
        self.screen.blit(points_header, (board_x + 120, board_y + 5))

        pygame.draw.line(self.screen, (0, 0, 0), (board_x, board_y + 30), (board_x + board_width, board_y + 30), 2)

        # Exibe o nome do jogador e a pontuação atual
        player_name_text = self.settings.font.render(self.player_name, True, (0, 0, 0))
        player_score_text = self.settings.font.render(str(self.player_points), True, (0, 0, 0))

        self.screen.blit(player_name_text, (board_x + 10, board_y + 35))
        self.screen.blit(player_score_text, (board_x + 130, board_y + 35))

    def exit_game(self):
        pygame.quit()
        exit()

if __name__ == "__main__":
    game = Game()
    game.run()
