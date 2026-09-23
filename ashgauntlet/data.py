"""Static rules data for the first march. Names stay synthetic."""

from __future__ import annotations

SKILLS = {
    "shockwave_front": {
        "name": "Shockwave",
        "sp": 16,
        "kind": "line",
        "length": 3,
        "blurb": "Hit a straight line, 3 tiles.",
    },
    "shockwave_four": {
        "name": "Cross Shock",
        "sp": 28,
        "kind": "nova",
        "length": 3,
        "blurb": "Hit all four directions, 3 tiles.",
    },
    "six_hit": {
        "name": "Sixfold",
        "sp": 40,
        "kind": "multi",
        "hits": 6,
        "blurb": "Six strikes on one adjacent enemy.",
    },
    "heal_one": {
        "name": "Heal",
        "sp": 10,
        "kind": "heal",
        "ratio": 0.40,
        "blurb": "Heal yourself, or an ally on the next tile, for 40% of your health.",
    },
    "heal_aura": {
        "name": "Wide Heal",
        "sp": 22,
        "kind": "heal_aura",
        "ratio": 0.25,
        "radius": 2,
        "blurb": "Heal allies within 2 tiles for 25% of your health.",
    },
    "heal_all": {
        "name": "Field Heal",
        "sp": 40,
        "kind": "heal_all",
        "ratio": 0.20,
        "blurb": "Heal every ally for 20% of your health.",
    },
    "strongman": {
        "name": "Strongman",
        "sp": 8,
        "kind": "mode",
        "mode": "strongman",
        "blurb": "Attack +8 for your next two turns.",
    },
    "defender": {
        "name": "Defender",
        "sp": 8,
        "kind": "mode",
        "mode": "defender",
        "blurb": "Defense +8 for your next two turns.",
    },
    "dodge": {
        "name": "Dodge",
        "sp": 8,
        "kind": "mode",
        "mode": "dodge",
        "blurb": "Incoming hits are less likely for two turns.",
    },
    "line_3": {
        "name": "Line Thrust",
        "sp": 18,
        "kind": "line",
        "length": 3,
        "blurb": "Thrust through 3 tiles.",
    },
    "line_8": {
        "name": "Long Thrust",
        "sp": 36,
        "kind": "line",
        "length": 8,
        "blurb": "Thrust through 8 tiles.",
    },
    "thunder": {
        "name": "Thunder",
        "sp": 14,
        "kind": "bolt",
        "length": 4,
        "blurb": "A shot in a straight line, range 4.",
    },
    "two_hit": {
        "name": "Double Cut",
        "sp": 24,
        "kind": "multi",
        "hits": 2,
        "blurb": "Two strikes on one adjacent enemy.",
    },
    "blind": {
        "name": "Blind",
        "sp": 8,
        "kind": "mode_target",
        "mode": "blind",
        "aim": "bolt",
        "length": 4,
        "blurb": "An enemy in a line is worse with bows and guns.",
    },
}

# Soul cost to reach the tier, then the total bonus at that tier.
CURVES = {
    "ash": [(200, 2), (400, 4), (800, 6), (1200, 8)],
    "light": [(200, 1), (400, 2), (800, 3), (1200, 4)],
    "spear": [(200, 2), (400, 4), (800, 6), (1200, 8)],
    "coat": [(150, 1), (300, 2), (500, 3), (800, 4)],
    "charm": [(150, 1), (300, 2)],
}

GEAR = {
    "village_sword": {
        "name": "Village Sword",
        "slot": "weapon",
        "family": "sword",
        "curve": "ash",
        "gate": 4,
        "skill": "two_hit",
    },
    "light_sword": {
        "name": "Light Sword",
        "slot": "weapon",
        "family": "light_sword",
        "curve": "light",
        "gate": None,
        "skill": None,
    },
    "militia_spear": {
        "name": "Militia Spear",
        "slot": "weapon",
        "family": "spear",
        "curve": "spear",
        "gate": 4,
        "skill": "line_3",
    },
    "traveler_dagger": {
        "name": "Traveler Dagger",
        "slot": "weapon",
        "family": "dagger",
        "curve": None,
        "gate": None,
        "skill": None,
    },
    "ash_blade": {
        "name": "Ash Blade",
        "slot": "weapon",
        "family": "sword",
        "curve": "ash",
        "gate": 4,
        "skill": "two_hit",
    },
    "line_spear": {
        "name": "Line Spear",
        "slot": "weapon",
        "family": "spear",
        "curve": "spear",
        "gate": 4,
        "skill": "line_3",
    },
    "cedar_coat": {
        "name": "Cedar Coat",
        "slot": "armor",
        "family": None,
        "curve": "coat",
        "gate": None,
        "skill": None,
    },
    "paper_charm": {
        "name": "Paper Charm",
        "slot": "accessory",
        "family": None,
        "curve": "charm",
        "gate": 2,
        "skill": "heal_one",
    },
}

