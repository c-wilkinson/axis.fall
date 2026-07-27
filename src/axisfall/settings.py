from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    screen_width: int = 1280
    screen_height: int = 720
    title: str = "axis.fall - Test Chamber"
    target_fps: int = 120

    gravity_acceleration: float = 1450.0
    terminal_speed: float = 1000.0
    run_speed: float = 280.0
    ground_acceleration: float = 2100.0
    ground_deceleration: float = 2500.0
    air_acceleration: float = 720.0
    jump_speed: float = 510.0

    impact_speed: float = 360.0
    heavy_impact_speed: float = 680.0
    player_max_health: int = 3
