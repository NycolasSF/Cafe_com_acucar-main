import pygame
import random
from .Settings import Settings

class Player(pygame.sprite.Sprite):
    def __init__(self, settings,is_player_2=False):
        super().__init__()
        self.settings = settings  # Armazena as configurações recebidas
        
        if is_player_2:
            self.image = pygame.image.load('Project/images/coffee-skin-2.png').convert_alpha()
        else:
            self.image = pygame.image.load('Project/images/coffee-skin.png').convert_alpha()

        cup_width = int(self.settings.WIDTH * 0.0525)
        cup_height = int(self.settings.HEIGHT * 0.0483)
        self.image = pygame.transform.scale(self.image, (cup_width, cup_height))
        self.rect = self.image.get_rect(center=(self.settings.WIDTH // 2, self.settings.HEIGHT - cup_height - 10))
        
        self.speed = self.settings.WIDTH * 0.0125
        self.jump_speed = -self.settings.HEIGHT * 0.025
        self.velocity_y = 0
        self.gravity = self.settings.HEIGHT * 0.0017
        self.is_jumping = False

    def move(self,keys=None):
        if keys is None:
            pass
        #keys = pygame.key.get_pressed()
        
        # Movimento lateral
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        
        # Movimento horizontal infinito (loop)
        if self.rect.right < 0:
            self.rect.left = self.settings.WIDTH
        elif self.rect.left > self.settings.WIDTH:
            self.rect.right = 0

        # Controle de pulo
        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.velocity_y = self.jump_speed
            self.is_jumping = True

        # Aplicação da gravidade e controle de altura
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Impedir que o player passe do chão
        if self.rect.bottom >= self.settings.HEIGHT - 10:
            self.rect.bottom = self.settings.HEIGHT - 10
            self.velocity_y = 0
            self.is_jumping = False

    def draw(self, screen):
        # Desenhar a xícara na tela
        screen.blit(self.image, self.rect)
