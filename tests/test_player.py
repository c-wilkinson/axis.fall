from __future__ import annotations

import pygame

from axisfall.entities.player import Player
from axisfall.physics import GravityDirection
from axisfall.settings import Settings


def test_changing_gravity_preserves_velocity() -> None:
    player = Player((100, 100), Settings())
    player.velocity = pygame.Vector2(250, -125)

    player.set_gravity(GravityDirection.LEFT)

    assert player.velocity == pygame.Vector2(250, -125)
    assert player.gravity_direction is GravityDirection.LEFT
    assert not player.grounded


def test_damage_respects_invulnerability_window() -> None:
    player = Player((100, 100), Settings())

    player.take_damage(pygame.Vector2(100, 0))
    player.take_damage(pygame.Vector2(-100, 0))

    assert player.health == player.settings.player_max_health - 1
    assert player.velocity == pygame.Vector2(100, 0)
