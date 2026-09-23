"""Battle rules. No speed bar, no mid-fight bag, no timing minigame."""

from __future__ import annotations

import heapq
import random

from ashgauntlet.data import ISSEN_FAMILIES, LINE_FAMILIES, MELEE_FAMILIES, SKILLS

ORTHO = ((1, 0), (-1, 0), (0, 1), (0, -1))
EIGHT = ORTHO + ((1, 1), (1, -1), (-1, 1), (-1, -1))


def manhattan(a, b) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def ortho_dir(origin, tile):
    dx = tile[0] - origin[0]
    dy = tile[1] - origin[1]
    if dx == 0 and dy == 0:
        return None
    if dx != 0 and dy != 0:
        return None
    sx = 0 if dx == 0 else (1 if dx > 0 else -1)
    sy = 0 if dy == 0 else (1 if dy > 0 else -1)
    return (sx, sy)


def facing_toward(origin, tile):
    dx = tile[0] - origin[0]
    dy = tile[1] - origin[1]
    if dx == 0 and dy == 0:
        return (0, -1)
    if abs(dx) >= abs(dy):
        return (1 if dx > 0 else -1, 0)
    return (0, 1 if dy > 0 else -1)


class Unit:
    def __init__(self, **kw):
        self.id = ""
        self.name = ""
        self.side = "player"
        self.sprite = "pawn"
        self.gid = None
        self.pos = (0, 0)
        self.facing = (0, -1)
        self.hp = 1
        self.max_hp = 1
        self.sp = 0
        self.max_sp = 0
        self.atk = 1
        self.defn = 0
        self.mov = 4
        self.weapon_family = None
        self.weapon_atk = 0
        self.armor_def = 0
        self.acc_def = 0
        self.weapon_name = ""
        self.skills = []
        self.items = [None, None]
        self.alive = True
        self.acted = False
        self.issen = False
        self.mode = None
        self.mode_left = 0
        self.mode_fresh = False
        self.is_lord = False
        self.lose_flag = False
        self.stone = None
        self.recipe = None
        self.exp_value = 0
        for key, value in kw.items():
            setattr(self, key, value)


