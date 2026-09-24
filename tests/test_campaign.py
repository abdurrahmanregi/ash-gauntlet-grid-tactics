"""Workshop and save tests."""

from __future__ import annotations

import unittest

from ashgauntlet.campaign import Save, materialize, new_game
from ashgauntlet.data import craft_line, gear_bonus, next_enhance_cost, raise_line


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
        asked = raise_line("village_sword", 0)
        self.assertIn("Village Sword", asked)
        self.assertIn("200 souls", asked)
        self.assertIn("attack bonus becomes +2", asked)
        self.assertIn("Continue or cancel.", asked)
        self.assertIn("3 ash", craft_line("ash_blade"))
        self.assertIn("Continue or cancel.", craft_line("ash_blade"))

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

        save.prepare_episode(3)
        chief = materialize(save, "gun_chief", (2, 10))
        self.assertEqual(chief.weapon_family, "gun")
        self.assertIn("shot_2", chief.skills)
        self.assertNotIn("shot_3", chief.skills)
        self.assertEqual(chief.max_hp, 22)
        self.assertEqual(next_enhance_cost("clan_gun", 0), 300)
        self.assertEqual(gear_bonus("clan_gun", 1), 2)
        sword_choices = [g.kind for g in save.gear_choices("gun_chief", "weapon")]
        self.assertEqual(sword_choices, ["clan_gun"])
        self.assertNotIn("clan_gun", [g.kind for g in save.gear_choices("kairo", "weapon")])

    def test_later_recruits_stances_and_depths(self):
        from ashgauntlet.campaign import build_depth, depth_unlocked
        from ashgauntlet.data import level_label

        save = new_game()
        self.assertEqual(level_label(4, "River Stage", "Next"), "Level 4 - River Stage - Next")
        save.prepare_episode(4)
        self.assertIn("stage_man", save.roster)
        stage = materialize(save, "stage_man", (0, 0))
        self.assertIn("strongman", stage.skills)
        self.assertEqual(stage.max_hp, 34)
        save.cleared = [1, 2, 3, 4, 5, 6]
        notes = save.finish_victory(7, type("Loot", (), {"loot_recipes": [], "loot_exp": {}, "loot_souls": 0, "loot_stones": []})())
        self.assertIn("fang", save.stances)
        self.assertTrue(any("Stance" in note for note in notes))
        save.finish_victory(9, type("Loot", (), {"loot_recipes": [], "loot_exp": {}, "loot_souls": 0, "loot_stones": []})())
        self.assertTrue(save.oni_wake)
        kairo = materialize(save, "kairo", (0, 0))
        self.assertIn("oni_wake", kairo.skills)
        self.assertFalse(depth_unlocked(save, 1))
        save.cleared.append(13)
        self.assertTrue(depth_unlocked(save, 1))
        self.assertFalse(depth_unlocked(save, 2))
        battle = build_depth(save, 1, ["kairo"], {}, __import__("random").Random(0))
        battle.outcome = "win"
        battle.loot_recipes = []
        battle.loot_exp = {}
        battle.loot_souls = 10
        battle.loot_stones = ["cinder"]
        save.finish_depth(1, battle)
        self.assertEqual(save.depths_cleared, 1)
        self.assertNotIn("soot_child", save.roster)
        save.cleared.extend([18, 22])
        save.depths_cleared = 11
        self.assertTrue(depth_unlocked(save, 12))
        save.finish_depth(12, battle)
        self.assertIn("soot_child", save.roster)
        self.assertEqual(save.units["soot_child"]["level"], 1)
        again = __import__("ashgauntlet.campaign", fromlist=["Save"]).Save.from_dict(save.to_dict())
        self.assertEqual(again.depths_cleared, 12)
        self.assertTrue(again.oni_wake)
        self.assertIn("fang", again.stances)


if __name__ == "__main__":
    unittest.main()
