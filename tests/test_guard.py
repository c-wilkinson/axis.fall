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

def test_stationary_guard_does_not_move() -> None:
    settings = Settings()
    player = Player((500, 500), settings)
    guard = Guard((100, 115), settings)
    starting_position = guard.rect.center

    guard.update(player, 1.0)

    assert guard.rect.center == starting_position

def test_patrolling_guard_moves_between_patrol_limits() -> None:
    settings = Settings()
    player = Player((500, 500), settings)
    guard = Guard(
        (100, 115),
        settings,
        patrol_range=(100, 200),
        patrol_speed=50.0,
    )

    guard.update(player, 1.0)
    assert guard.rect.centerx == 150

    guard.update(player, 1.0)
    assert guard.rect.centerx == 200

    guard.update(player, 0.5)
    assert guard.rect.centerx == 175


def test_reset_returns_patrolling_guard_to_start() -> None:
    settings = Settings()
    player = Player((500, 500), settings)
    guard = Guard(
        (100, 115),
        settings,
        patrol_range=(100, 200),
        patrol_speed=50.0,
    )

    guard.update(player, 1.0)
    guard.reset()

    assert guard.rect.midbottom == (100, 115)