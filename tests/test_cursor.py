"""The click follows the ground diamond, not the tall picture covering it."""

from __future__ import annotations

import os
import random
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from ashgauntlet.app import Game, closest_diamond
from ashgauntlet.rules import Battle, Unit


def fighter(**kw) -> Unit:
    base = dict(
        id="hero",
        name="Hero",
        side="player",
        sprite="kairo",
        pos=(0, 0),
        hp=30,
        max_hp=30,
        sp=30,
        max_sp=30,
        atk=8,
        defn=4,
        mov=5,
        weapon_family="sword",
        weapon_atk=0,
        skills=[],
        items=[None, None],
    )
    base.update(kw)
    return Unit(**base)


class CursorTests(unittest.TestCase):
    def test_stacked_diamonds_stay_distinct(self):
        front = (2, 2)
        rear = (1, 1)
        further = (0, 0)
        diamonds = [(front, 0, 0), (rear, 0, -40), (further, 0, -80)]
        self.assertEqual(closest_diamond(0, 0, diamonds), front)
        self.assertEqual(closest_diamond(0, -40, diamonds), rear)
        # The chest of the front picture hangs over the tile two steps behind.
        self.assertEqual(closest_diamond(0, -70, diamonds), further)
        self.assertIsNone(closest_diamond(0, -120, diamonds))

    def test_side_neighbor_is_not_stolen(self):
        front = (2, 2)
        side = (1, 2)
        diamonds = [(front, 0, 0), (side, -40, -20)]
        self.assertEqual(closest_diamond(0, 0, diamonds), front)
        self.assertEqual(closest_diamond(-40, -20, diamonds), side)

    def test_pick_reaches_the_fighter_hidden_behind_a_picture(self):
        game = Game()
        try:
            front = fighter(pos=(5, 5), id="front", name="Front")
            rear = fighter(pos=(4, 4), id="rear", name="Rear", side="enemy")
            game.battle = Battle(8, 8, {}, set(), [front, rear], [], random.Random(0))
            game.cam = [0, 0]
            cx, cy = game.iso(4, 4)
            picked = game.pick(cx, cy)
            self.assertEqual(picked[0], "unit")
            self.assertEqual(picked[1].id, "rear")
            cx, cy = game.iso(5, 5)
            picked = game.pick(cx, cy)
            self.assertEqual(picked[1].id, "front")
            # A point on the front picture, above that fighter's own diamond,
            # belongs to the tile behind them — not to the covering sprite.
            fx, fy = game.iso(5, 5)
            covered = game.pick(fx, fy - 40)
            self.assertEqual(covered[1].id, "rear")
            high = fighter(pos=(3, 3), id="high", name="High", side="enemy")
            game.battle = Battle(8, 8, {(3, 3): 2}, set(), [high], [], random.Random(0))
            hx, hy = game.iso(3, 3)
            self.assertEqual(game.pick(hx, hy - 32)[1].id, "high")
        finally:
            pygame.quit()
