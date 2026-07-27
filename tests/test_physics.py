from __future__ import annotations

import pygame
import pytest

from axisfall.physics import GravityDirection, approach, clamp_vector_component, tangent_for


def test_tangent_is_perpendicular_to_every_gravity_direction() -> None:
    for direction in GravityDirection:
        gravity = direction.vector
        tangent = tangent_for(gravity)
        assert tangent.dot(gravity) == pytest.approx(0.0)
        assert tangent.length() == pytest.approx(1.0)


def test_approach_does_not_overshoot() -> None:
    assert approach(0.0, 10.0, 3.0) == 3.0
    assert approach(9.0, 10.0, 3.0) == 10.0
    assert approach(0.0, -10.0, 4.0) == -4.0
    assert approach(-8.0, -10.0, 4.0) == -10.0


def test_clamp_vector_component_preserves_perpendicular_motion() -> None:
    velocity = pygame.Vector2(30, 120)
    clamped = clamp_vector_component(velocity, pygame.Vector2(0, 1), -50, 80)
    assert clamped.x == pytest.approx(30)
    assert clamped.y == pytest.approx(80)
