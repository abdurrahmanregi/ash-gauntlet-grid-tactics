"""Static rules data. Names stay synthetic."""

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
    "shot_2": {
        "name": "Twin Shot",
        "sp": 14,
        "kind": "salvo",
        "hits": 2,
        "length": 5,
        "blurb": "Two shots on one enemy in gun range. Not two enemies.",
    },
    "shot_3": {
        "name": "Triple Shot",
        "sp": 24,
        "kind": "salvo",
        "hits": 3,
        "length": 5,
        "blurb": "Three shots on one enemy in gun range.",
    },
    "salvo_8": {
        "name": "Eight Salvo",
        "sp": 36,
        "kind": "salvo",
        "hits": 8,
        "length": 5,
        "blurb": "Eight shots on one enemy in gun range, not eight enemies.",
    },
    "target": {
        "name": "Target",
        "sp": 8,
        "kind": "mode_target",
        "mode": "target",
        "blurb": "That enemy takes 4 more damage from every hit for two turns.",
    },
    "weakling": {
        "name": "Weakling",
        "sp": 8,
        "kind": "mode_target",
        "mode": "weakling",
        "blurb": "That enemy's attack drops by 8 for two turns.",
    },
    "fire_2": {
        "name": "Twin Flame",
        "sp": 24,
        "kind": "multi",
        "hits": 2,
        "blurb": "Two burning strikes on one adjacent enemy.",
    },
    "fire_3": {
        "name": "Triple Flame",
        "sp": 24,
        "kind": "multi",
        "hits": 3,
        "blurb": "Three burning strikes on one adjacent enemy.",
    },
    "smash": {
        "name": "Smash",
        "sp": 24,
        "kind": "multi",
        "hits": 2,
        "flat": 4,
        "blurb": "Two strikes on one adjacent enemy. Each strike deals 4 more.",
    },
    "whirlwind": {
        "name": "Whirlwind",
        "sp": 28,
        "kind": "nova",
        "length": 1,
        "blurb": "Hit all four tiles beside you.",
    },
    "cross": {
        "name": "Cross",
        "sp": 28,
        "kind": "cross",
        "length": 3,
        "blurb": "Hit in front of you and behind you, up to 3 tiles each way.",
    },
    "aura": {
        "name": "Aura",
        "sp": 30,
        "kind": "aura",
        "blurb": "Every ally gains 5 attack and 5 defense for this round and the next.",
    },
    "sleep_touch": {
        "name": "Sleep",
        "sp": 12,
        "kind": "status",
        "status": "sleep",
        "blurb": "The next-door enemy sleeps for two of their turns. A hit wakes them.",
    },
    "confuse_touch": {
        "name": "Confuse",
        "sp": 12,
        "kind": "status",
        "status": "confuse",
        "blurb": "The next-door enemy does nothing for two of their turns. A hit does not clear it.",
    },
    "sleep_arrow": {
        "name": "Sleep Arrow",
        "sp": 12,
        "kind": "status",
        "status": "sleep",
        "aim": "bolt",
        "length": 5,
        "blurb": "An enemy in bow range sleeps for two of their turns. A hit wakes them.",
    },
    "poison_arrow": {
        "name": "Poison Arrow",
        "sp": 12,
        "kind": "status",
        "status": "poison",
        "aim": "bolt",
        "length": 5,
        "blurb": "An enemy in bow range loses 3 health at the start of each of their next two turns.",
    },
    "para_arrow": {
        "name": "Para Arrow",
        "sp": 12,
        "kind": "status",
        "status": "para",
        "aim": "bolt",
        "length": 5,
        "blurb": "An enemy in bow range does nothing for two of their turns. A hit does not clear it.",
    },
    "steal": {
        "name": "Steal",
        "sp": 8,
        "kind": "steal",
        "blurb": "Take one stone or one recipe from the next-door enemy. Lords have nothing to take.",
    },
    "oni_wake": {
        "name": "Oni-Wake",
        "sp": 0,
        "kind": "oni",
        "blurb": "Spend half of Kairo's maximum skill points, rounded down. He fights alone for three enemy turns, then can only move.",
    },
    "chant": {
        "name": "Chant",
        "sp": 0,
        "kind": "chant",
        "blurb": "Mark a ring. On the next turn, anyone still inside falls unless the chanter was hit.",
    },
}