class Battle:
    def __init__(self, width, height, heights, blocked, units, reinforcements, rng=None):
        self.w = width
        self.h = height
        self.heights = dict(heights)
        self.blocked = set(blocked)
        self.units = list(units)
        self.reinforcements = list(reinforcements)
        self.rng = rng or random.Random()
        self.rnd = 1
        self.phase = "player"
        self.outcome = None
        self.loot_souls = 0
        self.loot_stones = []
        self.loot_recipes = []
        self.loot_exp = {}
        self.log = []
        self.spawned = set()
        self.enemy_queue = []
        self.enemy_index = 0
        self.theme = "village"
        self.title = ""
        self.episode_id = 0
        self._next_gid = 1
        for unit in self.units:
            unit.gid = None
            self._tag(unit)
        self._refresh_players()

    def _tag(self, unit: Unit) -> None:
        if unit.gid is None:
            unit.gid = self._next_gid
            self._next_gid += 1

    def in_bounds(self, pos) -> bool:
        return 0 <= pos[0] < self.w and 0 <= pos[1] < self.h

    def height(self, pos) -> int:
        return self.heights.get((pos[0], pos[1]), 0)

    def height_ok(self, a, b) -> bool:
        return abs(self.height(a) - self.height(b)) < 2

    def step_cost(self, a, b):
        gap = abs(self.height(a) - self.height(b))
        if gap >= 2:
            return None
        return 1 + gap

    def unit_by_gid(self, gid):
        for unit in self.units:
            if unit.gid == gid:
                return unit
        return None

    def unit_at(self, pos):
        spot = (pos[0], pos[1])
        for unit in self.units:
            if unit.alive and unit.pos == spot:
                return unit
        return None

    def is_free(self, pos) -> bool:
        return self.in_bounds(pos) and pos not in self.blocked and self.unit_at(pos) is None

    def is_adjacent(self, a, b) -> bool:
        return manhattan(a, b) == 1

    def living(self, side=None):
        units = [u for u in self.units if u.alive]
        if side is None:
            return units
        return [u for u in units if u.side == side]

    def unacted_players(self):
        return [u for u in self.units if u.alive and u.side == "player" and not u.acted]

    def _say(self, text: str) -> None:
        self.log.append(text)
        if len(self.log) > 48:
            del self.log[:16]

    def find_empty(self, pos):
        pos = (int(pos[0]), int(pos[1]))
        if self.is_free(pos):
            return pos
        limit = max(self.w, self.h)
        for rad in range(1, limit + 1):
            for y in range(pos[1] - rad, pos[1] + rad + 1):
                for x in range(pos[0] - rad, pos[0] + rad + 1):
                    if max(abs(x - pos[0]), abs(y - pos[1])) != rad:
                        continue
                    spot = (x, y)
                    if self.is_free(spot):
                        return spot
        return pos

    def _refresh_players(self):
        self.phase = "player"
        events = []
        for unit in self.units:
            if unit.alive and unit.side == "player":
                unit.acted = False
        events.extend(self._spawn())
        return events

    def _spawn(self):
        events = []
        for index, spec in enumerate(self.reinforcements):
            if spec["round"] != self.rnd or index in self.spawned:
                continue
            self.spawned.add(index)
            guest = spec["unit"]
            if any(u.alive and u.id == guest.id for u in self.units):
                continue
            guest.pos = self.find_empty(spec["pos"])
            guest.alive = True
            guest.acted = False
            self._tag(guest)
            self.units.append(guest)
            self._say(f"{guest.name} arrives.")
            if guest.lose_flag:
                self._say(f"If {guest.name} falls, the march is over.")
            events.append({"t": "spawn", "gid": guest.gid})
        return events

    def movement(self, unit: Unit):
        start = unit.pos
        occupied = {u.pos: u for u in self.units if u.alive}
        dist = {start: 0}
        prev = {}
        heap = [(0, start[0], start[1])]
        while heap:
            cost, x, y = heapq.heappop(heap)
            pos = (x, y)
            if cost != dist.get(pos):
                continue
            for dx, dy in ORTHO:
                nxt = (x + dx, y + dy)
                if not self.in_bounds(nxt) or nxt in self.blocked:
                    continue
                step = self.step_cost(pos, nxt)
                if step is None:
                    continue
                occ = occupied.get(nxt)
                if occ and occ.gid != unit.gid and occ.side != unit.side:
                    continue
                nd = cost + step
                if nd > unit.mov or nd >= dist.get(nxt, 9999):
                    continue
                dist[nxt] = nd
                prev[nxt] = pos
                heapq.heappush(heap, (nd, nxt[0], nxt[1]))
        stand = {}
        for pos, cost in dist.items():
            occ = occupied.get(pos)
            if occ is None or occ.gid == unit.gid:
                stand[pos] = cost
        return stand, prev

    def path_to(self, prev, start, dest):
        if dest == start:
            return [start]
        out = [dest]
        guard = 0
        while out[-1] != start and guard < 64:
            out.append(prev[out[-1]])
            guard += 1
        out.reverse()
        return out

    def attack_power(self, unit: Unit) -> int:
        value = unit.atk + unit.weapon_atk
        if unit.mode == "strongman":
            value += 8
        if unit.mode == "weakling":
            value -= 8
        return value

    def defense_power(self, unit: Unit) -> int:
        value = unit.defn + unit.armor_def + unit.acc_def
        if unit.mode == "defender":
            value += 8
        return value

    def preview_damage(self, attacker: Unit, defender: Unit) -> int:
        damage = max(1, self.attack_power(attacker) - self.defense_power(defender))
        if defender.mode == "target":
            damage += 4
        return damage

    def _add_enemy(self, unit, origin, pos, out):
        if not self.in_bounds(pos) or not self.height_ok(origin, pos):
            return
        occ = self.unit_at(pos)
        if occ and occ.side != unit.side and occ.gid not in {u.gid for u in out}:
            out.append(occ)

    def melee_targets(self, unit, pos):
        out = []
        for dx, dy in ORTHO:
            self._add_enemy(unit, pos, (pos[0] + dx, pos[1] + dy), out)
        return out

    def _spear_mid_ok(self, unit, pos, direction) -> bool:
        mid = (pos[0] + direction[0], pos[1] + direction[1])
        if not self.in_bounds(mid) or mid in self.blocked:
            return False
        if not self.height_ok(pos, mid):
            return False
        occ = self.unit_at(mid)
        if occ and occ.side != unit.side:
            return False
        return True

    def attack_targets(self, unit, pos):
        family = unit.weapon_family
        out = []
        if family in MELEE_FAMILIES:
            return self.melee_targets(unit, pos)
        if family == "spear":
            for direction in ORTHO:
                for dist in (1, 2):
                    spot = (pos[0] + direction[0] * dist, pos[1] + direction[1] * dist)
                    if dist == 2 and not self._spear_mid_ok(unit, pos, direction):
                        continue
                    self._add_enemy(unit, pos, spot, out)
            return out
        if family in LINE_FAMILIES:
            for foe in self.living("enemy" if unit.side == "player" else "player"):
                if self.clear_line(pos, foe.pos, 5):
                    out.append(foe)
        return out

    def clear_line(self, origin, target, reach) -> bool:
        dx = target[0] - origin[0]
        dy = target[1] - origin[1]
        if dx == 0 and dy == 0:
            return False
        adx, ady = abs(dx), abs(dy)
        if not (dx == 0 or dy == 0 or adx == ady):
            return False
        steps = max(adx, ady)
        if steps < 1 or steps > reach:
            return False
        sx = 0 if dx == 0 else dx // adx
        sy = 0 if dy == 0 else dy // ady
        for i in range(1, steps):
            spot = (origin[0] + sx * i, origin[1] + sy * i)
            if spot in self.blocked or self.unit_at(spot) or not self.height_ok(origin, spot):
                return False
        return self.height_ok(origin, target)

    def line_tiles(self, pos, direction, length):
        tiles = []
        h0 = self.height(pos)
        for i in range(1, length + 1):
            spot = (pos[0] + direction[0] * i, pos[1] + direction[1] * i)
            if not self.in_bounds(spot) or spot in self.blocked:
                break
            if abs(self.height(spot) - h0) >= 2:
                break
            tiles.append(spot)
        return tiles

    def line_targets(self, unit, pos, direction, length):
        found = []
        for spot in self.line_tiles(pos, direction, length):
            occ = self.unit_at(spot)
            if occ and occ.side != unit.side:
                found.append(occ)
        return found

    def bolt_targets(self, unit, pos, reach):
        foes = self.living("enemy" if unit.side == "player" else "player")
        return [foe for foe in foes if self.clear_line(pos, foe.pos, reach)]

    def skill_options(self, unit, pos, skill_id):
        skill = SKILLS[skill_id]
        tiles = set()
        gids = []
        ok = False
        if unit.sp < skill["sp"] or skill_id not in unit.skills:
            return {"tiles": tiles, "gids": gids, "ok": False}
        kind = skill["kind"]
        if kind == "line":
            for direction in ORTHO:
                hits = self.line_targets(unit, pos, direction, skill["length"])
                if not hits:
                    continue
                for spot in self.line_tiles(pos, direction, skill["length"]):
                    tiles.add(spot)
            ok = bool(tiles)
        elif kind == "nova":
            ok = any(self.line_targets(unit, pos, d, skill["length"]) for d in ORTHO)
        elif kind == "heal":
            for ally in self.living(unit.side):
                if ally.gid == unit.gid or ally.hp >= ally.max_hp:
                    continue
                if self.is_adjacent(pos, ally.pos) and self.height_ok(pos, ally.pos):
                    gids.append(ally.gid)
                    tiles.add(ally.pos)
            ok = bool(gids)
        elif kind == "heal_aura":
            ok = self._hurt_allies_near(unit, pos, skill["radius"])
        elif kind == "heal_all":
            ok = any(a.hp < a.max_hp for a in self.living(unit.side))
        elif kind == "mode":
            ok = True
        elif kind == "mode_target":
            targets = (
                self.melee_targets(unit, pos)
                if skill.get("aim") != "bolt"
                else self.bolt_targets(unit, pos, skill.get("length", 4))
            )
            for tgt in targets:
                gids.append(tgt.gid)
                tiles.add(tgt.pos)
            ok = bool(gids)
        elif kind == "multi":
            for tgt in self.melee_targets(unit, pos):
                gids.append(tgt.gid)
                tiles.add(tgt.pos)
            ok = bool(gids)
        elif kind == "bolt":
            for tgt in self.bolt_targets(unit, pos, skill["length"]):
                gids.append(tgt.gid)
                tiles.add(tgt.pos)
            ok = bool(gids)
        return {"tiles": tiles, "gids": gids, "ok": ok}

    def _hurt_allies_near(self, unit, pos, radius) -> bool:
        for ally in self.living(unit.side):
            if ally.hp >= ally.max_hp:
                continue
            if manhattan(pos, ally.pos) <= radius and self.height_ok(pos, ally.pos):
                return True
        return False

    def item_targets(self, unit, pos, slot):
        if slot < 0 or slot >= len(unit.items) or unit.items[slot] != "herb":
            return []
        gids = []
        if unit.hp < unit.max_hp:
            gids.append(unit.gid)
        for ally in self.living(unit.side):
            if ally.gid == unit.gid or ally.hp >= ally.max_hp:
                continue
            if self.is_adjacent(pos, ally.pos) and self.height_ok(pos, ally.pos):
                gids.append(ally.gid)
        return gids

    def action_legal(self, unit, action):
        kind = action.get("type")
        if kind == "wait":
            return True, ""
        if kind == "issen":
            if unit.weapon_family not in ISSEN_FAMILIES:
                return False, "This weapon cannot set Issen."
            return True, ""
        if kind == "attack":
            if not unit.weapon_family:
                return False, "They have nothing to strike with."
            target = self.unit_by_gid(action.get("target"))
            legal = {u.gid for u in self.attack_targets(unit, unit.pos)}
            if target is None or target.gid not in legal:
                return False, "You cannot reach that enemy."
            return True, ""
        if kind == "skill":
            skill_id = action.get("skill")
            if skill_id not in unit.skills or skill_id not in SKILLS:
                return False, "They do not know that."
            skill = SKILLS[skill_id]
            if unit.sp < skill["sp"]:
                return False, "Not enough spirit."
            opts = self.skill_options(unit, unit.pos, skill_id)
            if skill["kind"] == "line":
                direction = tuple(action.get("dir", ()))
                if direction not in ORTHO or not self.line_targets(unit, unit.pos, direction, skill["length"]):
                    return False, "Nobody is standing on that line."
                return True, ""
            if skill["kind"] in ("heal", "multi", "bolt", "mode_target"):
                if action.get("target") not in opts["gids"]:
                    return False, "Choose a valid target."
                return True, ""
            if not opts["ok"]:
                return False, "That will not do anything."
            return True, ""
        if kind == "item":
            target = self.unit_by_gid(action.get("target"))
            opts = self.item_targets(unit, unit.pos, action.get("slot", -1))
            if target is None or target.gid not in opts:
                return False, "The herb cannot reach them."
            return True, ""
        return False, "That is not an action."

    def begin_turn(self, unit: Unit) -> None:
        if unit.issen:
            unit.issen = False
            self._say(f"{unit.name}'s Issen fades.")

    def finish_turn(self, unit: Unit) -> None:
        if not unit.mode:
            return
        if unit.mode_fresh:
            unit.mode_fresh = False
            return
        unit.mode_left -= 1
        if unit.mode_left <= 0:
            unit.mode = None
            unit.mode_left = 0

    def apply_mode(self, who: Unit, mode: str, self_cast: bool) -> None:
        who.mode = mode
        who.mode_left = 2
        who.mode_fresh = self_cast

    def player_act(self, gid, dest, action):
        if self.outcome:
            return [], "The fight is already over."
        if self.phase != "player":
            return [], "The enemy is moving."
        unit = self.unit_by_gid(gid)
        if unit is None or not unit.alive or unit.side != "player":
            return [], "Pick one of your fighters."
        if unit.acted:
            return [], "They already acted."
        return self.apply_act(unit, dest, action)

    def apply_act(self, unit: Unit, dest, action):
        dest = (int(dest[0]), int(dest[1]))
        stand, prev = self.movement(unit)
        if dest not in stand:
            return [], "That tile is out of reach."
        path = self.path_to(prev, unit.pos, dest)
        saved = unit.pos
        unit.pos = dest
        ok, reason = self.action_legal(unit, action)
        if not ok:
            unit.pos = saved
            return [], reason
        self.begin_turn(unit)
        unit.pos = dest
        if len(path) >= 2:
            unit.facing = (path[-1][0] - path[-2][0], path[-1][1] - path[-2][1])
        events = []
        if path != [saved]:
            events.append({"t": "move", "gid": unit.gid, "path": path})
        events.extend(self.resolve(unit, action))
        self.finish_turn(unit)
        unit.acted = True
        if self.outcome:
            events.append({"t": "over", "outcome": self.outcome})
        return events, None

    def resolve(self, unit, action):
        kind = action["type"]
        if kind == "wait":
            self._say(f"{unit.name} waits.")
            return [{"t": "wait", "gid": unit.gid}]
        if kind == "issen":
            unit.issen = True
            self._say(f"{unit.name} sets Issen.")
            return [{"t": "issen", "gid": unit.gid}]
        if kind == "attack":
            target = self.unit_by_gid(action["target"])
            unit.facing = facing_toward(unit.pos, target.pos)
            return self.resolve_attack(unit, target)
        if kind == "skill":
            return self.resolve_skill(unit, action)
        if kind == "item":
            return self.resolve_item(unit, action)
        return []

    def roll_hit(self, attacker, defender, ranged: bool) -> bool:
        chance = 90 if ranged else 100
        if defender.mode == "dodge":
            chance -= 15
        if defender.mode == "blind" and ranged:
            chance -= 30
        return self.rng.randrange(100) < max(0, chance)

    def resolve_attack(self, attacker, defender):
        melee = self.is_adjacent(attacker.pos, defender.pos) and attacker.weapon_family in ISSEN_FAMILIES
        if defender.issen and melee:
            defender.issen = False
            if attacker.is_lord:
                self._say(f"{attacker.name} breaks the Issen and still strikes.")
                return self.apply_damage(attacker, defender)
            self._say(f"{defender.name} answers with Issen. {attacker.name} falls.")
            events = [{
                "t": "hit",
                "gid": defender.gid,
                "src": attacker.gid,
                "amount": 0,
                "hp": defender.hp,
                "miss": True,
            }]
            events.extend(self.kill(attacker, defender, issen=True))
            return events
        ranged = attacker.weapon_family in LINE_FAMILIES
        if not self.roll_hit(attacker, defender, ranged):
            self._say(f"{attacker.name} misses {defender.name}.")
            return [{
                "t": "hit",
                "gid": defender.gid,
                "src": attacker.gid,
                "amount": 0,
                "hp": defender.hp,
                "miss": True,
            }]
        return self.apply_damage(attacker, defender)

    def apply_damage(self, attacker, defender, amount=None):
        if defender is None or not defender.alive:
            return []
        if amount is None:
            amount = self.preview_damage(attacker, defender)
        defender.hp -= amount
        events = [{
            "t": "hit",
            "gid": defender.gid,
            "src": attacker.gid if attacker else None,
            "amount": amount,
            "hp": defender.hp,
            "miss": False,
        }]
        name = attacker.name if attacker else "Something"
        self._say(f"{name} hits {defender.name} for {amount}.")
        if defender.hp <= 0:
            events.extend(self.kill(defender, attacker, issen=False))
        return events

    def heal(self, target, amount):
        before = target.hp
        target.hp = min(target.max_hp, target.hp + amount)
        gained = target.hp - before
        self._say(f"{target.name} recovers {gained}.")
        return {"t": "heal", "gid": target.gid, "amount": gained, "hp": target.hp}

    def kill(self, victim, killer, issen=False):
        victim.hp = 0
        victim.alive = False
        events = [{"t": "die", "gid": victim.gid}]
        if killer and killer.side == "player" and victim.side == "enemy":
            if victim.is_lord:
                souls = 100
            elif issen:
                souls = 40
            else:
                souls = 10
            self.loot_souls += souls
            if victim.stone:
                self.loot_stones.append(victim.stone)
            if victim.recipe and victim.recipe not in self.loot_recipes:
                self.loot_recipes.append(victim.recipe)
            self.loot_exp[killer.id] = self.loot_exp.get(killer.id, 0) + victim.exp_value
            self._say(f"{victim.name} falls. Souls +{souls}.")
        else:
            self._say(f"{victim.name} falls.")
        if victim.id == "kairo" or (victim.lose_flag and victim.side == "player"):
            self.outcome = "lose"
            self._say("The march is over.")
        elif victim.side == "enemy" and not self.living("enemy"):
            self.outcome = "win"
            self._say("The field is clear.")
        return events

    def resolve_skill(self, unit, action):
        skill = SKILLS[action["skill"]]
        unit.sp -= skill["sp"]
        kind = skill["kind"]
        self._say(f"{unit.name} uses {skill['name']}.")
        if kind == "mode":
            self.apply_mode(unit, skill["mode"], True)
            return [{"t": "mode", "gid": unit.gid, "mode": skill["mode"]}]
        if kind == "mode_target":
            target = self.unit_by_gid(action["target"])
            self.apply_mode(target, skill["mode"], False)
            unit.facing = facing_toward(unit.pos, target.pos)
            return [{"t": "mode", "gid": target.gid, "mode": skill["mode"]}]
        if kind == "line":
            direction = tuple(action["dir"])
            unit.facing = direction
            return self._hit_many(unit, self.line_targets(unit, unit.pos, direction, skill["length"]))
        if kind == "nova":
            seen = []
            for direction in ORTHO:
                for tgt in self.line_targets(unit, unit.pos, direction, skill["length"]):
                    if tgt.gid not in seen:
                        seen.append(tgt.gid)
            return self._hit_many(unit, [self.unit_by_gid(gid) for gid in seen])
        if kind == "multi":
            target = self.unit_by_gid(action["target"])
            unit.facing = facing_toward(unit.pos, target.pos)
            events = []
            for _ in range(skill["hits"]):
                if not target.alive or self.outcome == "lose":
                    break
                events.extend(self.apply_damage(unit, target))
            return events
        if kind == "bolt":
            target = self.unit_by_gid(action["target"])
            unit.facing = facing_toward(unit.pos, target.pos)
            return self.apply_damage(unit, target)
        if kind == "heal":
            target = self.unit_by_gid(action["target"])
            amount = max(1, int(unit.max_hp * skill["ratio"]))
            return [self.heal(target, amount)]
        if kind == "heal_aura":
            return self._heal_near(unit, skill["ratio"], skill["radius"])
        if kind == "heal_all":
            return self._heal_near(unit, skill["ratio"], 99)
        return []

    def _hit_many(self, unit, targets):
        events = []
        for target in targets:
            if target is None or not target.alive:
                continue
            events.extend(self.apply_damage(unit, target))
            if self.outcome:
                break
        return events

    def _heal_near(self, unit, ratio, radius):
        amount = max(1, int(unit.max_hp * ratio))
        events = []
        for ally in self.living(unit.side):
            if ally.hp >= ally.max_hp:
                continue
            if manhattan(unit.pos, ally.pos) <= radius and self.height_ok(unit.pos, ally.pos):
                events.append(self.heal(ally, amount))
        return events

    def resolve_item(self, unit, action):
        slot = action["slot"]
        unit.items[slot] = None
        target = self.unit_by_gid(action["target"])
        self._say(f"{unit.name} uses a herb.")
        return [self.heal(target, 15)]

    def end_player_phase(self):
        events = []
        if self.outcome:
            return events
        for unit in list(self.unacted_players()):
            if self.outcome:
                break
            ev, _err = self.apply_act(unit, unit.pos, {"type": "wait"})
            events.extend(ev)
        if self.outcome:
            return events
        foes = [u for u in self.living("enemy")]
        foes.sort(key=lambda u: (u.pos[1], u.pos[0]))
        self.enemy_queue = [u.gid for u in foes]
        self.enemy_index = 0
        self.phase = "enemy"
        if not self.enemy_queue:
            self.outcome = "win"
            self._say("The field is clear.")
            events.append({"t": "over", "outcome": "win"})
            return events
        events.append({"t": "phase", "phase": "enemy", "round": self.rnd})
        return events

    def enemy_step(self):
        if self.outcome or self.phase != "enemy":
            return []
        while self.enemy_index < len(self.enemy_queue):
            gid = self.enemy_queue[self.enemy_index]
            self.enemy_index += 1
            unit = self.unit_by_gid(gid)
            if unit and unit.alive and unit.side == "enemy":
                return self.enemy_act(unit)
        self.rnd += 1
        events = self._refresh_players()
        events.append({"t": "phase", "phase": "player", "round": self.rnd})
        return events

    def enemy_act(self, unit: Unit):
        dest, action = self.choose_enemy_action(unit)
        events, err = self.apply_act(unit, dest, action)
        if err:
            events, _err = self.apply_act(unit, unit.pos, {"type": "wait"})
        return events

    def _target_key(self, attacker, target):
        flag = 1 if (target.lose_flag or target.id == "kairo") else 0
        return (flag, -target.hp, self.preview_damage(attacker, target))

    def choose_enemy_action(self, unit: Unit):
        stand, _prev = self.movement(unit)
        best_attack = None
        for dest in stand:
            for target in self.attack_targets(unit, dest):
                key = self._target_key(unit, target)
                if best_attack is None or key > best_attack[0]:
                    best_attack = (key, dest, target)
        best_line = None
        if "line_3" in unit.skills and unit.sp >= SKILLS["line_3"]["sp"]:
            for dest in stand:
                for direction in ORTHO:
                    hits = self.line_targets(unit, dest, direction, 3)
                    if not hits:
                        continue
                    key = max(self._target_key(unit, hit) for hit in hits)
                    pack = (len(hits), key, dest, direction)
                    if best_line is None or (pack[0], pack[1]) > (best_line[0], best_line[1]):
                        best_line = pack
        if best_line and best_line[0] >= 2:
            _count, _key, dest, direction = best_line
            return dest, {"type": "skill", "skill": "line_3", "dir": direction}
        if best_attack:
            _key, dest, target = best_attack
            return dest, {"type": "attack", "target": target.gid}
        if best_line:
            _count, _key, dest, direction = best_line
            return dest, {"type": "skill", "skill": "line_3", "dir": direction}
        foes = self.living("player")
        if not foes or not stand:
            return unit.pos, {"type": "wait"}
        goal = min(foes, key=lambda foe: manhattan(foe.pos, unit.pos))
        dest = min(stand, key=lambda tile: (manhattan(tile, goal.pos), stand[tile]))
        return dest, {"type": "wait"}
