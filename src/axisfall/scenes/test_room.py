from __future__ import annotations

from collections.abc import Iterable

import pygame

from axisfall.entities.guard import Guard
from axisfall.entities.player import Player, PlayerInput
from axisfall.physics import GravityDirection
from axisfall.scenes.base import Scene
from axisfall.settings import Settings
from axisfall.world.collision import CollisionWorld


class TestRoomScene(Scene):
    BACKGROUND = (21, 24, 31)
    SOLID = (72, 78, 91)
    SOLID_EDGE = (108, 116, 132)
    TEXT = (224, 227, 234)
    MUTED = (155, 162, 177)

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.font = pygame.font.Font(None, 26)
        self.small_font = pygame.font.Font(None, 21)
        self.solids = self._build_room()
        self.world = CollisionWorld(self.solids)
        self.player = Player((130, 625), settings)
        self.guard = Guard((1050, 656), settings)
        self.debug_visible = True
        self.jump_queued = False
        self.gravity_queued: GravityDirection | None = None
        self.message = "Build speed, hold F, then strike the guard."
        self.message_timer = 4.0

    def _build_room(self) -> list[pygame.Rect]:
        return [
            pygame.Rect(0, 0, 1280, 32),
            pygame.Rect(0, 688, 1280, 32),
            pygame.Rect(0, 0, 32, 720),
            pygame.Rect(1248, 0, 32, 720),
            pygame.Rect(32, 656, 350, 32),
            pygame.Rect(470, 544, 300, 28),
            pygame.Rect(342, 382, 30, 180),
            pygame.Rect(760, 324, 30, 248),
            pygame.Rect(112, 254, 350, 28),
            pygame.Rect(612, 168, 470, 28),
            pygame.Rect(1050, 196, 32, 226),
            pygame.Rect(874, 420, 180, 26),
            pygame.Rect(940, 656, 308, 32),
            pygame.Rect(220, 572, 72, 84),
            pygame.Rect(548, 464, 76, 80),
            pygame.Rect(1130, 520, 118, 28),
        ]

    def reset(self) -> None:
        self.player.reset()
        self.guard.reset()
        self.message = "Room reset. Momentum is preserved when gravity changes."
        self.message_timer = 2.8

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.KEYDOWN:
            return

        if event.key == pygame.K_SPACE:
            self.jump_queued = True
        elif event.key == pygame.K_UP:
            self.gravity_queued = GravityDirection.UP
        elif event.key == pygame.K_DOWN:
            self.gravity_queued = GravityDirection.DOWN
        elif event.key == pygame.K_LEFT:
            self.gravity_queued = GravityDirection.LEFT
        elif event.key == pygame.K_RIGHT:
            self.gravity_queued = GravityDirection.RIGHT
        elif event.key == pygame.K_r:
            self.reset()
        elif event.key == pygame.K_F1:
            self.debug_visible = not self.debug_visible

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        move = float(keys[pygame.K_d]) - float(keys[pygame.K_a])
        controls = PlayerInput(
            move=move,
            jump_pressed=self.jump_queued,
            gravity_direction=self.gravity_queued,
            attack_held=keys[pygame.K_f],
        )
        self.jump_queued = False
        self.gravity_queued = None

        self.player.update(controls, self.world, dt)
        event = self.guard.update(self.player, dt)
        if event == "hit":
            self.message = "Momentum strike!"
            self.message_timer = 1.0
        elif event == "heavy_hit":
            self.message = "Heavy momentum strike!"
            self.message_timer = 1.2
        elif event == "player_hurt":
            self.message = "Too slow. Alex loses a direct fight."
            self.message_timer = 1.7

        if not self.guard.alive:
            self.message = "Guard defeated. Press R to reset the chamber."
            self.message_timer = 999.0
        elif self.player.health <= 0:
            self.message = "Alex is down. Press R to try again."
            self.message_timer = 999.0

        self.message_timer = max(0.0, self.message_timer - dt)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(self.BACKGROUND)
        self._draw_grid(surface)
        self._draw_solids(surface)
        self._draw_gravity_markers(surface)
        self.guard.draw(surface)
        self.player.draw(surface)
        self._draw_hud(surface)
        if self.debug_visible:
            self._draw_debug(surface)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        for x in range(0, self.settings.screen_width, 32):
            pygame.draw.line(surface, (29, 33, 42), (x, 0), (x, self.settings.screen_height))
        for y in range(0, self.settings.screen_height, 32):
            pygame.draw.line(surface, (29, 33, 42), (0, y), (self.settings.screen_width, y))

    def _draw_solids(self, surface: pygame.Surface) -> None:
        for solid in self.solids:
            pygame.draw.rect(surface, self.SOLID, solid)
            pygame.draw.rect(surface, self.SOLID_EDGE, solid, width=2)

    def _draw_gravity_markers(self, surface: pygame.Surface) -> None:
        markers = [
            ((640, 80), GravityDirection.UP),
            ((640, 640), GravityDirection.DOWN),
            ((76, 360), GravityDirection.LEFT),
            ((1204, 360), GravityDirection.RIGHT),
        ]
        for centre, direction in markers:
            vector = direction.vector
            start = pygame.Vector2(centre) - vector * 13
            end = pygame.Vector2(centre) + vector * 13
            pygame.draw.line(surface, (67, 145, 186), start, end, width=3)
            tangent = pygame.Vector2(-vector.y, vector.x)
            pygame.draw.polygon(
                surface,
                (67, 145, 186),
                [end, end - vector * 7 + tangent * 5, end - vector * 7 - tangent * 5],
            )

    def _draw_hud(self, surface: pygame.Surface) -> None:
        title = self.font.render("AXISFALL // GRAVITY TEST CHAMBER", True, self.TEXT)
        surface.blit(title, (48, 46))

        controls = self.small_font.render(
            "A/D move   SPACE jump   ARROWS gravity   hold F impact   R reset   F1 debug",
            True,
            self.MUTED,
        )
        surface.blit(controls, (48, 76))

        health = "■" * max(0, self.player.health) + "□" * max(
            0, self.settings.player_max_health - self.player.health
        )
        health_text = self.font.render(f"Alex  {health}", True, self.TEXT)
        surface.blit(health_text, (48, 108))

        if self.message_timer > 0:
            message_surface = self.font.render(self.message, True, (255, 220, 118))
            message_rect = message_surface.get_rect(midbottom=(640, 680))
            background = message_rect.inflate(24, 14)
            pygame.draw.rect(surface, (18, 20, 26), background, border_radius=7)
            pygame.draw.rect(surface, (78, 82, 91), background, width=2, border_radius=7)
            surface.blit(message_surface, message_rect)

    def _draw_debug(self, surface: pygame.Surface) -> None:
        lines: Iterable[str] = [
            f"gravity: {self.player.gravity_direction.label}",
            f"velocity: ({self.player.velocity.x:7.1f}, {self.player.velocity.y:7.1f})",
            f"speed: {self.player.speed:6.1f}",
            f"grounded: {self.player.grounded}",
            f"impact ready: {self.player.attack_held and self.player.speed >= self.settings.impact_speed}",
            f"guard health: {self.guard.health}/{self.guard.max_health}",
        ]
        box = pygame.Rect(930, 42, 290, 154)
        pygame.draw.rect(surface, (15, 17, 22), box, border_radius=8)
        pygame.draw.rect(surface, (75, 82, 96), box, width=2, border_radius=8)
        y = box.top + 13
        for line in lines:
            rendered = self.small_font.render(line, True, self.TEXT)
            surface.blit(rendered, (box.left + 14, y))
            y += 22

        if self.player.velocity.length_squared() > 1:
            start = pygame.Vector2(self.player.rect.center)
            end = start + self.player.velocity.normalize() * min(90, self.player.speed * 0.12)
            pygame.draw.line(surface, (255, 205, 92), start, end, width=3)
            pygame.draw.circle(surface, (255, 205, 92), end, 4)
