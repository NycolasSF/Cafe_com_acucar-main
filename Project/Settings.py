import pygame
import os

# Cores
PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)

class Settings:
    def __init__(self):
        pygame.init()
        self.WIDTH = 1280
        self.HEIGHT = 920
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_size = 48
        self.font = pygame.font.Font(None, self.font_size)
        self.title_font = None
        self.menu_font = None
        
        # MENU
        self.setup_fonts()
        self.highlight_color = (255, 69, 0) 
        self.menu_text_color = (255, 255, 255) 
        self.load_menu_background()

        self.load_fonts()# GERAL
        self.load_map_background()

        pygame.mixer.init()  # Inicializa o mixer para áudio
        self.load_sounds()

        #MULTIPLAYER
        self.server = None
        self.client = None
        self.client_connected = False
        self.multiplayer = False 
        self.client_socket = None
        self.server_socket = None
        self.size = 1024


    def setup_fonts(self):
        try:
            
            self.title_font = pygame.font.Font("Project/fonte/PixelifySans-Bold.ttf", 72)
            self.menu_font = pygame.font.Font("Project/fonte/PixelifySans-Regular.ttf", 48)
        except FileNotFoundError:
            print("Fonte personalizada não encontrada. Usando fontes padrão.")
            self.title_font = pygame.font.Font(None, 72)
            self.menu_font = pygame.font.Font(None, 48)

        

    def load_menu_background(self):
        try:
            self.menu_background = pygame.image.load("Project/images/coffee-pixels.png").convert_alpha()
            self.menu_background = pygame.transform.scale(self.menu_background, (self.WIDTH, self.HEIGHT))
        except pygame.error:
            print("Erro ao carregar a imagem de fundo do menu. Verifique o caminho do arquivo.")
            self.menu_background = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.menu_background.fill((50, 100, 200))  # Cor alternativa

    def load_map_background(self):
        try:
            self.map_background  = pygame.image.load('Project/images/background.jpeg').convert_alpha()
            self.map_background  = pygame.transform.scale(self.map_background , (self.WIDTH, self.HEIGHT))
        except pygame.error:
            print("Erro ao carregar a imagem de fundo do mapa. Verifique o caminho do arquivo.")
            self.map_background  = pygame.Surface((self.WIDTH, self.HEIGHT))
            self.map_background.fill((0, 0, 0))  # Cor alternativa para o mapa
    
    def load_fonts(self):
        try:
            # Caminho da fonte personalizada; altere o caminho conforme necessário
            self.font = pygame.font.Font("Project/fonte/PixelifySans-Regular.ttf", 14)
            self.headers_font = pygame.font.Font("Project/fonte/PixelifySans-Bold.ttf", 16)
            
        except FileNotFoundError:
            print("Fonte personalizada não encontrada. Usando a fonte padrão.")
            # Usa a fonte padrão do sistema caso a fonte personalizada não seja encontrada
            self.font = pygame.font.Font(None, 36)
            self.headers_font = pygame.font.Font(None, 28)

    def load_sounds(self):
        try:
            # Carrega a trilha sonora e o som de colisão
            self.music = pygame.mixer.Sound("Project/sound/trilha.mp3")
            self.music.set_volume(0.6)  
            self.collision_sound = pygame.mixer.Sound("Project/sound/agua-cafe.wav")
            self.collision_sound.set_volume(0.8)
            self.menu_sound = pygame.mixer.Sound("Project/sound/menu.wav")
            self.menu_sound.set_volume(0.8)
        except pygame.error as e:
            print("Erro ao carregar som: {e}")
            self.background_music = None
            self.collision_sound = None

    def play_background_music(self):
        if self.music:
            self.music.play(-1) 

    def stop_background_music(self):
        if self.music:
            self.music.stop() 
            
    def get_screen(self):
        return self.screen

settings = Settings()