# Soul cost to reach the tier, then the total bonus at that tier.
CURVES = {
    "ash": [(200, 2), (400, 4), (800, 6), (1200, 8)],
    "light": [(200, 1), (400, 2), (800, 3), (1200, 4)],
    "spear": [(200, 2), (400, 4), (800, 6), (1200, 8)],
    "coat": [(150, 1), (300, 2), (500, 3), (800, 4)],
    "charm": [(150, 1), (300, 2)],
    "gun": [(300, 2), (600, 4), (1000, 6), (1600, 8)],
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
    "clan_gun": {
        "name": "Clan Gun",
        "slot": "weapon",
        "family": "gun",
        "curve": "gun",
        "gate": 4,
        "skill": "shot_3",
    },
    "nest_gun": {
        "name": "Nest Gun",
        "slot": "weapon",
        "family": "gun",
        "curve": "gun",
        "gate": 4,
        "skill": "shot_3",
    },
    "saint_bow": {
        "name": "Saint Bow",
        "slot": "weapon",
        "family": "bow",
        "curve": None,
        "gate": None,
        "skill": None,
    },
    "camp_axe": {
        "name": "Camp Axe",
        "slot": "weapon",
        "family": "axe",
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
        "source": "A Pawn or a Gunner drops one Ash when they fall.",
        "use": "Every recipe in the workshop spends Ash.",
    },
    "bone": {
        "name": "Bone",
        "source": "A Bushi, the spear fighter, drops one Bone when they fall.",
        "use": "Line Spear and Paper Charm need Bone as well as Ash.",
    },
    "cinder": {
        "name": "Cinder",
        "source": "Camp beasts drop one Cinder. The factory does too.",
        "use": "Nest Gun needs Cinder as well as Bone.",
    },
    "void": {
        "name": "Void",
        "source": "A lord drops two Void. Hollow Depths floors 9 to 12 drop Void.",
        "use": "Nothing in the workshop spends Void.",
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
    "nest_gun": {
        "name": "Nest Gun",
        "stones": {"bone": 2, "cinder": 1},
        "gear": "nest_gun",
        "blurb": "A gun. At +4 it learns Triple Shot.",
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
    "gun_chief": {
        "name": "Gun-Chief",
        "family": "gun",
        "mov": 4,
        "hp": 22,
        "sp": 16,
        "atk": 7,
        "defn": 3,
        "growth": (2, 1, 1, 0),
        "start_weapon": "clan_gun",
        "pitch": "Shoots a straight line. A person in the way stops it.",
        "skills": (("shot_2", 1), ("shot_3", 10), ("salvo_8", 20)),
    },
    "stage_man": {
        "name": "Stage-Man",
        "family": "sword",
        "mov": 4,
        "hp": 34,
        "sp": 14,
        "atk": 6,
        "defn": 6,
        "growth": (4, 1, 0, 1),
        "start_weapon": "village_sword",
        "pitch": "Strongman adds 8 attack, and it spends the whole action.",
        "skills": (("strongman", 1), ("defender", 8)),
    },
    "smith": {
        "name": "Smith",
        "family": "sword",
        "mov": 5,
        "hp": 26,
        "sp": 14,
        "atk": 7,
        "defn": 4,
        "growth": (3, 1, 1, 0),
        "start_weapon": "village_sword",
        "pitch": "Shockwave hits a straight line of 3.",
        "skills": (("shockwave_front", 1), ("target", 12)),
    },
    "bow_saint": {
        "name": "Bow-Saint",
        "family": "bow",
        "mov": 4,
        "hp": 20,
        "sp": 18,
        "atk": 6,
        "defn": 2,
        "growth": (2, 1, 1, 0),
        "start_weapon": "saint_bow",
        "pitch": "Arrows fly in a straight line. Sleep breaks when they are hit.",
        "skills": (("sleep_arrow", 1), ("poison_arrow", 8), ("para_arrow", 16)),
    },
    "dancer": {
        "name": "Dancer",
        "family": "light_sword",
        "mov": 5,
        "hp": 20,
        "sp": 20,
        "atk": 5,
        "defn": 2,
        "growth": (2, 2, 0, 0),
        "start_weapon": "light_sword",
        "pitch": "Sleep and confuse an adjacent enemy. Sleep breaks when they are hit.",
        "skills": (("sleep_touch", 1), ("confuse_touch", 10)),
    },
    "monk_spear": {
        "name": "Monk-Spear",
        "family": "spear",
        "mov": 4,
        "hp": 24,
        "sp": 18,
        "atk": 7,
        "defn": 3,
        "growth": (2, 1, 1, 0),
        "start_weapon": "militia_spear",
        "pitch": "Cross hits in front and behind, up to 3 tiles each way.",
        "skills": (("cross", 1), ("weakling", 12)),
    },
    "half_blood": {
        "name": "Half-Blood",
        "family": "sword",
        "mov": 5,
        "hp": 22,
        "sp": 18,
        "atk": 7,
        "defn": 3,
        "growth": (2, 1, 1, 0),
        "start_weapon": "village_sword",
        "pitch": "Two or three burning strikes on one adjacent enemy.",
        "skills": (("fire_2", 1), ("fire_3", 14)),
    },
    "deserter": {
        "name": "Deserter",
        "family": "dagger",
        "mov": 7,
        "hp": 18,
        "sp": 16,
        "atk": 6,
        "defn": 2,
        "growth": (2, 1, 1, 0),
        "start_weapon": "traveler_dagger",
        "pitch": "Steal a stone or a recipe. Lords have nothing you can take.",
        "skills": (("steal", 1), ("dodge", 12)),
    },
    "coil_champion": {
        "name": "Coil-Champion",
        "family": "dagger",
        "mov": 7,
        "hp": 20,
        "sp": 18,
        "atk": 7,
        "defn": 2,
        "growth": (2, 1, 1, 0),
        "start_weapon": "traveler_dagger",
        "pitch": "Whirlwind hits the four tiles beside you.",
        "skills": (("whirlwind", 1), ("thunder", 12)),
    },
    "fang_champion": {
        "name": "Fang-Champion",
        "family": "axe",
        "mov": 4,
        "hp": 32,
        "sp": 12,
        "atk": 9,
        "defn": 5,
        "growth": (3, 1, 1, 1),
        "start_weapon": "camp_axe",
        "pitch": "Smash hits twice, and each hit deals 4 more.",
        "skills": (("smash", 1), ("strongman", 10)),
    },
    "shell_champion": {
        "name": "Shell-Champion",
        "family": "spear",
        "mov": 4,
        "hp": 30,
        "sp": 20,
        "atk": 6,
        "defn": 7,
        "growth": (3, 1, 0, 1),
        "start_weapon": "militia_spear",
        "pitch": "Aura raises every ally's attack and defense by 5 for this round and the next.",
        "skills": (("aura", 1), ("line_3", 8)),
    },
    "soot_child": {
        "name": "Soot-Child",
        "family": "axe",
        "mov": 5,
        "hp": 20,
        "sp": 10,
        "atk": 6,
        "defn": 3,
        "growth": (5, 1, 2, 1),
        "start_weapon": "camp_axe",
        "pitch": "Joins from Hollow Depths floor 12, at level 1, however far the road has gone.",
        "skills": (("smash", 1), ("six_hit", 16)),
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
    "gunner": {
        "name": "Gunner",
        "family": "gun",
        "sprite": "gunner",
        "hp": 14,
        "sp": 0,
        "atk": 7,
        "defn": 2,
        "mov": 4,
        "skills": [],
        "stone": "ash",
        "exp": 45,
    },
    "claw": {
        "name": "Claw",
        "family": "axe",
        "sprite": "claw",
        "hp": 20,
        "sp": 24,
        "atk": 8,
        "defn": 3,
        "mov": 5,
        "skills": ["two_hit"],
        "stone": "cinder",
        "exp": 55,
    },
    "bomb": {
        "name": "Fang",
        "family": "sword",
        "sprite": "bomb",
        "hp": 24,
        "sp": 0,
        "atk": 8,
        "defn": 3,
        "mov": 4,
        "skills": [],
        "stone": "cinder",
        "exp": 60,
    },
    "nest": {
        "name": "Gun Nest",
        "family": "gun",
        "sprite": "nest",
        "hp": 30,
        "sp": 0,
        "atk": 9,
        "defn": 5,
        "mov": 0,
        "skills": [],
        "stone": None,
        "exp": 45,
    },
    "beast": {
        "name": "Beast",
        "family": "sword",
        "sprite": "beast",
        "hp": 56,
        "sp": 0,
        "atk": 12,
        "defn": 5,
        "mov": 4,
        "skills": [],
        "stone": None,
        "exp": 100,
    },
    "lord": {
        "name": "Lord",
        "family": "sword",
        "sprite": "lord",
        "hp": 60,
        "sp": 20,
        "atk": 13,
        "defn": 6,
        "mov": 5,
        "skills": [],
        "stone": None,
        "exp": 110,
    },
    "captain": {
        "name": "Captain",
        "family": "spear",
        "sprite": "bushi",
        "hp": 40,
        "sp": 18,
        "atk": 10,
        "defn": 4,
        "mov": 4,
        "skills": ["line_3"],
        "stone": "bone",
        "exp": 80,
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


def town_rows() -> list[str]:
    return ["0" * 12 for _ in range(12)]


def town_blocked() -> list[tuple[int, int]]:
    blocked = []
    for y in range(12):
        if y in (4, 9):
            continue
        for x in (0, 1, 4, 5, 6, 7, 10, 11):
            blocked.append((x, y))
    return blocked


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
            ("Narrator", "The cedar pass is quiet. The gun town is the next road."),
        ],
    },
    {
        "id": 3,
        "name": "Gun-Clan Town",
        "place": "Gun-clan town",
        "theme": "town",
        "heights": town_rows(),
        "blocked": town_blocked(),
        "slots": [(2, 11), (3, 11), (8, 11), (9, 11), (2, 10), (8, 10)],
        "must": ["kairo"],
        "recruit_before": ["gun_chief"],
        "recruit_after": [],
        "enemies": [
            {"kind": "gunner", "pos": (2, 1)},
            {"kind": "gunner", "pos": (9, 1)},
            {"kind": "gunner", "pos": (3, 3)},
            {"kind": "pawn", "pos": (8, 6)},
            {"kind": "pawn", "pos": (3, 7)},
        ],
        "reinforcements": [],
        "intro": [
            ("Gun-Chief", "I am Gun-Chief. Their guns hold the two streets. A shot travels in a straight line, and it stops if someone stands in it."),
            ("Kairo", "Then you take a lane. We will not stand in your shot."),
            ("Swallow", "I can run the alleys. Call the shot before you fire."),
        ],
        "outro": [
            ("Gun-Chief", "The clan will not hold this town again. The gun stays with me."),
            ("Kairo", "Then take the back of the line."),
            ("Narrator", "The gun town is quiet. You can walk it again."),
        ],
    },
]


from ashgauntlet.road import DEPTHS, LATER_EPISODES

EPISODES.extend(LATER_EPISODES)


def level_label(episode_id: int, name: str, status: str | None = None) -> str:
    text = f"Level {episode_id} - {name}"
    if status:
        text += f" - {status}"
    return text


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
