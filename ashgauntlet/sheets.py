"""Plain sentences for the reading box. No pygame."""

from __future__ import annotations

from ashgauntlet.data import BODIES, GEAR, RECIPES, SKILLS, STONES, gear_bonus, next_enhance_cost

RANGE_LINE = {
    "sword": "A sword strikes the next tile only.",
    "light_sword": "A light sword strikes the next tile only.",
    "dagger": "A dagger strikes the next tile only.",
    "axe": "An axe strikes the next tile only.",
    "spear": "A spear strikes one or two tiles in a straight line, not diagonally. An enemy on the near tile blocks the farther one.",
}


def workshop_intro() -> list[str]:
    return [
        "Ash and Bone are stones, not money. Pawns drop Ash. Spear fighters (Bushi) drop Bone.",
        "Cinder and Void do not drop on these two maps, and nothing here spends them.",
        "Recipes spend stones and make a new piece. A click asks you to continue or cancel before anything is spent.",
        "Souls only raise a piece you already own. Souls cannot buy stones.",
        "Point at Souls, a stone, a recipe, or a piece. This box reads the attack, defense, and the next upgrade.",
    ]


def stone_lines(stone_id: str, have: int) -> list[str]:
    info = STONES[stone_id]
    lines = [
        f"{info['name']}. You have {have}.",
        info["source"],
        info["use"],
    ]
    users = []
    for recipe in RECIPES.values():
        amount = recipe["stones"].get(stone_id)
        if amount:
            users.append(f"{recipe['name']} needs {amount}")
    if users:
        lines.append("Recipes: " + ". ".join(users) + ".")
    else:
        lines.append("No recipe on this march spends it.")
    lines.append("Pointing and clicking here does not spend anything.")
    return lines


def soul_lines(souls: int) -> list[str]:
    return [
        f"You have {souls} souls.",
        "Souls are kept after a win. They are not coins, and they are not stones.",
        "They only raise a piece you already own. Making a new piece spends stones instead.",
        "A sword's first raise costs 200 souls. A coat's first raise costs 150 souls.",
        "A light sword gains half the attack of a Village Sword or an Ash Blade.",
        "Point at a piece on the right to see the exact cost and the new bonus.",
    ]


def holders_line(kind: str) -> str:
    meta = GEAR[kind]
    if meta["slot"] != "weapon":
        return "Anyone can wear it."
    names = [body["name"] for body in BODIES.values() if body["family"] == meta["family"]]
    if not names:
        return "Nobody on this march can hold it."
    if len(names) == 1:
        return f"Only {names[0]} can hold it."
    if len(names) == 2:
        return f"{names[0]} or {names[1]} can hold it."
    return ", ".join(names[:-1]) + f", or {names[-1]} can hold it."


def gear_short(kind: str, plus: int) -> str:
    meta = GEAR[kind]
    stat = "attack" if meta["slot"] == "weapon" else "defense"
    bonus = gear_bonus(kind, plus)
    text = f"{meta['name']} +{plus}: {stat} +{bonus}."
    cost = next_enhance_cost(kind, plus)
    if meta["curve"] is None:
        return text + " Cannot be raised."
    if cost is None:
        return text + " Fully raised."
    text += f" Next {cost} souls makes {stat} +{gear_bonus(kind, plus + 1)}."
    gate = meta.get("gate")
    skill_id = meta.get("skill")
    if gate and skill_id in SKILLS:
        name = SKILLS[skill_id]["name"]
        if plus >= gate:
            text += f" {name} is already learned."
        else:
            text += f" {name} at +{gate}."
    elif meta.get("family") == "light_sword":
        text += " Less attack than a full sword, and no Double Cut."
    return text


def gear_brief(kind: str, plus: int) -> str:
    meta = GEAR[kind]
    stat = "attack" if meta["slot"] == "weapon" else "defense"
    bonus = gear_bonus(kind, plus)
    text = f"{meta['name']} +{plus} adds +{bonus} {stat}."
    cost = next_enhance_cost(kind, plus)
    if meta["curve"] is None:
        return text + " It cannot be raised."
    if cost is None:
        return text + " It cannot be raised further."
    nxt = plus + 1
    text += f" Next raise costs {cost} souls and makes that +{gear_bonus(kind, nxt)}."
    gate = meta.get("gate")
    skill_id = meta.get("skill")
    if gate and skill_id in SKILLS:
        name = SKILLS[skill_id]["name"]
        if plus >= gate:
            text += f" {name} is already learned."
        else:
            text += f" {name} is learned at +{gate}."
    return text


