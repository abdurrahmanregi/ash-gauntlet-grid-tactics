"""Reading-box sentences stay true to the rules."""

from __future__ import annotations

import unittest

from ashgauntlet.campaign import new_game
from ashgauntlet.rules import Unit
from ashgauntlet.sheets import (
    describe_body,
    fighter_block,
    gear_lines,
    recipe_lines,
    soul_lines,
    stone_lines,
    workshop_intro,
)


def joined(lines) -> str:
    return " ".join(lines)


class SheetTests(unittest.TestCase):
    def test_stones_and_souls_say_what_they_are_for(self):
        intro = joined(workshop_intro())
        self.assertIn("Pawns drop Ash", intro)
        self.assertIn("Spear fighters", intro)
        self.assertIn("Souls only raise", intro)
        self.assertIn("not money", intro)

        bone = joined(stone_lines("bone", 2))
        self.assertIn("You have 2", bone)
        self.assertIn("Bushi", bone)
        self.assertIn("Line Spear needs 1", bone)
        self.assertIn("Paper Charm needs 1", bone)
        self.assertIn("does not spend", bone)

        cinder = joined(stone_lines("cinder", 0))
        self.assertIn("not dropped", cinder)
        self.assertIn("No recipe", cinder)

        souls = joined(soul_lines(30))
        self.assertIn("30 souls", souls)
        self.assertIn("spends stones instead", souls)
        self.assertIn("half the attack", souls)

    def test_weapon_and_upgrade_numbers(self):
        sword = joined(gear_lines("village_sword", 1, None, souls=30))
        self.assertIn("Village Sword +1", sword)
        self.assertIn("Spare", sword)
        self.assertIn("Adds +2 attack", sword)
        self.assertIn("400 souls", sword)
        self.assertIn("becomes +4", sword)
        self.assertIn("does not add on top", sword)
        self.assertIn("button stays dark", sword)
        self.assertIn("Double Cut", sword)
        self.assertIn("Kairo or Sword-Two", sword)
        self.assertNotIn("Shio", sword)
        self.assertIn("same kind of sword", sword)

        light = joined(gear_lines("light_sword", 0, "Shio", souls=200))
        self.assertIn("Adds +0 attack", light)
        self.assertIn("200 souls", light)
        self.assertIn("becomes +1", light)
        self.assertIn("never learns Double Cut", light)
        self.assertIn("Only Shio", light)
        self.assertNotIn("stays dark", light)

        charm = joined(gear_lines("paper_charm", 2, "Kairo", souls=0))
        self.assertIn("Adds +2 defense", charm)
        self.assertIn("cannot be raised further", charm)
        self.assertIn("Heal", charm)
        self.assertIn("Anyone can wear", charm)

        dagger = joined(gear_lines("traveler_dagger", 0))
        self.assertIn("cannot be raised", dagger)
        self.assertIn("Only Swallow", dagger)

        gun = joined(gear_lines("clan_gun", 0, "Gun-Chief", souls=200))
        self.assertIn("Clan Gun +0", gun)
        self.assertIn("300 souls", gun)
        self.assertIn("becomes +2", gun)
        self.assertIn("button stays dark", gun)
        self.assertIn("Only Gun-Chief", gun)
        self.assertIn("5 tiles", gun)
        self.assertIn("cannot set Issen", gun)

    def test_recipe_names_the_stones(self):
        text = joined(recipe_lines("ash_blade", {"ash": 1}, False))
        self.assertIn("3 Ash", text)
        self.assertIn("You have 1", text)
        self.assertIn("not enough", text)
        self.assertIn("not souls", text)
        self.assertIn("Kairo or Sword-Two", text)
        self.assertNotIn("Shio", text)
        spear = joined(recipe_lines("line_spear", {"ash": 2, "bone": 1}, True))
        self.assertIn("2 Ash", spear)
        self.assertIn("1 Bone", spear)
        self.assertIn("enough", spear)
        self.assertNotIn("stays dark", spear)

    def test_fighter_sheet_includes_level_gear_and_skills(self):
        save = new_game()
        save.units["kairo"]["level"] = 4
        save.units["kairo"]["exp"] = 60
        sword = save.equipped("kairo", "weapon")
        sword.plus = 1
        save.add_gear("cedar_coat", owner="kairo", plus=0)
        block = describe_body(save, "kairo")
        text = joined([block["title"], *block["summary"], *block["details"]])
        self.assertIn("Level 4", text)
        self.assertIn("60/100", text)
        self.assertIn("Health 37/37", text)
        self.assertIn("Skill points 23/23", text)
        self.assertIn("Attack 13", text)
        self.assertIn("Village Sword +1", text)
        self.assertIn("Defense 4", text)
        self.assertIn("Move 5", text)
        self.assertIn("Shockwave", text)
        self.assertIn("level 12", text)
        self.assertIn("400 souls", text)
        self.assertIn("this fight is lost", text)

    def test_enemy_sheet_and_mode_bonus(self):
        pawn = Unit(
            id="pawn",
            name="Pawn",
            side="enemy",
            hp=12,
            max_hp=12,
            sp=0,
            max_sp=0,
            atk=6,
            defn=1,
            mov=4,
            weapon_family="sword",
            skills=[],
            stone="ash",
            exp_value=40,
            recipe="cedar_coat",
        )
        text = joined(fighter_block(pawn, strike=5, in_reach=True, actor_name="Kairo")["details"])
        self.assertIn("No skills", text)
        self.assertIn("40 experience", text)
        self.assertIn("10 souls", text)
        self.assertIn("1 Ash", text)
        self.assertIn("Cedar Coat", text)
        self.assertIn("deals 5", text)
        pawn.mode = "strongman"
        attack = joined(fighter_block(pawn)["summary"])
        self.assertIn("Attack 14", attack)
        self.assertIn("Strongman", attack)

    def test_victory_notes_name_the_stones(self):
        from ashgauntlet.campaign import new_game as fresh

        class Loot:
            loot_recipes = []
            loot_exp = {}
            loot_souls = 10
            loot_stones = ["ash", "bone"]

        notes = " ".join(fresh().finish_victory(1, Loot()))
        self.assertIn("Ash", notes)
        self.assertIn("Bone", notes)
        self.assertIn("only raise", notes)
        self.assertIn("Pawns drop Ash", notes)


if __name__ == "__main__":
    unittest.main()
