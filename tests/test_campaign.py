"""Workshop and save tests."""

from __future__ import annotations

import unittest

from ashgauntlet.campaign import Save, materialize, new_game
from ashgauntlet.data import gear_bonus


class CampaignTests(unittest.TestCase):
    def test_craft_enhance_and_roundtrip(self):
        save = new_game()
        save.stones["ash"] = 3
        self.assertFalse(save.craft("ash_blade"))
        save.recipes.append("ash_blade")
        self.assertTrue(save.craft("ash_blade"))
        self.assertEqual(save.stones["ash"], 0)
        blade = [g for g in save.gear if g.kind == "ash_blade"][0]
        self.assertIsNone(blade.owner)
        save.souls = 199
        self.assertFalse(save.enhance(blade.uid))
        save.souls = 200
        self.assertTrue(save.enhance(blade.uid))
        self.assertEqual(blade.plus, 1)
        self.assertEqual(save.souls, 0)
        self.assertEqual(gear_bonus("ash_blade", 1), 2)

        light = [g for g in save.gear if g.kind == "light_sword"]
        self.assertEqual(light, [])
        save.recruit("shio")
        charm_sword = save.equipped("shio", "weapon")
        self.assertEqual(charm_sword.kind, "light_sword")
        save.souls = 200
        save.enhance(charm_sword.uid)
        self.assertEqual(gear_bonus("light_sword", 1), 1)

        again = Save.from_dict(save.to_dict())
        self.assertEqual(again.souls, save.souls)
        self.assertEqual(again.equipped("kairo", "weapon").kind, "village_sword")
        self.assertEqual(len(again.gear), len(save.gear))

    def test_level_and_family_lock(self):
        save = new_game()
        save.recruit("shio")
        notes = save.grant_exp({"kairo": 100})
        self.assertEqual(save.units["kairo"]["level"], 2)
        self.assertEqual(save.units["kairo"]["exp"], 0)
        self.assertTrue(any("Kairo" in note for note in notes))
        unit = materialize(save, "kairo", (0, 0))
        self.assertEqual(unit.max_hp, 31)

        choices = [g.kind for g in save.gear_choices("shio", "weapon")]
        self.assertNotIn("ash_blade", choices)
        self.assertNotIn("village_sword", choices)


if __name__ == "__main__":
    unittest.main()
