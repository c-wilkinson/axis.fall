from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(slots=True)
class CollisionResult:
    normal: pygame.Vector2
    collider: pygame.Rect


class CollisionWorld:
    def __init__(self, solids: list[pygame.Rect]) -> None:
        self.solids = solids

    def move(
        self,
        rect: pygame.Rect,
        position: pygame.Vector2,
        velocity: pygame.Vector2,
        dt: float,
    ) -> tuple[pygame.Vector2, pygame.Vector2, list[CollisionResult]]:
        collisions: list[CollisionResult] = []

        position.x += velocity.x * dt
        rect.centerx = round(position.x)
        for solid in self.solids:
            if not rect.colliderect(solid):
                continue
            if velocity.x > 0:
                rect.right = solid.left
                normal = pygame.Vector2(-1, 0)
            elif velocity.x < 0:
                rect.left = solid.right
                normal = pygame.Vector2(1, 0)
            else:
                continue
            position.x = float(rect.centerx)
            velocity.x = 0.0
            collisions.append(CollisionResult(normal, solid))

        position.y += velocity.y * dt
        rect.centery = round(position.y)
        for solid in self.solids:
            if not rect.colliderect(solid):
                continue
            if velocity.y > 0:
                rect.bottom = solid.top
                normal = pygame.Vector2(0, -1)
            elif velocity.y < 0:
                rect.top = solid.bottom
                normal = pygame.Vector2(0, 1)
            else:
                continue
            position.y = float(rect.centery)
            velocity.y = 0.0
            collisions.append(CollisionResult(normal, solid))

        rect.center = (round(position.x), round(position.y))
        return position, velocity, collisions

    def touching_in_direction(self, rect: pygame.Rect, direction: pygame.Vector2) -> bool:
        probe = rect.move(round(direction.x * 2), round(direction.y * 2))
        return any(probe.colliderect(solid) for solid in self.solids)
