from __future__ import annotations

from enum import Enum

import pygame


class GravityDirection(Enum):
    DOWN = (0.0, 1.0)
    UP = (0.0, -1.0)
    LEFT = (-1.0, 0.0)
    RIGHT = (1.0, 0.0)

    @property
    def vector(self) -> pygame.Vector2:
        return pygame.Vector2(self.value)

    @property
    def label(self) -> str:
        return self.name.title()


def tangent_for(gravity: pygame.Vector2) -> pygame.Vector2:
    return pygame.Vector2(gravity.y, -gravity.x)


def approach(current: float, target: float, maximum_delta: float) -> float:
    if current < target:
        return min(current + maximum_delta, target)
    return max(current - maximum_delta, target)


def clamp_vector_component(
    velocity: pygame.Vector2,
    axis: pygame.Vector2,
    minimum: float,
    maximum: float,
) -> pygame.Vector2:
    component = velocity.dot(axis)
    clamped = max(minimum, min(maximum, component))
    return velocity + axis * (clamped - component)
