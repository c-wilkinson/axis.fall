from __future__ import annotations

import pygame

from axisfall.entities.player import Player
from axisfall.settings import Settings


class Guard:
    def __init__(self, position: tuple[int, int], settings: Settings, patrol_range: tuple[int, int] | None = None, patrol_speed: float = 80.0,  facing_direction: int = 1) -> None:
        self.settings = settings
        self.start_position = position
        self.rect = pygame.Rect(0, 0, 44, 62)
        self.rect.midbottom = position
        self.max_health = 4
        self.health = self.max_health
        self.hit_flash_timer = 0.0
        self.contact_cooldown = 0.0

        self.patrol_range = patrol_range
        self.patrol_speed = patrol_speed
        self.start_direction = 1 if facing_direction >= 0 else -1
        self.patrol_direction = self.start_direction
        self.patrol_x = float(self.rect.centerx)

    @property
    def alive(self) -> bool:
        return self.health > 0

    def reset(self) -> None:
        self.rect.midbottom = self.start_position
        self.health = self.max_health
        self.hit_flash_timer = 0.0
        self.contact_cooldown = 0.0
        self.patrol_direction = self.start_direction
        self.patrol_x = float(self.rect.centerx)

    def update(self, player: Player, dt: float) -> str | None:
        self.hit_flash_timer = max(0.0, self.hit_flash_timer - dt)
        self.contact_cooldown = max(0.0, self.contact_cooldown - dt)

        if self.alive:
            self._update_patrol(dt)

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
            heavy_hit = impact_speed >= self.settings.heavy_impact_speed
            damage = 2.0 if heavy_hit else 1.0

            player_is_in_front = (
                self.patrol_direction > 0
                and player.rect.centerx >= self.rect.centerx
            ) or (
                self.patrol_direction < 0
                and player.rect.centerx <= self.rect.centerx
            )

            if player_is_in_front:
                damage *= 0.5

            self.health = max(0.0, self.health - damage)
            self.hit_flash_timer = 0.16
            self.contact_cooldown = 0.25

            if player.velocity.length_squared() > 0:
                player.velocity = -player.velocity.normalize() * min(260.0, impact_speed * 0.35)
            else:
                player.velocity = pygame.Vector2(0, -220)
            return "heavy_hit" if heavy_hit else "hit"

        separation = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if separation.length_squared() == 0:
            separation = -player.gravity
        knockback = separation.normalize() * 380 - player.gravity * 120
        player.take_damage(knockback)
        self.contact_cooldown = 0.55
        return "player_hurt"

    def _update_patrol(self, dt: float) -> None:
        if self.patrol_range is None:
            return

        patrol_left, patrol_right = self.patrol_range
        self.patrol_x += self.patrol_direction * self.patrol_speed * dt

        if self.patrol_x <= patrol_left:
            self.patrol_x = float(patrol_left)
            self.patrol_direction = 1
        elif self.patrol_x >= patrol_right:
            self.patrol_x = float(patrol_right)
            self.patrol_direction = -1

        self.rect.centerx = round(self.patrol_x)

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

        if self.patrol_direction > 0:
            shield.midleft = (
                self.rect.right - 4,
                self.rect.centery,
            )
            visor_start = (
                self.rect.centerx,
                self.rect.top + 15,
            )
            visor_end = (
                self.rect.right + 3,
                self.rect.top + 15,
            )
        else:
            shield.midright = (
                self.rect.left + 4,
                self.rect.centery,
            )
            visor_start = (
                self.rect.centerx,
                self.rect.top + 15,
            )
            visor_end = (
                self.rect.left - 3,
                self.rect.top + 15,
            )

        pygame.draw.rect(
            surface,
            (92, 98, 112),
            shield,
            border_radius=4,
        )

        pygame.draw.line(
            surface,
            (38, 34, 40),
            visor_start,
            visor_end,
            width=4,
        )

        bar = pygame.Rect(self.rect.left, self.rect.top - 12, self.rect.width, 6)
        pygame.draw.rect(surface, (40, 42, 48), bar)
        if self.health:
            health_bar = bar.copy()
            health_bar.width = round(bar.width * (self.health / self.max_health))
            pygame.draw.rect(surface, (224, 224, 224), health_bar)
