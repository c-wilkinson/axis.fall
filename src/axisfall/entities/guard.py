from __future__ import annotations

import pygame

from axisfall.entities.player import Player
from axisfall.settings import Settings


class Guard:
    def __init__(self, position: tuple[int, int], settings: Settings) -> None:
        self.settings = settings
        self.rect = pygame.Rect(0, 0, 44, 62)
        self.rect.midbottom = position
        self.max_health = 4
        self.health = self.max_health
        self.hit_flash_timer = 0.0
        self.contact_cooldown = 0.0

    @property
    def alive(self) -> bool:
        return self.health > 0

    def reset(self) -> None:
        self.health = self.max_health
        self.hit_flash_timer = 0.0
        self.contact_cooldown = 0.0

    def update(self, player: Player, dt: float) -> str | None:
        self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)
        self.contact_cooldown = max(0.0, self.contact_cooldown - dt)

        if (
            not self.alive
            or not player.alive
            or not self.rect.colliderect(player.rect)
        ):
            return None
        if self.contact_cooldown > 0.0:
            return None

        impact_speed = player.speed
        if player.attack_held and impact_speed >= self.settings.impact_speed:
            damage = 2 if impact_speed >= self.settings.heavy_impact_speed else 1
            self.health = max(0, self.health - damage)
            self.hit_flash_timer = 0.16
            self.contact_cooldown = 0.25

            if player.velocity.length_squared() > 0:
                player.velocity = -player.velocity.normalize() * min(260.0, impact_speed * 0.35)
            else:
                player.velocity = pygame.Vector2(0, -220)
            return "heavy_hit" if damage == 2 else "hit"

        separation = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if separation.length_squared() == 0:
            separation = -player.gravity
        knockback = separation.normalize() * 380 - player.gravity * 120
        player.take_damage(knockback)
        self.contact_cooldown = 0.55
        return "player_hurt"

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            wreck = self.rect.copy()
            wreck.height = 14
            wreck.bottom = self.rect.bottom
            pygame.draw.rect(surface, (76, 78, 84), wreck, border_radius=4)
            return

        fill = (230, 105, 105) if self.hit_flash_timer <= 0 else (255, 235, 235)
        pygame.draw.rect(surface, fill, self.rect, border_radius=6)
        pygame.draw.rect(surface, (38, 34, 40), self.rect, width=4, border_radius=6)

        shield = pygame.Rect(0, 0, 12, 40)
        shield.midleft = (self.rect.left - 4, self.rect.centery)
        pygame.draw.rect(surface, (92, 98, 112), shield, border_radius=4)

        bar = pygame.Rect(self.rect.left, self.rect.top - 12, self.rect.width, 6)
        pygame.draw.rect(surface, (40, 42, 48), bar)
        if self.health:
            health_bar = bar.copy()
            health_bar.width = round(bar.width * (self.health / self.max_health))
            pygame.draw.rect(surface, (224, 224, 224), health_bar)
