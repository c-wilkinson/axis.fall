from __future__ import annotations

from importlib.resources import as_file, files

import pygame

from axisfall.physics import GravityDirection


class PlayerSprites:
    FRAME_SIZE = (48, 48)
    ANIMATIONS = {
        "idle": ("idle.png",),
        "walk": ("walk_0.png", "walk_1.png", "walk_2.png", "walk_3.png"),
        "jump": ("jump.png",),
        "fall": ("fall.png",),
        "death": ("death_0.png", "death_1.png", "death_2.png"),
    }
    ROTATION = {
        GravityDirection.DOWN: 0,
        GravityDirection.LEFT: -90,
        GravityDirection.UP: 180,
        GravityDirection.RIGHT: 90,
    }

    def __init__(self) -> None:
        self.animations = {
            name: tuple(self._load(filename) for filename in filenames)
            for name, filenames in self.ANIMATIONS.items()
        }
        self._oriented_cache: dict[
            tuple[str, int, int, GravityDirection], pygame.Surface
        ] = {}

    @classmethod
    def _load(cls, filename: str) -> pygame.Surface:
        resource = files("axisfall").joinpath("assets", "player", filename)
        with as_file(resource) as path:
            image = pygame.image.load(path).convert_alpha()
        if image.get_size() != cls.FRAME_SIZE:
            image = pygame.transform.scale(image, cls.FRAME_SIZE)
        return image

    def frame(
        self,
        animation: str,
        index: int,
        facing: int,
        gravity_direction: GravityDirection,
    ) -> pygame.Surface:
        frames = self.animations[animation]
        index = max(0, min(index, len(frames) - 1))
        normalised_facing = 1 if facing >= 0 else -1
        key = (animation, index, normalised_facing, gravity_direction)

        if key not in self._oriented_cache:
            image = frames[index]
            if normalised_facing < 0:
                image = pygame.transform.flip(image, True, False)
            image = pygame.transform.rotate(image, self.ROTATION[gravity_direction])
            self._oriented_cache[key] = image

        return self._oriented_cache[key]
