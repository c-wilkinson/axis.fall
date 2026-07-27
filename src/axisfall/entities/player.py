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
from axisfall.world.collision import CollisionWorld


@dataclass(slots=True)
class PlayerInput:
    move: float = 0.0
    jump_pressed: bool = False
    gravity_direction: GravityDirection | None = None
    attack_held: bool = False


class Player:
    SIZE = 30

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

    def update(self, controls: PlayerInput, world: CollisionWorld, dt: float) -> None:
        if not self.alive:
            self.attack_held = False
            self.velocity.update(0, 0)
            return

        self.invulnerability_timer = max(0.0, self.invulnerability_timer - dt)
        self.gravity_flash_timer = max(0.0, self.gravity_flash_timer - dt)
        self.attack_held = controls.attack_held

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
            return

        self.invulnerability_timer = 0.8
        self.velocity = knockback

    def draw(self, surface: pygame.Surface) -> None:
        flashing = self.invulnerability_timer > 0 and int(self.invulnerability_timer * 12) % 2 == 0
        if flashing:
            return

        if not self.alive:
            fill = (90, 92, 98)
        elif self.gravity_flash_timer > 0:
            fill = (136, 212, 255)
        elif self.attack_held:
            fill = (255, 214, 92)
        else:
            fill = (235, 235, 235)

        pygame.draw.rect(surface, fill, self.rect, border_radius=5)
        pygame.draw.rect(surface, (30, 34, 42), self.rect, width=3, border_radius=5)

        centre = pygame.Vector2(self.rect.center)
        gravity_tip = centre + self.gravity * 11
        tangent = tangent_for(self.gravity)
        left = centre - self.gravity * 2 + tangent * 5
        right = centre - self.gravity * 2 - tangent * 5
        pygame.draw.polygon(surface, (30, 34, 42), [gravity_tip, left, right])
