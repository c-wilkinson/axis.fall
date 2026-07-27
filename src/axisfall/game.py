from __future__ import annotations

import pygame

from axisfall.scenes.test_room import TestRoomScene
from axisfall.settings import Settings


class Game:
    def __init__(self, settings: Settings | None = None) -> None:
        pygame.init()
        self.settings = settings or Settings()
        self.screen = pygame.display.set_mode(
            (self.settings.screen_width, self.settings.screen_height)
        )
        pygame.display.set_caption(self.settings.title)
        self.clock = pygame.time.Clock()
        self.scene = TestRoomScene(self.settings)
        self.running = True

    def run(self) -> None:
        try:
            while self.running:
                dt = min(self.clock.tick(self.settings.target_fps) / 1000.0, 1 / 30)
                self._handle_events()
                self.scene.update(dt)
                self.scene.draw(self.screen)
                pygame.display.flip()
        finally:
            pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            else:
                self.scene.handle_event(event)