STONES = {
    "ash": {
        "name": "Ash",
        "source": "A Pawn drops one Ash when they fall.",
        "use": "Every recipe in the workshop spends Ash.",
    },
    "bone": {
        "name": "Bone",
        "source": "A Bushi, the spear fighter, drops one Bone when they fall.",
        "use": "Line Spear and Paper Charm need Bone as well as Ash.",
    },
    "cinder": {
        "name": "Cinder",
        "source": "Cinder is not dropped on the first two maps.",
        "use": "Nothing you can make on this march spends Cinder.",
    },
    "void": {
        "name": "Void",
        "source": "Void is not dropped on the first two maps.",
        "use": "Nothing you can make on this march spends Void.",
    },
}

RECIPES = {
    "ash_blade": {
        "name": "Ash Blade",
        "stones": {"ash": 3},
        "gear": "ash_blade",
        "blurb": "A sword. At +4 it learns Double Cut.",
    },
    "line_spear": {
        "name": "Line Spear",
        "stones": {"ash": 2, "bone": 1},
        "gear": "line_spear",
        "blurb": "A spear. At +4 it learns Line Thrust.",
    },
    "cedar_coat": {
        "name": "Cedar Coat",
        "stones": {"ash": 2},
        "gear": "cedar_coat",
        "blurb": "Armor anyone can wear.",
    },
    "paper_charm": {
        "name": "Paper Charm",
        "stones": {"ash": 1, "bone": 1},
        "gear": "paper_charm",
        "blurb": "At +2 the wearer can Heal.",
    },
}

BODIES = {
    "kairo": {
        "name": "Kairo",
        "family": "sword",
        "mov": 5,
        "hp": 28,
        "sp": 20,
        "atk": 8,
        "defn": 4,
        "growth": (3, 1, 1, 0),
        "start_weapon": "village_sword",
        "skills": (("shockwave_front", 1), ("shockwave_four", 12), ("six_hit", 20)),
    },
    "shio": {
        "name": "Shio",
        "family": "light_sword",
        "mov": 5,
        "hp": 18,
        "sp": 24,
        "atk": 4,
        "defn": 2,
        "growth": (2, 2, 0, 0),
        "start_weapon": "light_sword",
        "skills": (("heal_one", 1), ("heal_aura", 10), ("heal_all", 22)),
    },
    "spear_one": {
        "name": "Spear-One",
        "family": "spear",
        "mov": 4,
        "hp": 26,
        "sp": 16,
        "atk": 7,
        "defn": 4,
        "growth": (3, 1, 1, 0),
        "start_weapon": "militia_spear",
        "skills": (("line_3", 1), ("heal_one", 8), ("line_8", 18)),
    },
    "sword_two": {
        "name": "Sword-Two",
        "family": "sword",
        "mov": 5,
        "hp": 24,
        "sp": 16,
        "atk": 6,
        "defn": 4,
        "growth": (3, 1, 1, 0),
        "start_weapon": "village_sword",
        "skills": (("strongman", 1), ("defender", 6), ("dodge", 14)),
    },
    "swallow": {
        "name": "Swallow",
        "family": "dagger",
        "mov": 7,
        "hp": 18,
        "sp": 18,
        "atk": 6,
        "defn": 2,
        "growth": (2, 1, 1, 0),
        "start_weapon": "traveler_dagger",
        "skills": (("thunder", 1), ("blind", 10)),
    },
}

ENEMIES = {
    "pawn": {
        "name": "Pawn",
        "family": "sword",
        "sprite": "pawn",
        "hp": 12,
        "sp": 0,
        "atk": 6,
        "defn": 1,
        "mov": 4,
        "skills": [],
        "stone": "ash",
        "exp": 40,
    },
    "bushi": {
        "name": "Bushi",
        "family": "spear",
        "sprite": "bushi",
        "hp": 16,
        "sp": 18,
        "atk": 7,
        "defn": 2,
        "mov": 4,
        "skills": ["line_3"],
        "stone": "bone",
        "exp": 50,
    },
}

EP1_ROWS = [
    "000000000000",
    "000000000000",
    "000000000000",
    "000002200000",
    "000001100000",
    "000001100000",
    "000001100000",
    "011111111110",
    "000000000000",
    "000000000000",
    "000000000000",
    "000000000000",
]


def cedar_rows() -> list[str]:
    rows = []
    for _y in range(12):
        chars = []
        for x in range(12):
            if x <= 3:
                chars.append("0")
            elif x <= 6:
                chars.append("1")
            else:
                chars.append("2")
        rows.append("".join(chars))
    return rows