def gear_lines(kind: str, plus: int, owner_name: str | None = None, souls: int | None = None) -> list[str]:
    meta = GEAR[kind]
    stat = "attack" if meta["slot"] == "weapon" else "defense"
    bonus = gear_bonus(kind, plus)
    who = f"Held by {owner_name}." if owner_name else "Spare. Nobody is holding it."
    lines = [
        f"{meta['name']} +{plus}. {who}",
        f"Adds +{bonus} {stat} right now.",
    ]
    cost = next_enhance_cost(kind, plus)
    if meta["curve"] is None:
        lines.append("This piece cannot be raised.")
    elif cost is None:
        lines.append(f"The {stat} bonus is +{bonus}, and it cannot be raised further.")
    else:
        nxt = plus + 1
        nxt_bonus = gear_bonus(kind, nxt)
        lines.append(
            f"Next raise: +{nxt} for {cost} souls. The {stat} bonus becomes +{nxt_bonus}. "
            f"That replaces +{bonus}. It does not add on top."
        )
        if souls is not None and souls < cost:
            lines.append(f"You have {souls} souls, so the button stays dark.")
    gate = meta.get("gate")
    skill_id = meta.get("skill")
    if gate and skill_id in SKILLS:
        skill = SKILLS[skill_id]
        if plus >= gate:
            lines.append(f"The wearer has {skill['name']} ({skill['sp']} skill points). {skill['blurb']}")
        else:
            lines.append(
                f"At +{gate} the wearer learns {skill['name']} ({skill['sp']} skill points). {skill['blurb']}"
            )
    elif meta["family"] == "light_sword":
        lines.append(
            "Raising a light sword adds less attack than a Village Sword or an Ash Blade, and it never learns Double Cut."
        )
    lines.append(holders_line(kind))
    if kind in ("village_sword", "ash_blade"):
        lines.append("A Village Sword and an Ash Blade are the same kind of sword.")
    family = meta.get("family")
    if family in RANGE_LINE:
        lines.append(RANGE_LINE[family])
    return lines


def recipe_lines(recipe_id: str, stones: dict, can: bool) -> list[str]:
    recipe = RECIPES[recipe_id]
    lines = [
        f"{recipe['name']}. {recipe['blurb']}",
        "Making it spends stones, not souls. You will be asked to continue or cancel.",
    ]
    for key, amount in recipe["stones"].items():
        have = int(stones.get(key, 0))
        word = STONES[key]["name"]
        enough = "enough" if have >= amount else "not enough"
        lines.append(f"Needs {amount} {word}. You have {have} ({enough}).")
    if not can:
        lines.append("The button stays dark until you have those stones.")
    kind = recipe["gear"]
    lines.append(gear_brief(kind, 0))
    lines.append(holders_line(kind))
    family = GEAR[kind].get("family")
    if family in RANGE_LINE:
        lines.append(RANGE_LINE[family])
    return lines


def skill_lines(skill_id: str) -> list[str]:
    skill = SKILLS[skill_id]
    return [
        f"{skill['name']} — {skill['sp']} skill points. {skill['blurb']}",
        "Using a skill spends the action. They cannot also attack on that same turn.",
    ]


def issen_lines() -> list[str]:
    return [
        "Issen spends the action. You may step first, but you do not attack on that turn.",
        "It lasts until this fighter's next turn, or until it answers someone.",
        "The next enemy who swings from the next tile with a sword, light sword, dagger, axe, or spear misses and falls.",
        "A spear from two tiles away does not count. Skills do not count.",
        "That attacker is worth four times the souls. A lord would ignore Issen. These two maps have no lord.",
    ]


def herb_lines() -> list[str]:
    return [
        "Herb. Restores 15 health to this fighter, or to a friend on the next tile.",
        "Using it spends the action. Herbs left unused come back if you win.",
    ]


def _skill_sentence(skill_id: str) -> str:
    skill = SKILLS[skill_id]
    return f"{skill['name']} — {skill['sp']} skill points. {skill['blurb']}"


