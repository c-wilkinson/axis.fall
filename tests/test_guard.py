from __future__ import annotations

import pygame

from axisfall.entities.guard import Guard
from axisfall.entities.player import Player
from axisfall.settings import Settings


def make_overlapping_entities() -> tuple[Player, Guard]:
    settings = Settings()
    player = Player((100, 100), settings)
    guard = Guard((100, 115), settings)
    player.rect.center = guard.rect.center
    player.position = pygame.Vector2(player.rect.center)
    return player, guard


def test_fast_braced_impact_damages_guard() -> None:
    player, guard = make_overlapping_entities()
    player.attack_held = True
    player.velocity = pygame.Vector2(player.settings.impact_speed + 1, 0)

    event = guard.update(player, 0.0)

    assert event == "hit"
    assert guard.health == guard.max_health - 1
    assert player.health == player.settings.player_max_health


def test_slow_contact_damages_player_not_guard() -> None:
    player, guard = make_overlapping_entities()
    player.attack_held = True
    player.velocity = pygame.Vector2(player.settings.impact_speed - 1, 0)

    event = guard.update(player, 0.0)

    assert event == "player_hurt"
    assert player.health == player.settings.player_max_health - 1
    assert guard.health == guard.max_health
