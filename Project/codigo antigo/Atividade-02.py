#Aluno: Diogo Zenatti Gomes
#Aluno: Nicolas Froes

#Atividade 02



import pygame
import random

# Definir as dimensões da tela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Definir cores
WHITE = (255, 255, 255)  # Cor branca para o cubo de açúcar
BROWN = (139, 69, 19)  # Cor para a xícara
BLACK = (0, 0, 0)  # Cor para o contorno

# Classe principal do jogo
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Café com Açúcar')
        self.clock = pygame.time.Clock()
        self.cup = Cup()
        self.sugar_cubes = [SugarCube() for _ in range(5)]
        self.background_image = pygame.transform.scale(pygame.image.load('background.jpeg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.mixer.music.load('v.1 (2_13).mp3')
        pygame.mixer.music.play(-1)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.cup.move()
            self.update_sugar_cubes()
            self.check_collisions()
            self.draw()
            pygame.display.flip()
            self.clock.tick(30)

    def update_sugar_cubes(self):
        for sugar_cube in self.sugar_cubes:
            sugar_cube.update()

    def check_collisions(self):
        for sugar_cube in self.sugar_cubes:
            if self.cup.rect.colliderect(sugar_cube.rect):
                sugar_cube.reset_position()

    def draw(self):
        self.screen.blit(self.background_image, (0, 0))  # Desenhar plano de fundo
        self.cup.draw(self.screen)
        for sugar_cube in self.sugar_cubes:
            sugar_cube.draw(self.screen)

# Classe para a xícara
class Cup:
    def __init__(self):
        self.rect = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 60, 100, 50)
        self.speed = 10
        self.outline_width = 3

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, BROWN, self.rect)  # Desenhar a xícara
        pygame.draw.rect(surface, BLACK, self.rect, self.outline_width)  # Desenhar o contorno da xícara

# Classe para os cubos de açúcar
class SugarCube:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, SCREEN_WIDTH - 30), random.randint(-600, -30), 30, 30)
        self.speed = 5
        self.outline_width = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > SCREEN_HEIGHT:
            self.reset_position()

    def reset_position(self):
        self.rect.x = random.randint(0, SCREEN_WIDTH - 30)
        self.rect.y = random.randint(-600, -30)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)  # Desenhar o cubo de açúcar
        pygame.draw.rect(surface, BLACK, self.rect, self.outline_width)  # Desenhar o contorno do cubo de açúcar

# Inicializar e executar o jogo
if __name__ == "__main__":
    game = Game()
    game.run()
