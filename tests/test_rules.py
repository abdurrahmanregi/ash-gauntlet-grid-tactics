"""Rule tests for the first march. No window required."""

from __future__ import annotations

import random
import unittest

from ashgauntlet.autoplay import play
from ashgauntlet.campaign import build_battle, default_items, default_order, new_game
from ashgauntlet.data import episode
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


def make(units, w=6, h=6, heights=None, blocked=None, rng=None, reins=None) -> Battle:
    return Battle(w, h, heights or {}, blocked or set(), units, reins or [], rng or random.Random(0))


def run_enemies(battle: Battle) -> None:
    guard = 0
    while battle.phase == "enemy" and battle.outcome is None and guard < 40:
        battle.enemy_step()
        guard += 1


class RuleTests(unittest.TestCase):
    def test_height_cost_and_gap(self):
        hero = fighter(pos=(0, 0), mov=2)
        battle = make([hero], heights={(1, 0): 1})
        stand, _prev = battle.movement(hero)
        self.assertIn((1, 0), stand)
        self.assertEqual(stand[(1, 0)], 2)
        self.assertNotIn((2, 0), stand)

        hero.pos = (0, 0)
        battle = make([hero], heights={(1, 0): 2})
        stand, _prev = battle.movement(hero)
        self.assertNotIn((1, 0), stand)
        foe = fighter(id="pawn", name="Pawn", side="enemy", pos=(1, 0), hp=10, defn=0)
        battle = make([hero, foe], heights={(1, 0): 2})
        self.assertEqual(battle.attack_targets(hero, hero.pos), [])

    def test_pass_allies_not_enemies(self):
        hero = fighter(pos=(0, 0), mov=2)
        ally = fighter(id="ally", name="Ally", pos=(1, 0), gid=None)
        battle = make([hero, ally])
        stand, _prev = battle.movement(hero)
        self.assertIn((2, 0), stand)
        self.assertNotIn((1, 0), stand)

        enemy = fighter(id="e", name="E", side="enemy", pos=(1, 0))
        battle = make([hero, enemy])
        stand, _prev = battle.movement(hero)
        self.assertNotIn((2, 0), stand)
        self.assertNotIn((1, 0), stand)

    def test_damage_and_spear_and_gun(self):
        hero = fighter(atk=8, weapon_atk=2, defn=4)
        foe = fighter(id="e", name="E", side="enemy", pos=(1, 0), atk=6, defn=3, hp=20, max_hp=20)
        battle = make([hero, foe])
        self.assertEqual(battle.preview_damage(hero, foe), 7)
        foe.mode = "target"
        self.assertEqual(battle.preview_damage(hero, foe), 11)

        hero.weapon_family = "spear"
        hero.pos = (0, 0)
        ally = fighter(id="ally", name="Ally", pos=(1, 0))
        far = fighter(id="far", name="Far", side="enemy", pos=(2, 0), hp=10)
        battle = make([hero, ally, far])
        gids = {u.gid for u in battle.attack_targets(hero, hero.pos)}
        self.assertIn(far.gid, gids)

        blocker = fighter(id="block", name="Block", side="enemy", pos=(1, 0), hp=10)
        far.pos = (2, 0)
        battle = make([hero, blocker, far])
        gids = {u.gid for u in battle.attack_targets(hero, hero.pos)}
        self.assertIn(blocker.gid, gids)
        self.assertNotIn(far.gid, gids)

        shooter = fighter(weapon_family="gun", pos=(0, 0))
        straight = fighter(id="s", name="S", side="enemy", pos=(0, 3), hp=10)
        diag = fighter(id="d", name="D", side="enemy", pos=(2, 2), hp=10)
        crooked = fighter(id="c", name="C", side="enemy", pos=(2, 1), hp=10)
        battle = make([shooter, straight, diag, crooked])
        gids = {u.gid for u in battle.attack_targets(shooter, shooter.pos)}
        self.assertIn(straight.gid, gids)
        self.assertIn(diag.gid, gids)
        self.assertNotIn(crooked.gid, gids)
        wall = fighter(id="w", name="W", side="player", pos=(0, 1))
        battle = make([shooter, wall, straight])
        gids = {u.gid for u in battle.attack_targets(shooter, shooter.pos)}
        self.assertNotIn(straight.gid, gids)

    def test_issen_and_lord_and_loss(self):
        hero = fighter(pos=(1, 1), hp=20, max_hp=20, issen=True)
        foe = fighter(id="e", name="E", side="enemy", pos=(1, 2), hp=12, atk=9, defn=0, exp_value=40, stone="ash")
        battle = make([hero, foe])
        battle.phase = "enemy"
        events, err = battle.apply_act(foe, foe.pos, {"type": "attack", "target": hero.gid})
        self.assertIsNone(err)
        self.assertEqual(hero.hp, 20)
        self.assertFalse(foe.alive)
        self.assertEqual(battle.loot_souls, 40)
        self.assertTrue(any(ev["t"] == "die" for ev in events))

        hero = fighter(pos=(0, 2), issen=True, hp=20, max_hp=20)
        spear = fighter(
            id="s",
            name="S",
            side="enemy",
            pos=(0, 0),
            weapon_family="spear",
            atk=8,
            defn=0,
            hp=20,
        )
        battle = make([hero, spear])
        battle.phase = "enemy"
        _events, err = battle.apply_act(spear, spear.pos, {"type": "attack", "target": hero.gid})
        self.assertIsNone(err)
        self.assertLess(hero.hp, 20)
        self.assertTrue(hero.issen)
        self.assertTrue(spear.alive)

        hero = fighter(id="kairo", name="Kairo", pos=(0, 0), hp=4, max_hp=4, defn=0, issen=True, lose_flag=True)
        lord = fighter(id="lord", name="Lord", side="enemy", pos=(1, 0), hp=30, atk=8, defn=0, is_lord=True)
        battle = make([hero, lord])
        battle.phase = "enemy"
        battle.apply_act(lord, lord.pos, {"type": "attack", "target": hero.gid})
        self.assertLess(hero.hp, 5)
        self.assertTrue(lord.alive)
        self.assertFalse(hero.issen)
        self.assertEqual(battle.outcome, "lose")

    def test_rout_heal_herb_and_strongman(self):
        hero = fighter(pos=(0, 0), atk=8, skills=["heal_one", "strongman"], sp=30, max_sp=30)
        foe = fighter(id="e", name="E", side="enemy", pos=(1, 0), hp=1, defn=0, exp_value=40, stone="ash", recipe="ash_blade")
        ally = fighter(id="ally", name="Ally", pos=(0, 1), hp=10, max_hp=20)
        battle = make([hero, foe, ally])
        _events, err = battle.player_act(hero.gid, hero.pos, {"type": "attack", "target": foe.gid})
        self.assertIsNone(err)
        self.assertEqual(battle.outcome, "win")
        self.assertEqual(battle.loot_souls, 10)
        self.assertEqual(battle.loot_recipes, ["ash_blade"])
        self.assertEqual(battle.loot_exp["hero"], 40)

        hero = fighter(id="shio", name="Shio", pos=(0, 0), skills=["heal_one"], sp=10, max_hp=18, hp=18)
        ally = fighter(id="ally", name="Ally", pos=(1, 0), hp=4, max_hp=20)
        battle = make([hero, ally])
        _events, err = battle.player_act(hero.gid, hero.pos, {"type": "skill", "skill": "heal_one", "target": ally.gid})
        self.assertIsNone(err)
        self.assertEqual(ally.hp, 11)

        hurt = fighter(id="shio", name="Shio", pos=(0, 0), skills=["heal_one"], sp=10, max_hp=18, hp=10)
        battle = make([hurt])
        self.assertIn(hurt.gid, battle.skill_options(hurt, hurt.pos, "heal_one")["gids"])
        _events, err = battle.player_act(hurt.gid, hurt.pos, {"type": "skill", "skill": "heal_one", "target": hurt.gid})
        self.assertIsNone(err)
        self.assertEqual(hurt.hp, 17)

        hero = fighter(pos=(0, 0), hp=10, max_hp=30, items=["herb", None])
        battle = make([hero])
        battle.player_act(hero.gid, hero.pos, {"type": "item", "slot": 0, "target": hero.gid})
        self.assertEqual(hero.hp, 25)
        self.assertIsNone(hero.items[0])

        hero = fighter(pos=(0, 0), atk=6, skills=["strongman"], sp=8, hp=100, max_hp=100, defn=0)
        foe = fighter(id="e", name="E", side="enemy", pos=(4, 4), hp=100, max_hp=100, atk=1, defn=0, mov=4)
        battle = make([hero, foe], w=8, h=8)
        battle.player_act(hero.gid, hero.pos, {"type": "skill", "skill": "strongman"})
        self.assertEqual(hero.mode, "strongman")
        self.assertEqual(battle.preview_damage(hero, foe), 14)
        battle.end_player_phase()
        run_enemies(battle)
        battle.player_act(hero.gid, hero.pos, {"type": "wait"})
        self.assertEqual(hero.mode, "strongman")
        self.assertEqual(hero.mode_left, 1)
        battle.end_player_phase()
        run_enemies(battle)
        self.assertEqual(battle.preview_damage(hero, foe), 14)
        battle.player_act(hero.gid, hero.pos, {"type": "wait"})
        self.assertIsNone(hero.mode)
        self.assertEqual(battle.preview_damage(hero, foe), 6)

    def test_maps_and_reinforcement(self):
        for episode_id in (1, 2, 3):
            ep = episode(episode_id)
            from ashgauntlet.data import grid_from_rows

            _heights, width, height = grid_from_rows(ep["heights"])
            blocked = set(map(tuple, ep["blocked"]))
            spots = [tuple(p) for p in ep["slots"]]
            spots += [tuple(e["pos"]) for e in ep["enemies"]]
            spots += [tuple(r["pos"]) for r in ep["reinforcements"]]
            self.assertEqual(len(spots), len(set(spots)))
            for spot in spots:
                self.assertTrue(0 <= spot[0] < width and 0 <= spot[1] < height)
                self.assertNotIn(spot, blocked)

        save = new_game()
        battle = build_battle(save, 1, ["kairo", "sword_two"], {}, random.Random(0))
        self.assertFalse(any(u.id == "shio" for u in battle.units))
        battle.end_player_phase()
        run_enemies(battle)
        arrived = [u for u in battle.units if u.id == "shio" and u.alive]
        self.assertEqual(len(arrived), 1)
        self.assertTrue(arrived[0].lose_flag)
        self.assertEqual(battle.rnd, 2)
        self.assertEqual(battle.outcome, None)

    def test_first_march_can_be_won(self):
        save = new_game()
        save.prepare_episode(1)
        ep = episode(1)
        order = default_order(save, ep)
        battle = build_battle(save, 1, order, default_items(save, order), random.Random(1))
        outcome = play(battle)
        self.assertEqual(outcome, "win", "\n".join(battle.log[-25:]))

        save.finish_victory(1, battle)
        save.prepare_episode(2)
        ep = episode(2)
        order = default_order(save, ep)
        battle = build_battle(save, 2, order, default_items(save, order), random.Random(2))
        outcome = play(battle)
        self.assertEqual(outcome, "win", "\n".join(battle.log[-30:]))

        save.finish_victory(2, battle)
        save.prepare_episode(3)
        ep = episode(3)
        order = default_order(save, ep)
        self.assertIn("gun_chief", order)
        battle = build_battle(save, 3, order, default_items(save, order), random.Random(3))
        outcome = play(battle)
        self.assertEqual(outcome, "win", "\n".join(battle.log[-30:]))

    def test_gun_line_and_salvo(self):
        shooter = fighter(id="g", name="Gun", pos=(0, 0), weapon_family="gun", atk=7, defn=2, skills=["shot_2"], sp=16, max_sp=16)
        far = fighter(id="e", name="Far", side="enemy", pos=(0, 5), hp=40, max_hp=40, defn=0, atk=1)
        battle = make([shooter, far], w=8, h=8)
        self.assertEqual([u.id for u in battle.attack_targets(shooter, shooter.pos)], ["e"])
        ok, _reason = battle.action_legal(shooter, {"type": "issen"})
        self.assertFalse(ok)

        too_far = fighter(id="z", name="Farther", side="enemy", pos=(0, 6), hp=20, max_hp=20, defn=0)
        battle = make([shooter, too_far], w=8, h=8)
        self.assertEqual(battle.attack_targets(shooter, shooter.pos), [])

        diag = fighter(id="d", name="Diag", side="enemy", pos=(3, 3), hp=20, max_hp=20, defn=0)
        battle = make([shooter, diag], w=8, h=8)
        self.assertEqual([u.id for u in battle.attack_targets(shooter, shooter.pos)], ["d"])

        blocker = fighter(id="b", name="Block", side="enemy", pos=(0, 2), hp=20, max_hp=20, defn=0)
        blocked = make([shooter, blocker, far], w=8, h=8)
        reached = {u.id for u in blocked.attack_targets(shooter, shooter.pos)}
        self.assertEqual(reached, {"b"})

        gapped = make([shooter, far], w=8, h=8, heights={(0, 2): 2})
        self.assertEqual(gapped.attack_targets(shooter, shooter.pos), [])

        live = fighter(id="g", name="Gun", pos=(0, 0), weapon_family="gun", atk=7, skills=["shot_2"], sp=16, max_sp=16)
        foe = fighter(id="e", name="Far", side="enemy", pos=(0, 4), hp=30, max_hp=30, defn=0, atk=1)
        battle = make([live, foe], w=8, h=8)
        events, err = battle.player_act(live.gid, live.pos, {"type": "skill", "skill": "shot_2", "target": foe.gid})
        self.assertIsNone(err)
        self.assertEqual(live.sp, 2)
        hits = [event for event in events if event.get("t") == "hit" and not event.get("miss")]
        self.assertEqual(len(hits), 2)
        self.assertEqual(foe.hp, 16)


if __name__ == "__main__":
    unittest.main()