def fighter_block(
    unit,
    later=(),
    strike=None,
    in_reach=None,
    actor_name=None,
    with_loadout=False,
) -> dict:
    family = (unit.weapon_family or "").replace("_", " ")
    title = unit.name if not family else f"{unit.name}  ·  {family}"
    summary = []
    level = getattr(unit, "level", None)
    if level is not None:
        summary.append(f"Level {level}. Experience {getattr(unit, 'exp', 0)}/100 to the next level.")
    summary.append(f"Health {max(unit.hp, 0)}/{unit.max_hp}. Skill points {unit.sp}/{unit.max_sp}.")

    attack = unit.atk + unit.weapon_atk
    weapon_name = unit.weapon_name or ""
    if unit.mode == "strongman":
        attack += 8
    if unit.mode == "weakling":
        attack -= 8
    summary.append(f"Attack {attack}.")
    if weapon_name and weapon_name != "Empty hands":
        summary.append(f"{weapon_name} adds +{unit.weapon_atk} attack.")
    if unit.mode == "strongman":
        summary.append("Strongman adds +8 attack, already included above.")
    elif unit.mode == "weakling":
        summary.append("Weakened: attack is 8 lower, already included above.")

    defense = unit.defn + unit.armor_def + unit.acc_def
    armor_name = getattr(unit, "armor_name", "") or ""
    charm_name = getattr(unit, "charm_name", "") or ""
    if unit.mode == "defender":
        defense += 8
    summary.append(f"Defense {defense}.")
    if armor_name:
        summary.append(f"{armor_name} adds +{unit.armor_def} defense.")
    if charm_name:
        summary.append(f"{charm_name} adds +{unit.acc_def} defense.")
    if unit.mode == "defender":
        summary.append("Defender adds +8 defense, already included above.")
    summary.append(f"Move {unit.mov}.")

    details = []
    if getattr(unit, "lose_flag", False) or unit.id == "kairo":
        details.append("If they fall, this fight is lost.")
    if actor_name and unit.side == "enemy":
        if in_reach and strike is not None:
            details.append(f"A normal attack from {actor_name} deals {strike}.")
        elif in_reach is False:
            details.append(f"{actor_name} cannot reach them with a normal attack from the gold tile.")
    if unit.issen:
        details.append(
            "Issen is set. The next enemy who swings from the next tile with a sword, light sword, dagger, axe, or spear misses and falls."
        )
    if unit.mode == "dodge":
        details.append("Dodge is on. Incoming attacks are less likely to hit.")
    elif unit.mode == "blind":
        details.append("Blind is on. Their bows and guns are less likely to hit.")
    elif unit.mode == "target":
        details.append("They are marked. Every hit against them deals 4 more.")
    elif unit.mode in ("strongman", "defender", "weakling"):
        details.append("The bonus above is already included in the attack or defense number.")
    if unit.acted and unit.side == "player":
        details.append("They have already acted this round.")
    if unit.skills:
        for skill_id in unit.skills:
            if skill_id in SKILLS:
                details.append(_skill_sentence(skill_id))
    else:
        details.append("No skills.")
    if unit.weapon_family in RANGE_LINE:
        details.append(RANGE_LINE[unit.weapon_family])
    if with_loadout:
        weapon_kind = getattr(unit, "weapon_kind", None)
        if weapon_kind:
            details.append(gear_short(weapon_kind, getattr(unit, "weapon_plus", 0)))
        armor_kind = getattr(unit, "armor_kind", None)
        if armor_kind:
            details.append(gear_short(armor_kind, getattr(unit, "armor_plus", 0)))
        elif unit.side == "player":
            details.append("No armor. Defense is only from their body, unless a charm adds some.")
        charm_kind = getattr(unit, "charm_kind", None)
        if charm_kind:
            details.append(gear_short(charm_kind, getattr(unit, "charm_plus", 0)))
    for skill_id, needed in later:
        if skill_id in SKILLS:
            details.append(f"Learns {SKILLS[skill_id]['name']} at level {needed}.")
    herbs = sum(1 for item in getattr(unit, "items", []) or [] if item == "herb")
    if herbs:
        word = "herb" if herbs == 1 else "herbs"
        details.append(f"Carrying {herbs} {word}. A herb restores 15 health and spends the action.")
    if unit.side == "enemy":
        parts = []
        exp_value = getattr(unit, "exp_value", 0)
        if exp_value:
            parts.append(f"{exp_value} experience")
        souls = 100 if getattr(unit, "is_lord", False) else 10
        parts.append(f"{souls} souls")
        stone = getattr(unit, "stone", None)
        if stone in STONES:
            parts.append(f"1 {STONES[stone]['name']}")
        details.append("Defeating them is worth " + ", ".join(parts) + ". You keep that only if you win the fight.")
        recipe = getattr(unit, "recipe", None)
        if recipe in RECIPES:
            details.append(f"They carry the recipe for {RECIPES[recipe]['name']}. You learn it only if you win.")
    return {"title": title, "summary": summary, "details": details}


def describe_body(save, body_id: str) -> dict:
    from ashgauntlet.campaign import materialize

    unit = materialize(save, body_id, (0, 0))
    later = [(skill_id, needed) for skill_id, needed in BODIES[body_id]["skills"] if skill_id not in unit.skills]
    return fighter_block(unit, later=later, with_loadout=True)


def body_card(save, body_id: str) -> list[str]:
    block = describe_body(save, body_id)
    skills = [
        line
        for line in block["details"]
        if "skill points" in line or line.startswith("Learns ") or line.startswith("No skills")
    ]
    return [block["title"], *block["summary"], *skills]
