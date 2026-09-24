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
        from ashgauntlet.data import EPISODES, grid_from_rows

        for ep in EPISODES:
            if not ep.get("battle", True):
                self.assertEqual(ep["enemies"], [])
                continue
            _heights, width, height = grid_from_rows(ep["heights"])
            blocked = set(map(tuple, ep["blocked"]))
            spots = [tuple(p) for p in ep["slots"]]
            spots += [tuple(e["pos"]) for e in ep["enemies"]]
            spots += [tuple(r["pos"]) for r in ep["reinforcements"]]
            spots += [tuple(g["pos"]) for g in ep.get("guests", [])]
            self.assertEqual(len(spots), len(set(spots)), ep["name"])
            self.assertGreaterEqual(len(ep["slots"]), 1, ep["name"])
            self.assertLessEqual(len(ep["intro"]), 8, ep["name"])
            self.assertLessEqual(len(ep["outro"]), 4, ep["name"])
            if ep.get("win") == "lord":
                self.assertTrue(any(enemy.get("hunt") for enemy in ep["enemies"]), ep["name"])
            for spot in spots:
                self.assertTrue(0 <= spot[0] < width and 0 <= spot[1] < height, (ep["name"], spot))
                self.assertNotIn(spot, blocked, (ep["name"], spot))

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

    def test_level_label_and_later_rules(self):
        from ashgauntlet.data import level_label

        self.assertEqual(level_label(1, "Kureha Burns", "Cleared"), "Level 1 - Kureha Burns - Cleared")

        hero = fighter(pos=(0, 0), atk=30)
        mark = fighter(id="boss", name="Boss", side="enemy", pos=(1, 0), hp=10, defn=0, hunt=True)
        extra = fighter(id="pawn", name="Pawn", side="enemy", pos=(4, 4), hp=40, defn=0, mov=0)
        battle = make([hero, mark, extra], w=8, h=8)
        battle.win_mode = "lord"
        _events, err = battle.player_act(hero.gid, hero.pos, {"type": "attack", "target": mark.gid})
        self.assertIsNone(err)
        self.assertTrue(battle.hunt_down)
        self.assertIsNone(battle.outcome)
        battle.end_player_phase()
        run_enemies(battle)
        self.assertEqual(battle.outcome, "win")

        warden = fighter(id="warden", name="Warden", side="enemy", pos=(1, 0), hp=20, atk=8, defn=0)
        sleeper = fighter(pos=(0, 0), issen=True, hp=20, max_hp=20, defn=0)
        battle = make([sleeper, warden])
        battle.phase = "enemy"
        battle.apply_act(warden, warden.pos, {"type": "attack", "target": sleeper.gid})
        self.assertFalse(warden.alive)
        self.assertEqual(sleeper.hp, 20)

        high = fighter(id="e", name="E", side="enemy", pos=(1, 0), atk=6, defn=0, hp=30)
        low = fighter(pos=(0, 0), atk=6, defn=0, hp=30)
        battle = make([low, high], heights={(1, 0): 1})
        battle.enemy_high_ground = True
        self.assertEqual(battle.preview_damage(high, low), 12)
        battle.stance = "fang"
        self.assertEqual(battle.preview_damage(low, high), 6)
        battle.stance = "bird"
        self.assertEqual(battle.attack_power(low), 9)
        battle.stance = "shell"
        self.assertEqual(battle.preview_damage(high, low), 6)
        battle.stance = "coil"
        low.weapon_family = "spear"
        high.defn = 6
        self.assertEqual(battle.defense_power(high, low), 2)

        left = fighter(id="fang_a", name="A", side="enemy", pos=(3, 1), hp=10, max_hp=10, twin="fang_b", atk=1)
        right = fighter(id="fang_b", name="B", side="enemy", pos=(2, 2), hp=10, max_hp=10, twin="fang_a", atk=1)
        hitter = fighter(pos=(1, 2), atk=40, hp=40, max_hp=40, defn=4)
        battle = make([hitter, left, right])
        battle.player_act(hitter.gid, hitter.pos, {"type": "attack", "target": right.gid})
        self.assertFalse(right.alive)
        battle.end_player_phase()
        run_enemies(battle)
        self.assertTrue(right.alive)
        self.assertEqual(right.hp, 5)

        both_a = fighter(id="fang_a", name="A", side="enemy", pos=(1, 0), hp=5, max_hp=10, twin="fang_b")
        both_b = fighter(id="fang_b", name="B", side="enemy", pos=(2, 1), hp=5, max_hp=10, twin="fang_a")
        cleaner = fighter(pos=(1, 1), atk=40, mov=5)
        battle = make([cleaner, both_a, both_b])
        battle.player_act(cleaner.gid, cleaner.pos, {"type": "attack", "target": both_a.gid})
        battle.units[0].acted = False
        battle.player_act(cleaner.gid, (1, 1), {"type": "attack", "target": both_b.gid})
        self.assertEqual(battle.outcome, "win")
        self.assertFalse(both_a.alive)
        self.assertFalse(both_b.alive)

        asleep = fighter(id="e", name="E", side="enemy", pos=(2, 0), hp=20, status="sleep", status_left=2, mov=4)
        watcher = fighter(pos=(0, 0), atk=8)
        battle = make([watcher, asleep])
        battle.phase = "enemy"
        battle.enemy_act(asleep)
        self.assertEqual(asleep.pos, (2, 0))
        self.assertEqual(asleep.status_left, 1)
        asleep.acted = False
        battle.phase = "player"
        battle.player_act(watcher.gid, watcher.pos, {"type": "wait"})
        watcher.acted = False
        battle.player_act(watcher.gid, (1, 0), {"type": "attack", "target": asleep.gid})
        self.assertIsNone(asleep.status)

        thief = fighter(pos=(0, 0), skills=["steal"], sp=8, max_sp=8)
        rich = fighter(id="e", name="E", side="enemy", pos=(1, 0), hp=20, stone="cinder", recipe="nest_gun")
        battle = make([thief, rich])
        _events, err = battle.player_act(thief.gid, thief.pos, {"type": "skill", "skill": "steal", "target": rich.gid})
        self.assertIsNone(err)
        self.assertTrue(battle.loot_stones == ["cinder"] or battle.loot_recipes == ["nest_gun"])
        self.assertTrue(rich.stone is None or rich.recipe is None)

        nest = fighter(id="nest", name="Nest", side="enemy", pos=(3, 3), mov=0, weapon_family="gun")
        battle = make([nest], w=8, h=8)
        stand, _prev = battle.movement(nest)
        self.assertEqual(set(stand), {(3, 3)})

        kairo = fighter(id="kairo", name="Kairo", pos=(0, 4), sp=20, max_sp=20, skills=["oni_wake"], hp=40, max_hp=40, defn=4)
        dummy = fighter(id="e", name="E", side="enemy", pos=(0, 0), hp=80, atk=1, defn=0, mov=0)
        battle = make([kairo, dummy], w=8, h=8)
        battle.oni_allowed = True
        _events, err = battle.player_act(kairo.gid, kairo.pos, {"type": "skill", "skill": "oni_wake"})
        self.assertIsNone(err)
        self.assertEqual(kairo.sp, 10)
        self.assertTrue(kairo.oni)
        self.assertEqual(kairo.oni_left, 3)
        for _ in range(3):
            if battle.phase == "player":
                battle.oni_act(kairo)
            battle.end_player_phase()
            run_enemies(battle)
        self.assertFalse(kairo.oni)
        self.assertTrue(kairo.oni_move_only)
        ok, _reason = battle.action_legal(kairo, {"type": "attack", "target": dummy.gid})
        self.assertFalse(ok)

        chanter = fighter(
            id="lord",
            name="Lord",
            side="enemy",
            pos=(2, 0),
            hp=20,
            max_hp=40,
            atk=4,
            defn=0,
            skills=["chant"],
            chant_style="once",
            is_lord=True,
            issen_immune=True,
        )
        crowd = [
            fighter(id="a", name="A", pos=(2, 1), hp=30, max_hp=30, atk=8),
            fighter(id="b", name="B", pos=(3, 1), hp=20, max_hp=20),
        ]
        battle = make([chanter, *crowd], w=6, h=6)
        battle.phase = "enemy"
        battle.enemy_act(chanter)
        self.assertIsNotNone(chanter.chant)
        battle.phase = "player"
        crowd[0].acted = False
        _events, err = battle.player_act(crowd[0].gid, crowd[0].pos, {"type": "attack", "target": chanter.gid})
        self.assertIsNone(err)
        self.assertIsNone(chanter.chant)

    def test_every_story_fight_can_be_won(self):
        from ashgauntlet.data import BODIES, EPISODES

        save = new_game()
        for body_id in BODIES:
            if body_id != "soot_child":
                save.recruit(body_id)
        for body_id in save.roster:
            save.units[body_id]["level"] = 18
        save.oni_wake = True
        for ep in EPISODES:
            if not ep.get("battle", True):
                continue
            save.prepare_episode(ep["id"])
            order = default_order(save, ep)
            battle = build_battle(save, ep["id"], order, {}, random.Random(ep["id"] + 3))
            for unit in battle.units:
                if unit.id == "daughter":
                    unit.hp = unit.max_hp = 500
            outcome = play(battle, limit=600)
            self.assertEqual(outcome, "win", ep["name"] + "\n" + "\n".join(battle.log[-25:]))


if __name__ == "__main__":
    unittest.main()
