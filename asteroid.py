import random

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS, LINE_WIDTH
import pygame

from logger import log_event


class Asteroid(CircleShape):

    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        self.kill()

        if self.radius <= ASTEROID_MIN_RADIUS:
            return

        log_event("asteroid_split")

        angle = random.uniform(20, 50)

        v1 = self.velocity.rotate(angle)
        v2 = self.velocity.rotate(-angle)

        new_radius = self.radius - ASTEROID_MIN_RADIUS

        asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid1.velocity = v1 * 1.2

        asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
        asteroid2.velocity = v2 * 1.2
