"""A plain fighter used to prove the march can be won."""

from __future__ import annotations

from ashgauntlet.data import SKILLS
from ashgauntlet.rules import ORTHO, manhattan


def _rank(action, dest, pos) -> float:
    kind = action["type"]
    score = {"attack": 4, "skill": 3, "item": 3, "issen": 2, "wait": 0}.get(kind, 0)
    if dest != pos:
        score += 0.2
    return score


def choose(battle, unit):
    stand, _prev = battle.movement(unit)
    foes = [u for u in battle.units if u.alive and u.side == "enemy"]
    allies = [u for u in battle.units if u.alive and u.side == "player" and u.gid != unit.gid]

    if unit.id == "shio":
        return _choose_shio(battle, unit, stand, foes, allies)
    if unit.lose_flag and unit.id != "kairo" and foes and stand:
        goal = min(foes, key=lambda foe: manhattan(unit.pos, foe.pos))
        dest = max(stand, key=lambda tile: (manhattan(tile, goal.pos), -manhattan(tile, unit.pos)))
        return dest, {"type": "wait"}

    best = None
    for dest in stand:
        for target in battle.attack_targets(unit, dest):
            damage = battle.preview_damage(unit, target)
            score = 1000 - target.hp + damage
            if damage >= target.hp:
                score += 400
            plan = (score, dest, {"type": "attack", "target": target.gid})
            if best is None or plan[0] > best[0]:
                best = plan
        for skill_id in unit.skills:
            skill = SKILLS[skill_id]
            if skill["kind"] != "line" or unit.sp < skill["sp"]:
                continue
            for direction in ORTHO:
                hits = battle.line_targets(unit, dest, direction, skill["length"])
                if not hits:
                    continue
                score = sum(800 - hit.hp for hit in hits) + 180 * (len(hits) - 1)
                plan = (score, dest, {"type": "skill", "skill": skill_id, "dir": direction})
                if best is None or plan[0] > best[0]:
                    best = plan
    if best:
        return best[1], best[2]

    if foes and "strongman" in unit.skills and unit.sp >= 8 and unit.mode != "strongman":
        nearest = min(manhattan(unit.pos, foe.pos) for foe in foes)
        if nearest > unit.mov + 1:
            return unit.pos, {"type": "skill", "skill": "strongman"}

    if foes and stand:
        goal = min(foes, key=lambda foe: manhattan(foe.pos, unit.pos))
        dest = min(stand, key=lambda tile: (manhattan(tile, goal.pos), manhattan(tile, unit.pos)))
        return dest, {"type": "wait"}
    return unit.pos, {"type": "wait"}


def _choose_shio(battle, unit, stand, foes, allies):
    if "heal_one" in unit.skills and unit.sp >= SKILLS["heal_one"]["sp"]:
        best = None
        if unit.hp < unit.max_hp:
            missing = unit.max_hp - unit.hp
            best = (missing, unit.pos, unit)
        for dest in stand:
            for ally in allies:
                if ally.hp >= ally.max_hp:
                    continue
                if not battle.is_adjacent(dest, ally.pos) or not battle.height_ok(dest, ally.pos):
                    continue
                missing = ally.max_hp - ally.hp
                if ally.lose_flag or ally.id == "kairo":
                    missing += 8
                if best is None or missing > best[0]:
                    best = (missing, dest, ally)
        if best and best[0] >= 6:
            return best[1], {"type": "skill", "skill": "heal_one", "target": best[2].gid}
    if foes and stand:
        injured = [ally for ally in allies if ally.hp < ally.max_hp]
        if injured and unit.sp >= 10:
            goal = min(injured, key=lambda ally: ally.hp / ally.max_hp)
            dest = min(
                stand,
                key=lambda tile: (
                    manhattan(tile, goal.pos),
                    -min(manhattan(tile, foe.pos) for foe in foes),
                ),
            )
            return dest, {"type": "wait"}
        dest = max(stand, key=lambda tile: min(manhattan(tile, foe.pos) for foe in foes))
        return dest, {"type": "wait"}
    return unit.pos, {"type": "wait"}


def play(battle, limit: int = 250) -> str | None:
    steps = 0
    while battle.outcome is None and steps < limit:
        steps += 1
        if battle.phase == "player":
            ready = [u for u in battle.units if u.alive and u.side == "player" and not u.acted]
            if not ready:
                battle.end_player_phase()
                continue
            picked = None
            picked_rank = -1.0
            for unit in ready:
                dest, action = choose(battle, unit)
                rank = _rank(action, dest, unit.pos)
                if unit.id == "kairo":
                    rank += 0.05
                if rank > picked_rank:
                    picked_rank = rank
                    picked = (unit, dest, action)
            unit, dest, action = picked
            _events, err = battle.player_act(unit.gid, dest, action)
            if err:
                _events, err = battle.player_act(unit.gid, unit.pos, {"type": "wait"})
                if err:
                    break
        else:
            battle.enemy_step()
    return battle.outcome
