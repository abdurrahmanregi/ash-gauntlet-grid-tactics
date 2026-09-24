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
        self.issen_immune = False
        self.hunt = False
        self.twin = None
        self.revived_round = -1
        self.status = None
        self.status_left = 0
        self.status_from = None
        self.oni = False
        self.oni_left = 0
        self.oni_used = False
        self.oni_move_only = False
        self.chant = None
        self.chant_style = None
        self.chanted = False
        self.looted = False
        self.shell_hit = False
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
        self.depth_floor = 0
        self.win_mode = "rout"
        self.hunt_down = False
        self.stance = None
        self.enemy_high_ground = False
        self.oni_allowed = False
        self.aura_left = 0
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
        if self.win_mode == "lord" and self.hunt_down and self.outcome is None:
            self.outcome = "win"
            self._say("The marked enemy has fallen. The fight is over.")
            return events
        for unit in self.units:
            unit.shell_hit = False
            if unit.alive and unit.side == "player":
                unit.acted = False
        if self.aura_left > 0:
            self.aura_left -= 1
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
        if unit.side == "player" and self.stance == "bird":
            value += 3
        if unit.side == "player" and self.aura_left > 0:
            value += 5
        return value

    def defense_power(self, unit: Unit, attacker: Unit | None = None) -> int:
        value = unit.defn + unit.armor_def + unit.acc_def
        if unit.mode == "defender":
            value += 8
        if unit.side == "player" and self.aura_left > 0:
            value += 5
        if (
            attacker is not None
            and attacker.side == "player"
            and self.stance == "coil"
            and attacker.weapon_family in ("spear", "gun")
        ):
            value = max(0, value - 4)
        return value

    def _high_ground(self, attacker: Unit, defender: Unit) -> bool:
        if self.height(attacker.pos) <= self.height(defender.pos):
            return False
        if attacker.side == "player" and self.stance == "fang":
            return True
        if attacker.side == "enemy" and self.enemy_high_ground:
            return True
        return False

    def preview_damage(self, attacker: Unit, defender: Unit, first: bool = True) -> int:
        damage = max(1, self.attack_power(attacker) - self.defense_power(defender, attacker))
        if defender.mode == "target":
            damage += 4
        if first and self._high_ground(attacker, defender):
            damage += 6
        if self.stance == "shell" and not defender.shell_hit:
            damage = max(1, damage // 2)
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

    def skill_cost(self, unit, skill_id) -> int:
        skill = SKILLS[skill_id]
        if skill["kind"] == "oni":
            return unit.max_sp // 2
        return int(skill["sp"])

    def skill_options(self, unit, pos, skill_id):
        skill = SKILLS[skill_id]
        tiles = set()
        gids = []
        ok = False
        if skill_id not in unit.skills or unit.sp < self.skill_cost(unit, skill_id):
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
                if ally.hp >= ally.max_hp:
                    continue
                own = ally.gid == unit.gid
                if own or (self.is_adjacent(pos, ally.pos) and self.height_ok(pos, ally.pos)):
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
        elif kind == "salvo":
            for tgt in self.bolt_targets(unit, pos, skill.get("length", 5)):
                gids.append(tgt.gid)
                tiles.add(tgt.pos)
            ok = bool(gids)
        elif kind == "bolt":
            for tgt in self.bolt_targets(unit, pos, skill["length"]):
                gids.append(tgt.gid)
                tiles.add(tgt.pos)
            ok = bool(gids)
        elif kind == "cross":
            for direction in ORTHO:
                back = (-direction[0], -direction[1])
                if not (
                    self.line_targets(unit, pos, direction, skill["length"])
                    or self.line_targets(unit, pos, back, skill["length"])
                ):
                    continue
                for spot in self.line_tiles(pos, direction, skill["length"]):
                    tiles.add(spot)
                for spot in self.line_tiles(pos, back, skill["length"]):
                    tiles.add(spot)
            ok = bool(tiles)
        elif kind == "status":
            targets = (
                self.bolt_targets(unit, pos, skill.get("length", 5))
                if skill.get("aim") == "bolt"
                else self.melee_targets(unit, pos)
            )
            for tgt in targets:
                gids.append(tgt.gid)
                tiles.add(tgt.pos)
            ok = bool(gids)
        elif kind == "steal":
            for tgt in self.melee_targets(unit, pos):
                if tgt.is_lord:
                    continue
                if tgt.stone or (tgt.recipe and tgt.recipe not in self.loot_recipes):
                    gids.append(tgt.gid)
                    tiles.add(tgt.pos)
            ok = bool(gids)
        elif kind == "aura":
            ok = bool(self.living(unit.side))
        elif kind == "oni":
            ok = self.oni_allowed and unit.id == "kairo" and not unit.oni_used and not unit.oni
        elif kind == "chant":
            ok = False
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
        if unit.oni_move_only and kind != "wait":
            return False, "Oni-Wake has ended. This turn they can only move."
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
            if unit.sp < self.skill_cost(unit, skill_id):
                return False, "Not enough spirit."
            opts = self.skill_options(unit, unit.pos, skill_id)
            if skill["kind"] in ("line", "cross"):
                direction = tuple(action.get("dir", ()))
                if direction not in ORTHO:
                    return False, "Nobody is standing on that line."
                back = (-direction[0], -direction[1])
                forward = self.line_targets(unit, unit.pos, direction, skill["length"])
                if skill["kind"] == "line" and not forward:
                    return False, "Nobody is standing on that line."
                if skill["kind"] == "cross" and not forward and not self.line_targets(
                    unit, unit.pos, back, skill["length"]
                ):
                    return False, "Nobody is standing on that line."
                return True, ""
            if skill["kind"] in ("heal", "multi", "bolt", "mode_target", "salvo", "status", "steal"):
                if action.get("target") not in opts["gids"]:
                    return False, "Choose a valid target."
                return True, ""
            if skill["kind"] == "chant":
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

    def begin_turn(self, unit: Unit):
        events = []
        if unit.issen:
            unit.issen = False
            self._say(f"{unit.name}'s Issen fades.")
        if unit.status == "poison" and unit.alive:
            source = self.unit_by_gid(unit.status_from) if unit.status_from else None
            events.extend(self.apply_damage(source, unit, amount=3))
            unit.status_left -= 1
            if unit.status_left <= 0 or not unit.alive:
                unit.status = None
                unit.status_from = None
        if unit.alive and unit.status in ("sleep", "confuse", "para"):
            word = {"sleep": "asleep", "confuse": "confused", "para": "paralyzed"}[unit.status]
            self._say(f"{unit.name} is {word} and does nothing.")
            unit.status_left -= 1
            if unit.status_left <= 0:
                unit.status = None
                unit.status_from = None
        return events

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

    def apply_act(self, unit: Unit, dest, action, auto=False):
        dest = (int(dest[0]), int(dest[1]))
        if unit.oni and not unit.oni_move_only and not auto:
            return [], "Oni-Wake is moving on its own."
        frozen = unit.status in ("sleep", "confuse", "para")
        if frozen and dest != unit.pos:
            return [], "They cannot move."
        if frozen and action.get("type") != "wait":
            return [], "They are unable to act."
        if unit.oni_move_only and action.get("type") != "wait":
            return [], "Oni-Wake has ended. This turn they can only move."
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
        opening = self.begin_turn(unit)
        unit.pos = dest
        if len(path) >= 2:
            unit.facing = (path[-1][0] - path[-2][0], path[-1][1] - path[-2][1])
        events = list(opening)
        if path != [saved]:
            events.append({"t": "move", "gid": unit.gid, "path": path})
        if unit.alive and self.outcome is None:
            events.extend(self.resolve(unit, action))
        self.finish_turn(unit)
        if unit.oni_move_only:
            unit.oni_move_only = False
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
            if attacker.is_lord or attacker.issen_immune:
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

    def apply_damage(self, attacker, defender, amount=None, first=True, flat=0):
        if defender is None or not defender.alive:
            return []
        if amount is None:
            amount = self.preview_damage(attacker, defender, first=first) + flat
            if self.stance == "shell" and not defender.shell_hit and amount > 0:
                defender.shell_hit = True
        if amount > 0 and defender.status == "sleep":
            defender.status = None
            defender.status_left = 0
            defender.status_from = None
        if amount > 0 and defender.chant:
            defender.chant = None
            self._say(f"{defender.name}'s chant breaks.")
        defender.hp -= amount
        events = [{
            "t": "hit",
            "gid": defender.gid,
            "src": attacker.gid if attacker else None,
            "amount": amount,
            "hp": defender.hp,
            "miss": False,
        }]
        name = attacker.name if attacker else "Poison"
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
        victim.chant = None
        events = [{"t": "die", "gid": victim.gid}]
        if killer and killer.side == "player" and victim.side == "enemy" and not victim.looted:
            victim.looted = True
            if victim.is_lord:
                souls = 100
                self.loot_stones.extend(["void", "void"])
            else:
                souls = 40 if issen else 10
                if victim.stone:
                    self.loot_stones.append(victim.stone)
            if victim.recipe and victim.recipe not in self.loot_recipes:
                self.loot_recipes.append(victim.recipe)
            self.loot_exp[killer.id] = self.loot_exp.get(killer.id, 0) + victim.exp_value
            self.loot_souls += souls
            self._say(f"{victim.name} falls. Souls +{souls}.")
        else:
            self._say(f"{victim.name} falls.")
        if victim.hunt:
            self.hunt_down = True
        if victim.id == "kairo" or (victim.lose_flag and victim.side == "player"):
            self.outcome = "lose"
            self._say("The march is over.")
        elif victim.side == "enemy" and not self.living("enemy"):
            self.outcome = "win"
            self._say("The field is clear.")
        return events

    def resolve_skill(self, unit, action):
        skill = SKILLS[action["skill"]]
        unit.sp -= self.skill_cost(unit, action["skill"])
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
        if kind in ("multi", "salvo"):
            target = self.unit_by_gid(action["target"])
            unit.facing = facing_toward(unit.pos, target.pos)
            events = []
            for index in range(skill["hits"]):
                if not target.alive or self.outcome == "lose":
                    break
                events.extend(
                    self.apply_damage(unit, target, first=(index == 0), flat=skill.get("flat", 0))
                )
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
        if kind == "cross":
            direction = tuple(action["dir"])
            back = (-direction[0], -direction[1])
            unit.facing = direction
            seen = []
            hits = self.line_targets(unit, unit.pos, direction, skill["length"])
            hits += self.line_targets(unit, unit.pos, back, skill["length"])
            for tgt in hits:
                if tgt.gid not in seen:
                    seen.append(tgt.gid)
            return self._hit_many(unit, [self.unit_by_gid(gid) for gid in seen])
        if kind == "status":
            target = self.unit_by_gid(action["target"])
            target.status = skill["status"]
            target.status_left = 2
            target.status_from = unit.gid
            unit.facing = facing_toward(unit.pos, target.pos)
            self._say(f"{target.name} is struck by {skill['name']}.")
            return [{"t": "mode", "gid": target.gid, "mode": skill["status"]}]
        if kind == "steal":
            return self._steal(unit, self.unit_by_gid(action["target"]))
        if kind == "aura":
            self.aura_left = 2
            self._say("Aura covers the allies.")
            return [{"t": "mode", "gid": unit.gid, "mode": "aura"}]
        if kind == "oni":
            unit.oni = True
            unit.oni_left = 3
            unit.oni_used = True
            self._say(f"{unit.name} wakes the gauntlet.")
            return [{"t": "oni", "gid": unit.gid}]
        if kind == "chant":
            center = tuple(action.get("center", unit.pos))
            radius = int(action.get("radius", 2))
            unit.chant = (int(center[0]), int(center[1]), radius)
            if unit.chant_style == "once":
                unit.chanted = True
            self._say(f"{unit.name} begins to chant.")
            return [{"t": "chant", "gid": unit.gid}]
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
        events = self._tick_oni()
        self.rnd += 1
        events.extend(self._refresh_players())
        if self.outcome:
            events.append({"t": "over", "outcome": self.outcome})
            return events
        events.append({"t": "phase", "phase": "player", "round": self.rnd})
        return events

    def enemy_act(self, unit: Unit):
        revived = self._twin_revive(unit)
        if unit.chant:
            events = revived + self.begin_turn(unit)
            if unit.alive and self.outcome is None:
                events.extend(self._release_chant(unit))
            self.finish_turn(unit)
            unit.acted = True
            if self.outcome:
                events.append({"t": "over", "outcome": self.outcome})
            return events
        plan = self._chant_plan(unit)
        if plan is not None:
            dest, action = plan
        elif unit.status in ("sleep", "confuse", "para"):
            dest, action = unit.pos, {"type": "wait"}
        else:
            dest, action = self.choose_enemy_action(unit)
        events, err = self.apply_act(unit, dest, action)
        if err:
            events, _err = self.apply_act(unit, unit.pos, {"type": "wait"})
        return revived + events

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
        if best_attack and "two_hit" in unit.skills and unit.sp >= SKILLS["two_hit"]["sp"]:
            _key, dest, target = best_attack
            melee = {foe.gid for foe in self.melee_targets(unit, dest)}
            if target.gid in melee and target.hp * 2 < target.max_hp:
                return dest, {"type": "skill", "skill": "two_hit", "target": target.gid}
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

    def _tick_oni(self):
        events = []
        for unit in self.living("player"):
            if not unit.oni:
                continue
            unit.oni_left -= 1
            if unit.oni_left <= 0:
                unit.oni = False
                unit.oni_move_only = True
                self._say(f"{unit.name}'s Oni-Wake ends. Next turn, move only.")
                events.append({"t": "oni_end", "gid": unit.gid})
        return events

    def _twin_revive(self, actor: Unit):
        if not actor.twin or not actor.alive:
            return []
        partner = next((unit for unit in self.units if unit.id == actor.twin), None)
        if partner is None or partner.alive or partner.revived_round == self.rnd:
            return []
        spot = None
        for dx, dy in ORTHO:
            nxt = (actor.pos[0] + dx, actor.pos[1] + dy)
            if self.is_free(nxt) and self.height_ok(actor.pos, nxt):
                spot = nxt
                break
        if spot is None:
            return []
        partner.revived_round = self.rnd
        partner.alive = True
        partner.hp = max(1, partner.max_hp // 2)
        partner.pos = spot
        partner.acted = False
        self._say(f"{partner.name} stands again.")
        return [{"t": "spawn", "gid": partner.gid}]

    def _chant_plan(self, unit: Unit):
        if unit.chant or unit.chant_style not in ("once", "full") or "chant" not in unit.skills:
            return None
        if unit.chant_style == "once":
            if unit.chanted or unit.hp * 2 > unit.max_hp:
                return None
            radius = 1
            need = 1
        else:
            if unit.hp * 2 <= unit.max_hp:
                return None
            radius = 2
            need = 3
        best = None
        for y in range(self.h):
            for x in range(self.w):
                center = (x, y)
                if manhattan(unit.pos, center) > 6 or center in self.blocked:
                    continue
                if not self.height_ok(unit.pos, center):
                    continue
                count = 0
                for ally in self.living("player"):
                    if manhattan(ally.pos, center) <= radius and self.height_ok(center, ally.pos):
                        count += 1
                if count >= need and (best is None or count > best[0]):
                    best = (count, center, radius)
        if best is None:
            return None
        _count, center, radius = best
        return unit.pos, {"type": "skill", "skill": "chant", "center": center, "radius": radius}

    def _release_chant(self, unit: Unit):
        if not unit.chant:
            return []
        cx, cy, radius = unit.chant
        unit.chant = None
        self._say(f"{unit.name}'s chant lands.")
        events = [{"t": "chant_land", "gid": unit.gid}]
        for ally in list(self.living("player")):
            if manhattan(ally.pos, (cx, cy)) <= radius and self.height_ok((cx, cy), ally.pos):
                events.extend(self.apply_damage(unit, ally, amount=max(1, ally.hp)))
                if self.outcome:
                    break
        return events

    def chant_marks(self):
        marks = []
        for unit in self.living("enemy"):
            if not unit.chant:
                continue
            cx, cy, radius = unit.chant
            for y in range(cy - radius, cy + radius + 1):
                for x in range(cx - radius, cx + radius + 1):
                    spot = (x, y)
                    if self.in_bounds(spot) and manhattan(spot, (cx, cy)) <= radius:
                        marks.append(spot)
        return marks

    def _steal(self, unit, target):
        if target is None:
            return []
        unit.facing = facing_toward(unit.pos, target.pos)
        options = []
        if target.stone:
            options.append("stone")
        if target.recipe and target.recipe not in self.loot_recipes:
            options.append("recipe")
        if not options or target.is_lord:
            self._say(f"{unit.name} finds nothing to take.")
            return []
        pick = self.rng.choice(options)
        if pick == "stone":
            self.loot_stones.append(target.stone)
            self._say(f"{unit.name} takes the stone.")
            target.stone = None
        else:
            self.loot_recipes.append(target.recipe)
            self._say(f"{unit.name} takes a recipe.")
            target.recipe = None
        return [{"t": "steal", "gid": target.gid}]

    def auto_opening(self):
        if self.outcome or self.phase != "player":
            return None
        for unit in self.units:
            if not (unit.alive and unit.side == "player" and not unit.acted):
                continue
            if unit.oni and not unit.oni_move_only:
                return self.oni_act(unit)
            if unit.status in ("sleep", "confuse", "para"):
                events, _err = self.apply_act(unit, unit.pos, {"type": "wait"})
                return events
        return None

    def oni_act(self, unit: Unit):
        foes = [u for u in self.living("enemy") if u.is_lord or u.hunt]
        if not foes:
            foes = self.living("enemy")
        stand, _prev = self.movement(unit)
        best = None
        if foes:
            goal = min(foes, key=lambda foe: manhattan(unit.pos, foe.pos))
            for dest in stand:
                for target in self.attack_targets(unit, dest):
                    damage = self.preview_damage(unit, target)
                    score = damage + (800 if target.gid == goal.gid or target.is_lord or target.hunt else 0)
                    if damage >= target.hp:
                        score += 400
                    plan = (score, dest, {"type": "attack", "target": target.gid})
                    if best is None or plan[0] > best[0]:
                        best = plan
                for skill_id in unit.skills:
                    skill = SKILLS[skill_id]
                    if unit.sp < self.skill_cost(unit, skill_id):
                        continue
                    if skill["kind"] == "line":
                        for direction in ORTHO:
                            hits = self.line_targets(unit, dest, direction, skill["length"])
                            if not hits:
                                continue
                            score = sum(self.preview_damage(unit, hit) for hit in hits)
                            plan = (score, dest, {"type": "skill", "skill": skill_id, "dir": direction})
                            if best is None or plan[0] > best[0]:
                                best = plan
                    elif skill["kind"] == "multi":
                        for target in self.melee_targets(unit, dest):
                            damage = self.preview_damage(unit, target) + skill.get("flat", 0)
                            score = damage * skill["hits"]
                            plan = (score, dest, {"type": "skill", "skill": skill_id, "target": target.gid})
                            if best is None or plan[0] > best[0]:
                                best = plan
            if best is None:
                dest = min(stand, key=lambda tile: manhattan(tile, goal.pos))
                best = (0, dest, {"type": "wait"})
        if best is None:
            best = (0, unit.pos, {"type": "wait"})
        _score, dest, action = best
        events, err = self.apply_act(unit, dest, action, auto=True)
        if err:
            events, _err = self.apply_act(unit, unit.pos, {"type": "wait"}, auto=True)
        return events
