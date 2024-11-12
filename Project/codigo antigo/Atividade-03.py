import pygame
import random

# Classe principal do jogo
import pygame
import random

# Inicializar Pygame e obter a resolução da tela
#pygame.init()
#info = pygame.display.Info()
#SCREEN_WIDTH = info.current_w
#SCREEN_HEIGHT = info.current_h

SCREEN_WIDTH = 1280 
SCREEN_HEIGHT = 920

# Classe principal do jogo
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Café com Açúcar')
        self.clock = pygame.time.Clock()
        self.cup = Cup()
        
        self.sugar_cubes = [SugarCube() for _ in range(5)]
        
        # Carregar a imagem de fundo
        self.background_image = pygame.transform.scale(pygame.image.load('../images/background.jpeg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Carregar música de fundo e definir volume
        pygame.mixer.music.load('../sound/v.1 (2_13).mp3')
        pygame.mixer.music.set_volume(0.8)  # Volume original (1.0 = 100%)
        pygame.mixer.music.play(-1)

        # Carregar o efeito sonoro de colisão
        self.collision_sound = pygame.mixer.Sound('../sound/gota-agua.mp3')
        self.collision_time = None
        self.music_volume_reduced = False  # Flag para indicar volume reduzido

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False  # Permite sair do modo de tela cheia com a tecla ESC

            # Atualizar a posição da xícara e dos cubos de açúcar
            self.cup.move()
            for sugar_cube in self.sugar_cubes:
                sugar_cube.update()

            # Verificar colisões
            self.update()
            self.check_collisions()

            # Desenhar todos os elementos na tela
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

    def update(self):
        # Parar o som de colisão e restaurar o volume da música após 0.8 segundos
        if self.collision_time:
            elapsed_time = pygame.time.get_ticks() - self.collision_time
            if elapsed_time >= 800:  # 800 milissegundos
                self.collision_sound.stop()
                pygame.mixer.music.set_volume(1.0)  # Restaurar volume original
                self.collision_time = None
                self.music_volume_reduced = False

    def check_collisions(self):
        # Verificar colisão entre a xícara e os cubos de açúcar
        for sugar_cube in self.sugar_cubes:
            if self.cup.rect.colliderect(sugar_cube.rect):
                sugar_cube.reset_position()
                self.collision_sound.play()
                
                # Reduzir o volume da música
                pygame.mixer.music.set_volume(0.3)  # Volume reduzido
                self.collision_time = pygame.time.get_ticks()  # Armazenar o tempo da colisão
                self.music_volume_reduced = True

    def draw(self):
        # Desenhar o plano de fundo, a xícara e os cubos de açúcar
        self.screen.blit(self.background_image, (0, 0))
        self.cup.draw(self.screen)
        for sugar_cube in self.sugar_cubes:
            sugar_cube.draw(self.screen)

# Classe para a xícara
class Cup:
    def __init__(self):
        # Calcula o tamanho da xícara baseado na resolução da tela
        cup_width = int(SCREEN_WIDTH * 0.0525)  # Proporção para 42px em uma largura de 800px
        cup_height = int(SCREEN_HEIGHT * 0.0483)  # Proporção para 29px em uma altura de 600px

        self.image = pygame.image.load('../images/coffee-skin.png')
        self.image = pygame.transform.scale(self.image, (cup_width, cup_height))
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - cup_height - 10))
        
        self.speed = SCREEN_WIDTH * 0.0125  # Velocidade horizontal proporcional à largura da tela
        self.jump_speed = -SCREEN_HEIGHT * 0.025  # Velocidade inicial do pulo proporcional à altura da tela
        self.velocity_y = 0  # Velocidade vertical
        self.gravity = SCREEN_HEIGHT * 0.0017  # Gravidade proporcional à altura da tela

        self.is_jumping = False  # Controla o estado de pulo

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # Tela infinita horizontal
        if self.rect.right < 0:  # Saiu pela esquerda
            self.rect.left = SCREEN_WIDTH
        elif self.rect.left > SCREEN_WIDTH:  # Saiu pela direita
            self.rect.right = 0

        # Movimento de pulo
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.velocity_y = self.jump_speed  # Inicia o pulo
            self.is_jumping = True

        # Aplica gravidade
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Verifica se a xícara atingiu o chão
        if self.rect.bottom >= SCREEN_HEIGHT - 10:  # Limite inferior da tela
            self.rect.bottom = SCREEN_HEIGHT - 10  # Mantém a xícara no chão
            self.velocity_y = 0  # Para o movimento vertical
            self.is_jumping = False  # Permite outro pulo

    def draw(self, surface):
        surface.blit(self.image, self.rect)  # Desenhar a xícara com a imagem


class SugarCube:
    def __init__(self):
        # Calcula o tamanho do cubo de açúcar baseado na resolução da tela
        sugar_width = int(SCREEN_WIDTH * 0.02875)  # Proporção para 23px em uma largura de 800px
        sugar_height = int(SCREEN_HEIGHT * 0.0317)  # Proporção para 19px em uma altura de 600px

        self.image = pygame.image.load('../images/sugar.png')
        self.image = pygame.transform.scale(self.image, (sugar_width, sugar_height))
        self.rect = self.image.get_rect(x=random.randint(0, SCREEN_WIDTH - sugar_width), y=random.randint(-600, -30))
        self.speed = SCREEN_HEIGHT * 0.0083  # Velocidade de queda proporcional à altura da tela

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.reset_position()

    def reset_position(self):
        sugar_width = self.rect.width
        self.rect.x = random.randint(0, SCREEN_WIDTH - sugar_width)
        self.rect.y = random.randint(-600, -30)

    def draw(self, surface):
        surface.blit(self.image, self.rect)  # Desenhar o cubo de açúcar com a imagem

# Inicializar e executar o jogo
if __name__ == "__main__":
    game = Game()
    game.run()