EPISODES = [
    {
        "id": 1,
        "name": "Kureha Burns",
        "place": "Kureha",
        "theme": "village",
        "heights": EP1_ROWS,
        "blocked": [(0, 0), (11, 0), (0, 11), (11, 11), (1, 1), (10, 1), (1, 10), (10, 10)],
        "slots": [(4, 10), (7, 10)],
        "must": ["kairo", "sword_two"],
        "recruit_before": [],
        "recruit_after": ["shio"],
        "enemies": [
            {"kind": "pawn", "pos": (5, 3), "recipe": "cedar_coat"},
            {"kind": "pawn", "pos": (2, 4)},
            {"kind": "pawn", "pos": (9, 4)},
            {"kind": "pawn", "pos": (3, 7), "recipe": "ash_blade"},
            {"kind": "pawn", "pos": (8, 7)},
        ],
        "reinforcements": [
            {"round": 2, "body": "shio", "pos": (0, 9), "lose_flag": True, "gift_herb": True},
        ],
        "intro": [
            ("Narrator", "Year of the Broken Calendar. The village of Kureha is on fire."),
            ("Kairo", "Those are not our neighbors anymore. Stay on my shoulder."),
            ("Sword-Two", "The yard steps up in the middle. A blade cannot cross a tall gap."),
            ("Narrator", "Click one of your fighters, then a blue tile, then a red enemy."),
        ],
        "outro": [
            ("Shio", "I followed the smoke. If you send me away, I will only come back."),
            ("Kairo", "Then stay behind the line. You are the one who keeps us standing."),
            ("Narrator", "The gauntlet is warm. Stones and souls can be worked before the next road."),
        ],
    },
    {
        "id": 2,
        "name": "Cedar Pass",
        "place": "Cedar pass",
        "theme": "cedar",
        "heights": cedar_rows(),
        "blocked": [(x, y) for y in range(12) for x in range(7, 12)] + [(0, 0), (0, 11)],
        "slots": [(1, 11), (2, 11), (3, 11), (2, 10)],
        "must": ["kairo"],
        "recruit_before": ["spear_one"],
        "recruit_after": ["swallow"],
        "enemies": [
            {"kind": "bushi", "pos": (6, 2), "recipe": "line_spear"},
            {"kind": "bushi", "pos": (5, 4)},
            {"kind": "pawn", "pos": (2, 2)},
            {"kind": "pawn", "pos": (1, 4), "recipe": "paper_charm"},
            {"kind": "pawn", "pos": (3, 5)},
        ],
        "reinforcements": [],
        "intro": [
            ("Spear-One", "I am Spear-One. I held this pass until their spears outreached me."),
            ("Kairo", "Then you take the front. Show us the distance."),
            ("Shio", "I will be close. Do not make me run."),
        ],
        "outro": [
            ("Swallow", "The next town is already full of guns. I am coming with you. Call me Swallow."),
            ("Kairo", "Then walk behind the spears until the pass is behind us."),
            ("Narrator", "The cedar pass is quiet. This first march ends here. You can walk these fights again."),
        ],
    },
]


def episode(episode_id: int) -> dict:
    for ep in EPISODES:
        if ep["id"] == episode_id:
            return ep
    raise KeyError(episode_id)


def grid_from_rows(rows: list[str]) -> tuple[dict, int, int]:
    heights = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            heights[(x, y)] = int(ch)
    return heights, len(rows[0]), len(rows)


def gear_bonus(kind: str, plus: int) -> int:
    meta = GEAR[kind]
    curve = meta["curve"]
    if not curve or plus <= 0:
        return 0
    table = CURVES[curve]
    plus = min(plus, len(table))
    return table[plus - 1][1]


def next_enhance_cost(kind: str, plus: int) -> int | None:
    meta = GEAR[kind]
    curve = meta["curve"]
    if not curve:
        return None
    table = CURVES[curve]
    if plus >= len(table):
        return None
    return table[plus][0]


def raise_line(kind: str, plus: int) -> str:
    meta = GEAR[kind]
    cost = next_enhance_cost(kind, plus)
    nxt = plus + 1
    bonus = gear_bonus(kind, nxt)
    stat = "attack" if meta["slot"] == "weapon" else "defense"
    line = f"Raise {meta['name']} to +{nxt} for {cost} souls? Its {stat} bonus becomes +{bonus}."
    skill = meta.get("skill")
    if meta.get("gate") == nxt and skill in SKILLS:
        line += f" It learns {SKILLS[skill]['name']}."
    return line + " Continue or cancel."


def craft_line(recipe_id: str) -> str:
    recipe = RECIPES[recipe_id]
    cost = ", ".join(f"{amount} {name}" for name, amount in recipe["stones"].items())
    return f"Craft {recipe['name']}? This spends {cost}. Continue or cancel."


ISSEN_FAMILIES = {"sword", "light_sword", "dagger", "axe", "spear"}
MELEE_FAMILIES = {"sword", "light_sword", "dagger", "axe"}
LINE_FAMILIES = {"bow", "gun"}
