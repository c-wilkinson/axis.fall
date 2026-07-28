from __future__ import annotations

from dataclasses import dataclass

import pygame

from axisfall.physics import (
    GravityDirection,
    approach,
    clamp_vector_component,
    tangent_for,
)
from axisfall.settings import Settings
from axisfall.sprites import PlayerSprites
from axisfall.world.collision import CollisionWorld


@dataclass(slots=True)
class PlayerInput:
    move: float = 0.0
    jump_pressed: bool = False
    gravity_direction: GravityDirection | None = None
    attack_held: bool = False


class Player:
    SIZE = 30
    WALK_FRAME_TIME = 0.1
    DEATH_FRAME_TIME = 0.18

    def __init__(self, spawn: tuple[float, float], settings: Settings) -> None:
        self.settings = settings
        self.spawn = pygame.Vector2(spawn)
        self.position = self.spawn.copy()
        self.velocity = pygame.Vector2()
        self.rect = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center = self.position
        self.gravity_direction = GravityDirection.DOWN
        self.grounded = False
        self.attack_held = False
        self.health = settings.player_max_health
        self.invulnerability_timer = 0.0
        self.gravity_flash_timer = 0.0
        self.animation_timer = 0.0
        self.death_animation_timer = 0.0
        self.facing = 1
        self._sprites: PlayerSprites | None = None

    @property
    def gravity(self) -> pygame.Vector2:
        return self.gravity_direction.vector

    @property
    def speed(self) -> float:
        return self.velocity.length()

    @property
    def alive(self) -> bool:
        return self.health > 0

    def reset(self) -> None:
        self.position = self.spawn.copy()
        self.velocity.update(0, 0)
        self.rect.center = self.position
        self.gravity_direction = GravityDirection.DOWN
        self.grounded = False
        self.attack_held = False
        self.health = self.settings.player_max_health
        self.invulnerability_timer = 0.0
        self.gravity_flash_timer = 0.0
        self.animation_timer = 0.0
        self.death_animation_timer = 0.0
        self.facing = 1

    def update(self, controls: PlayerInput, world: CollisionWorld, dt: float) -> None:
        self.animation_timer += dt

        if not self.alive:
            self.death_animation_timer += dt
            self.attack_held = False
            self.velocity.update(0, 0)
            return

        self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)
        self.gravity_flash_timer = max(0.0, self.gravity_flash_timer - dt)
        self.attack_held = controls.attack_held

        if abs(controls.move) > 0.01:
            self.facing = 1 if controls.move > 0 else -1

        if controls.gravity_direction is not None:
            self.set_gravity(controls.gravity_direction)

        gravity = self.gravity
        tangent = tangent_for(gravity)
        tangent_speed = self.velocity.dot(tangent)
        if abs(controls.move) > 0.01:
            target_speed = controls.move * self.settings.run_speed
            acceleration = (
                self.settings.ground_acceleration
                if self.grounded
                else self.settings.air_acceleration
            )
            tangent_speed = approach(tangent_speed, target_speed, acceleration * dt)
            normal_speed = self.velocity.dot(gravity)
            self.velocity = tangent * tangent_speed + gravity * normal_speed
        elif self.grounded:
            tangent_speed = approach(
                tangent_speed,
                0.0,
                self.settings.ground_deceleration * dt,
            )
            normal_speed = self.velocity.dot(gravity)
            self.velocity = tangent * tangent_speed + gravity * normal_speed

        if controls.jump_pressed and self.grounded:
            self.velocity += -gravity * self.settings.jump_speed
            self.grounded = False

        self.velocity += gravity * self.settings.gravity_acceleration * dt
        self.velocity = clamp_vector_component(
            self.velocity,
            gravity,
            -self.settings.terminal_speed,
            self.settings.terminal_speed,
        )
        self.position, self.velocity, collisions = world.move(
            self.rect,
            self.position,
            self.velocity,
            dt,
        )

        self.grounded = any(
            collision.normal.dot(-gravity) > 0.99 for collision in collisions
        ) or world.touching_in_direction(self.rect, gravity)

    def set_gravity(self, direction: GravityDirection) -> None:
        if not self.alive or direction is self.gravity_direction:
            return
        self.gravity_direction = direction
        self.grounded = False
        self.gravity_flash_timer = 0.12

    def take_damage(self, knockback: pygame.Vector2) -> None:
        if not self.alive or self.invulnerability_timer > 0.0:
            return

        self.health = max(0, self.health - 1)
        self.grounded = False
        if not self.alive:
            self.attack_held = False
            self.velocity.update(0, 0)
            self.invulnerability_timer = 0.0
            self.death_animation_timer = 0.0
            return

        self.invulnerability_timer = 0.8
        self.velocity = knockback

    def draw(self, surface: pygame.Surface) -> None:
        flashing = (
            self.invulnerability_timer > 0
            and int(self.invulnerability_timer * 12) % 2 == 0
        )
        if flashing:
            return

        if self._sprites is None:
            self._sprites = PlayerSprites()

        animation, frame_index = self._current_animation()
        image = self._sprites.frame(
            animation,
            frame_index,
            self.facing,
            self.gravity_direction,
        )

        if self.gravity_flash_timer > 0 and self.alive:
            image = image.copy()
            image.fill((40, 75, 100), special_flags=pygame.BLEND_RGB_ADD)

        if self.attack_held and self.alive:
            pygame.draw.circle(
                surface,
                (255, 214, 92),
                self.rect.center,
                image.get_width() // 2 + 2,
                width=2,
            )

        surface.blit(image, image.get_rect(center=self.rect.center))

    def _current_animation(self) -> tuple[str, int]:
        if not self.alive:
            frame = int(self.death_animation_timer / self.DEATH_FRAME_TIME)
            return "death", min(frame, 2)

        normal_speed = self.velocity.dot(self.gravity)
        if not self.grounded:
            return ("jump", 0) if normal_speed < 0 else ("fall", 0)

        tangent_speed = self.velocity.dot(tangent_for(self.gravity))
        if abs(tangent_speed) > 20:
            frame = int(self.animation_timer / self.WALK_FRAME_TIME) % 4
            return "walk", frame

        return "idle", 0
