import pygame
import random
from .Settings import Settings

class SugarCube(pygame.sprite.Sprite):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings  # Armazena as configurações recebidas
        self.image = pygame.image.load('Project/images/sugar.png').convert_alpha()
        sugar_width = int(self.settings.WIDTH * 0.02875)
        sugar_height = int(self.settings.HEIGHT * 0.0317)
        self.image = pygame.transform.scale(self.image, (sugar_width, sugar_height))
        self.rect = self.image.get_rect(x=random.randint(0, self.settings.WIDTH - sugar_width), y=random.randint(-600, -30))
        self.speed = self.settings.HEIGHT * 0.0083  # Velocidade de queda proporcional à altura da tela

    def update(self):
        self.rect.y += self.speed
        if self.rect.y > self.settings.HEIGHT:
            self.reset_position()

    def reset_position(self):
        sugar_width = self.rect.width
        self.rect.x = random.randint(0, self.settings.WIDTH - sugar_width)
        self.rect.y = random.randint(-600, -30)
        
    def draw(self, screen):
        screen.blit(self.image, self.rect)