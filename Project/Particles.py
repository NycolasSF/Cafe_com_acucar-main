import pygame
import random

class WaterParticle(pygame.sprite.Sprite):
    def __init__(self, groups, pos, color, direction, speed):
        super().__init__(groups)
        self.pos = pygame.math.Vector2(pos)
        self.color = color
        self.direction = pygame.math.Vector2(direction)
        self.speed = speed
        self.alpha = 255
        self.fade_speed = 100
        self.size = random.randint(2, 5)  # Tamanhos variados para efeito natural

        self.create_surface()

    def create_surface(self):
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.size // 2, self.size // 2), self.size // 2)
        self.rect = self.image.get_rect(center=self.pos)

    def update(self, dt):
        # Movimento das partículas
        self.pos += self.direction * self.speed * dt
        self.rect.center = self.pos

        # Reduz a opacidade
        self.alpha -= self.fade_speed * dt
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)


class WaterEffect:
    def __init__(self, screen, particle_group):
        self.screen = screen
        self.particle_group = particle_group

    def spawn_water_particles(self, pos):
        for _ in range(10):  # Número de partículas geradas
            direction = pygame.math.Vector2(random.uniform(-0.5, 0.5), random.uniform(-1.5, -0.5))
            speed = random.uniform(30, 100)
            color = (139, 69, 19)  # Marrom para simular café
            WaterParticle(self.particle_group, pos, color, direction, speed)

    def update(self, dt):
        self.particle_group.update(dt)

    def draw(self):
        self.particle_group.draw(self.screen)
 

class LoadingEffect:
    def __init__(self, screen, particle_color=(41, 132, 189), max_particles=150):
        self.screen = screen
        self.particle_color = particle_color
        self.max_particles = max_particles
        self.particles = []

    def spawn_particle(self):
        x = random.randint(0, self.screen.get_width())
        y = random.randint(0, self.screen.get_height())
        radius = random.randint(2, 5)
        speed_x = random.uniform(-1, 1)
        speed_y = random.uniform(-1, 1)
        self.particles.append([x, y, radius, speed_x, speed_y])

        # Remove partículas antigas para manter o limite
        if len(self.particles) > self.max_particles:
            self.particles.pop(0)

    def update_particles(self):
        for particle in self.particles:
            particle[0] += particle[3]  # Movimento em X
            particle[1] += particle[4]  # Movimento em Y

    def draw_particles(self):
        for particle in self.particles:
            pygame.draw.circle(self.screen, self.particle_color, (int(particle[0]), int(particle[1])), particle[2])

    def run(self):
        self.spawn_particle()
        self.update_particles()
        self.draw_particles()