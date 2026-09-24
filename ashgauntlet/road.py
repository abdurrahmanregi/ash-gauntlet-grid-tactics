"""Levels 4–24 and the Hollow Depths. Names stay synthetic."""

from __future__ import annotations


def flat(n: int = 12, band: str = "0") -> list[str]:
    return [band * n for _ in range(n)]


def slope_rows(n: int = 12) -> list[str]:
    rows = []
    for y in range(n):
        if y <= 3:
            band = "2"
        elif y <= 7:
            band = "1"
        else:
            band = "0"
        rows.append(band * n)
    return rows


def stair_rows(n: int = 12) -> list[str]:
    rows = []
    for y in range(n):
        if y >= 8:
            middle = "0"
        elif y >= 4:
            middle = "1"
        else:
            middle = "2"
        chars = []
        for x in range(n):
            if x <= 1 or x >= n - 2:
                chars.append("2" if y < 8 else "0")
            else:
                chars.append(middle)
        rows.append("".join(chars))
    return rows


def river_blocked(n: int = 12) -> list[tuple[int, int]]:
    blocked = []
    for y in range(n):
        for x in (0, 1, n - 2, n - 1):
            blocked.append((x, y))
    return blocked


def gate_blocked(n: int = 12) -> list[tuple[int, int]]:
    blocked = [(x, 0) for x in range(n)]
    for y in range(n):
        blocked.append((0, y))
        blocked.append((n - 1, y))
    for y in range(3, 6):
        blocked.append((4, y))
        blocked.append((7, y))
    return blocked


def corner_blocked() -> list[tuple[int, int]]:
    return [(0, 0), (11, 0), (0, 11), (11, 11)]


BOTTOM = [(3, 11), (4, 11), (5, 11), (6, 11), (7, 11), (8, 11), (4, 10), (7, 10)]


def _ep(**kwargs) -> dict:
    kwargs.setdefault("reinforcements", [])
    kwargs.setdefault("guests", [])
    kwargs.setdefault("recruit_before", [])
    kwargs.setdefault("recruit_after", [])
    kwargs.setdefault("win", "rout")
    kwargs.setdefault("battle", True)
    return kwargs


LATER_EPISODES = [
    _ep(
        id=4,
        name="River Stage",
        place="River stage",
        theme="river",
        heights=flat(),
        blocked=river_blocked(),
        slots=BOTTOM,
        must=["kairo"],
        recruit_before=["stage_man"],
        enemies=[
            {"kind": "pawn", "pos": (3, 2)},
            {"kind": "pawn", "pos": (8, 2)},
            {"kind": "bushi", "pos": (5, 3)},
            {"kind": "bushi", "pos": (6, 4)},
            {"kind": "pawn", "pos": (4, 5)},
            {"kind": "gunner", "pos": (7, 1)},
        ],
        intro=[
            ("Stage-Man", "I am Stage-Man. Strongman adds 8 attack, and it spends the whole action. You do not swing on that same turn."),
            ("Kairo", "Then you raise it before they close. We will take the bank."),
            ("Sword-Two", "I already know that stance. I will not waste it on an empty road."),
            ("Deserter", "I am only passing this stage. The capital road is where I join."),
        ],
        outro=[
            ("Stage-Man", "The river is quiet. I am coming with the swords."),
            ("Kairo", "Then walk in the middle. The water is not a path."),
            ("Narrator", "The next gate has a name. One marked enemy ends it."),
        ],
    ),
    _ep(
        id=5,
        name="Gate of Ash",
        place="Gate of Ash",
        theme="castle",
        heights=flat(band="1"),
        blocked=gate_blocked(),
        slots=[(2, 10), (3, 10), (5, 10), (6, 10), (8, 10), (9, 10), (3, 11), (8, 11)],
        must=["kairo"],
        win="lord",
        enemies=[
            {
                "kind": "captain",
                "pos": (5, 2),
                "id": "ash_warden",
                "name": "Ash Warden",
                "hunt": True,
                "family": "spear",
                "hp": 40,
                "atk": 10,
                "defn": 4,
                "exp": 80,
                "stone": "ash",
                "sprite": "bushi",
            },
            {"kind": "bushi", "pos": (2, 3)},
            {"kind": "bushi", "pos": (9, 3)},
            {"kind": "pawn", "pos": (5, 6)},
            {"kind": "pawn", "pos": (6, 6)},
        ],
        intro=[
            ("Kairo", "The Ash Warden is the one that matters. When he falls, the gate is ours on the next turn."),
            ("Stage-Man", "The others can wait. He is not a lord. Issen still answers him."),
            ("Narrator", "A gold dot on your own fighter means the fight is lost if they fall. The Warden has no such protection."),
        ],
        outro=[
            ("Kairo", "The gate is open. The high ground ahead belongs to something with fangs."),
            ("Narrator", "The Warden was not a lord. Later named lords will ignore Issen."),
        ],
    ),
    _ep(
        id=6,
        name="White Fang Approach",
        place="White Fang approach",
        theme="camp",
        heights=slope_rows(),
        blocked=corner_blocked(),
        slots=BOTTOM,
        must=["kairo"],
        enemies=[
            {"kind": "claw", "pos": (3, 1)},
            {"kind": "claw", "pos": (6, 1)},
            {"kind": "claw", "pos": (8, 2)},
            {"kind": "pawn", "pos": (5, 2)},
            {"kind": "bushi", "pos": (4, 3)},
        ],
        intro=[
            ("Kairo", "They stand on the high step. A blow from above hits harder. Climb before you trade swings."),
            ("Swallow", "I can run the low ground and come up beside them."),
            ("Narrator", "From here on, an enemy on a higher step deals 6 more on the first hit of that swing."),
        ],
        outro=[
            ("Kairo", "The den is next. Two of them share a life. Kill both before their turn, or one stands back up."),
            ("Narrator", "The approach is quiet. You can walk it again."),
        ],
    ),
    _ep(
        id=7,
        name="White Fang Den",
        place="White Fang den",
        theme="camp",
        heights=flat(band="1"),
        blocked=[(1, 1), (10, 1), (1, 10), (10, 10), (5, 6), (6, 6)],
        slots=[(2, 11), (3, 11), (4, 11), (7, 11), (8, 11), (9, 11), (3, 10), (8, 10)],
        must=["kairo"],
        recruit_after=["fang_champion"],
        enemies=[
            {
                "kind": "bomb",
                "pos": (3, 3),
                "id": "fang_a",
                "twin": "fang_b",
                "name": "White Fang",
                "sprite": "bomb",
            },
            {
                "kind": "bomb",
                "pos": (8, 3),
                "id": "fang_b",
                "twin": "fang_a",
                "name": "Pale Fang",
                "sprite": "bomb_b",
            },
            {"kind": "claw", "pos": (5, 2)},
            {"kind": "claw", "pos": (6, 4)},
            {"kind": "pawn", "pos": (4, 5)},
        ],
        intro=[
            ("Kairo", "White Fang and Pale Fang. If one is down when the other acts, the fallen one stands at half health."),
            ("Shio", "Then drop them both on our turn. I will not have the souls to spare a second time."),
            ("Narrator", "A revive happens only once for each of them in a round, and the souls from the first fall are not returned."),
        ],
        outro=[
            ("Fang-Champion", "The den is finished. I am Fang-Champion. The high-ground blow is yours now, if you set that stance."),
            ("Kairo", "One stance only. We will choose it before the next deploy."),
            ("Narrator", "White Fang stance: an ally above the target deals 6 more on the first hit."),
        ],
    ),
    _ep(
        id=8,
        name="Half-Blood Ridge",
        place="Half-blood ridge",
        theme="camp",
        heights=slope_rows(),
        blocked=corner_blocked(),
        slots=BOTTOM,
        must=["kairo"],
        recruit_before=["half_blood"],
        enemies=[
            {"kind": "claw", "pos": (2, 1)},
            {"kind": "claw", "pos": (7, 1)},
            {"kind": "bushi", "pos": (4, 2)},
            {"kind": "pawn", "pos": (8, 3)},
            {"kind": "pawn", "pos": (5, 4)},
        ],
        intro=[
            ("Half-Blood", "I am Half-Blood. Two burning strikes, or three when I am older. One enemy, not a line."),
            ("Kairo", "Then take a flank. Do not stand where their height can answer you."),
            ("Dancer", "I am only watching this ridge. The capital road is where I join."),
        ],
        outro=[
            ("Half-Blood", "The ridge is quiet. The smith's stair is next, and your gauntlet knows the way."),
            ("Narrator", "You can walk this ridge again."),
        ],
    ),
    _ep(
        id=9,
        name="Smith's Stair",
        place="Smith's stair",
        theme="camp",
        heights=stair_rows(),
        blocked=[],
        slots=[(3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (4, 11), (7, 11)],
        must=["kairo"],
        recruit_before=["smith"],
        win="lord",
        enemies=[
            {
                "kind": "captain",
                "pos": (6, 1),
                "id": "stair_captain",
                "name": "Stair Captain",
                "hunt": True,
                "family": "sword",
                "hp": 44,
                "atk": 11,
                "defn": 5,
                "exp": 80,
                "stone": "cinder",
                "sprite": "bushi",
            },
            {"kind": "bushi", "pos": (4, 3)},
            {"kind": "bushi", "pos": (8, 3)},
            {"kind": "pawn", "pos": (5, 5)},
            {"kind": "pawn", "pos": (7, 6)},
        ],
        intro=[
            ("Smith", "I am Smith. The Stair Captain is the mark. He is not a lord. Issen still fells him."),
            ("Kairo", "When this stair is clear, the gauntlet can wake. That form spends half my skill points and fights without my orders."),
            ("Shio", "Then do not wake it until the captain is the only thing left that matters."),
        ],
        outro=[
            ("Smith", "The stair is ours. Oni-Wake is open. Three enemy turns, then you may only move."),
            ("Kairo", "I will not spend it on a pawn."),
            ("Narrator", "Oni-Wake can be used once each fight, and only by Kairo."),
        ],
    ),
    _ep(
        id=10,
        name="Cinder Bird Approach",
        place="Cinder Bird approach",
        theme="camp",
        heights=slope_rows(),
        blocked=corner_blocked(),
        slots=BOTTOM,
        must=["kairo"],
        enemies=[
            {"kind": "gunner", "pos": (2, 1)},
            {"kind": "gunner", "pos": (9, 1)},
            {"kind": "claw", "pos": (5, 2)},
            {"kind": "bushi", "pos": (4, 4)},
            {"kind": "pawn", "pos": (7, 5)},
        ],
        intro=[
            ("Gun-Chief", "Their guns hold the high step. A person in the line still stops the shot."),
            ("Kairo", "We climb the middle. Do not stand in his lane."),
            ("Narrator", "The nest beyond this slope has a lord. Issen will not fell that one."),
        ],
        outro=[
            ("Kairo", "The approach is quiet. The bird is next."),
            ("Narrator", "You can walk this slope again."),
        ],
    ),
    _ep(
        id=11,
        name="Cinder Bird Nest",
        place="Cinder Bird nest",
        theme="camp",
        heights=flat(band="1"),
        blocked=[(1, 1), (10, 1), (2, 8), (9, 8)],
        slots=BOTTOM,
        must=["kairo"],
        win="lord",
        enemies=[
            {
                "kind": "beast",
                "pos": (6, 2),
                "id": "cinder_bird",
                "name": "Cinder Bird",
                "hunt": True,
                "lord": True,
                "immune": True,
                "family": "sword",
                "hp": 56,
                "atk": 12,
                "defn": 5,
                "exp": 100,
                "sprite": "beast_bird",
            },
            {"kind": "claw", "pos": (3, 3)},
            {"kind": "claw", "pos": (9, 3)},
            {"kind": "pawn", "pos": (6, 5)},
        ],
        intro=[
            ("Kairo", "Cinder Bird is a lord. Issen does not fell a lord. A normal hit still lands."),
            ("Smith", "When the bird falls, the fight ends on the next turn. The rest can live."),
            ("Narrator", "Lords are worth 100 souls and two Void. The souls are not multiplied."),
        ],
        outro=[
            ("Kairo", "The bird is down. Its stance is attack: every ally gains 3 attack while it is set."),
            ("Narrator", "Only one stance can be on. White Fang is still there if you want the high ground instead."),
        ],
    ),
    _ep(
        id=12,
        name="Ash Factory",
        place="Ash factory",
        theme="factory",
        heights=flat(),
        blocked=[(1, 1), (2, 1), (10, 1), (1, 8), (10, 8), (5, 8)],
        slots=BOTTOM,
        must=["kairo"],
        enemies=[
            {"kind": "nest", "pos": (3, 3)},
            {"kind": "nest", "pos": (6, 2)},
            {"kind": "nest", "pos": (9, 4)},
            {"kind": "gunner", "pos": (4, 5), "recipe": "nest_gun"},
            {"kind": "pawn", "pos": (7, 6)},
            {"kind": "pawn", "pos": (3, 6)},
        ],
        intro=[
            ("Gun-Chief", "Three nests. They do not walk, and they drop no stone. A clear line still reaches them."),
            ("Kairo", "Break the nests, then the gunner. He carries a recipe."),
            ("Narrator", "A nest is worth experience and 10 souls. It cannot set Issen, and it cannot answer one."),
        ],
        outro=[
            ("Gun-Chief", "The factory is quiet. Nest Gun can be made when you have Bone and Cinder."),
            ("Kairo", "The hollow gate is next. A bow joins us there."),
            ("Narrator", "You can walk the factory again."),
        ],
    ),
    _ep(
        id=13,
        name="Hollow Gate",
        place="Hollow gate",
        theme="hollow",
        heights=flat(),
        blocked=corner_blocked() + [(5, 5), (6, 5)],
        slots=BOTTOM,
        must=["kairo"],
        recruit_before=["bow_saint"],
        enemies=[
            {"kind": "bushi", "pos": (4, 2)},
            {"kind": "bushi", "pos": (8, 2)},
            {"kind": "claw", "pos": (6, 3)},
            {"kind": "gunner", "pos": (3, 4)},
            {"kind": "pawn", "pos": (9, 6)},
        ],
        intro=[
            ("Bow-Saint", "I am Bow-Saint. An arrow is a straight line, like a gun. Sleep, poison, and paralysis replace the shot."),
            ("Kairo", "Sleep breaks when they are hit. Poison does not stop their turn. Paralysis does, and a hit does not clear it."),
            ("Narrator", "Hollow Depths opens after this gate. Floors 1 to 4. The road itself does not skip."),
        ],
        outro=[
            ("Bow-Saint", "The gate is quiet. The depths can be walked when you choose. The river coil is still the road."),
            ("Narrator", "Clearing a floor does not open the next story fight."),
        ],
    ),
    _ep(
        id=14,
        name="River Coil Approach",
        place="River Coil approach",
        theme="river",
        heights=flat(),
        blocked=river_blocked(),
        slots=BOTTOM,
        must=["kairo"],
        enemies=[
            {"kind": "bushi", "pos": (4, 2)},
            {"kind": "bushi", "pos": (7, 2)},
            {"kind": "gunner", "pos": (5, 1)},
            {"kind": "pawn", "pos": (3, 4)},
            {"kind": "pawn", "pos": (8, 4)},
            {"kind": "claw", "pos": (6, 3)},
        ],
        intro=[
            ("Spear-One", "Spears and guns along the water. Keep off their lines until we are close."),
            ("Kairo", "The nest beyond this is a lord again. Same rule as the bird."),
            ("Bow-Saint", "I can sleep the gunner if the lane is empty."),
        ],
        outro=[
            ("Kairo", "The approach is quiet. The coil is next."),
            ("Narrator", "You can walk this bank again."),
        ],
    ),
    _ep(
        id=15,
        name="River Coil Nest",
        place="River Coil nest",
        theme="river",
        heights=flat(),
        blocked=river_blocked(),
        slots=BOTTOM,
        must=["kairo"],
        win="lord",
        recruit_after=["coil_champion"],
        enemies=[
            {
                "kind": "beast",
                "pos": (6, 2),
                "id": "river_coil",
                "name": "River Coil",
                "hunt": True,
                "lord": True,
                "immune": True,
                "family": "spear",
                "hp": 58,
                "atk": 12,
                "defn": 5,
                "exp": 100,
                "sprite": "beast_coil",
            },
            {"kind": "bushi", "pos": (3, 3)},
            {"kind": "bushi", "pos": (8, 3)},
            {"kind": "gunner", "pos": (5, 5)},
        ],
        intro=[
            ("Kairo", "River Coil is the mark. A lord. Issen will not fell it. Spears reach two tiles."),
            ("Gun-Chief", "I will take the lane if you stay out of it."),
            ("Narrator", "When the coil falls, the fight ends on the next turn."),
        ],
        outro=[
            ("Coil-Champion", "I am Coil-Champion. The coil's stance lets spears and guns ignore 4 defense."),
            ("Kairo", "One stance. Choose it on the deploy screen."),
            ("Narrator", "The nest is quiet."),
        ],
    ),
    _ep(
        id=16,
        name="Rebel Ford",
        place="Rebel ford",
        theme="river",
        heights=flat(),
        blocked=river_blocked(),
        slots=[(2, 11), (3, 11), (4, 11), (5, 11), (8, 11), (9, 11), (3, 10), (8, 10)],
        must=["kairo"],
        recruit_before=["monk_spear"],
        win="lord",
        guests=[
            {
                "id": "daughter",
                "name": "Daughter",
                "sprite": "daughter",
                "pos": (6, 9),
                "hp": 30,
                "atk": 4,
                "defn": 2,
                "mov": 4,
                "family": "light_sword",
            }
        ],
        enemies=[
            {
                "kind": "lord",
                "pos": (6, 2),
                "id": "ford_father",
                "name": "The Father",
                "hunt": True,
                "lord": True,
                "immune": True,
                "family": "sword",
                "hp": 50,
                "atk": 12,
                "defn": 5,
                "exp": 100,
                "sprite": "lord",
            },
            {"kind": "pawn", "pos": (4, 4)},
            {"kind": "pawn", "pos": (8, 4)},
            {"kind": "bushi", "pos": (5, 3)},
            {"kind": "bushi", "pos": (7, 5)},
        ],
        intro=[
            ("Monk-Spear", "I am Monk-Spear. The Father is the mark. His daughter must live. If she falls, the march ends."),
            ("Kairo", "She has a gold dot, the same as I do. Pull her back. I will take the father."),
            ("Daughter", "I can step. I cannot hold them. Do not leave me in the middle."),
        ],
        outro=[
            ("Monk-Spear", "He is gone. She is standing. That is the only win I came for."),
            ("Kairo", "Then stay with the spears."),
            ("Narrator", "The ford is quiet."),
        ],
    ),
    _ep(
        id=17,
        name="Stone Shell Approach",
        place="Stone Shell approach",
        theme="camp",
        heights=slope_rows(),
        blocked=corner_blocked(),
        slots=BOTTOM,
        must=["kairo"],
        enemies=[
            {"kind": "claw", "pos": (3, 1)},
            {"kind": "claw", "pos": (8, 1)},
            {"kind": "bushi", "pos": (5, 2)},
            {"kind": "bushi", "pos": (6, 4)},
            {"kind": "pawn", "pos": (4, 3)},
        ],
        intro=[
            ("Kairo", "Another high slope. Their first hit from above still hurts. The shell itself is the next nest."),
            ("Stage-Man", "I will take the step before I spend Strongman."),
        ],
        outro=[
            ("Kairo", "The approach is quiet. The shell is next."),
            ("Narrator", "You can walk this slope again."),
        ],
    ),
    _ep(
        id=18,
        name="Stone Shell Nest",
        place="Stone Shell nest",
        theme="camp",
        heights=flat(band="1"),
        blocked=[(1, 2), (10, 2), (2, 7), (9, 7)],
        slots=BOTTOM,
        must=["kairo"],
        win="lord",
        recruit_after=["shell_champion"],
        enemies=[
            {
                "kind": "beast",
                "pos": (6, 2),
                "id": "stone_shell",
                "name": "Stone Shell",
                "hunt": True,
                "lord": True,
                "immune": True,
                "family": "spear",
                "hp": 64,
                "atk": 11,
                "defn": 8,
                "exp": 100,
                "sprite": "beast_shell",
            },
            {"kind": "bushi", "pos": (3, 4)},
            {"kind": "claw", "pos": (8, 4)},
            {"kind": "pawn", "pos": (6, 5)},
        ],
        intro=[
            ("Kairo", "Stone Shell is the mark. Heavy defense. A lord. Issen will not fell it."),
            ("Spear-One", "If the coil stance is on, a spear ignores 4 of that defense."),
            ("Narrator", "Floors 5 to 8 of the depths open after this nest. The road does not skip."),
        ],
        outro=[
            ("Shell-Champion", "I am Shell-Champion. The shell's stance halves the first hit each fighter takes in a round."),
            ("Kairo", "One stance. The others remain on the deploy screen."),
            ("Narrator", "The nest is quiet."),
        ],
    ),
    _ep(
        id=19,
        name="Fox Court",
        place="Fox court",
        theme="castle",
        heights=flat(band="1"),
        blocked=gate_blocked(),
        slots=[(2, 10), (3, 10), (5, 10), (6, 10), (8, 10), (9, 10), (3, 11), (8, 11)],
        must=["kairo"],
        win="lord",
        enemies=[
            {
                "kind": "lord",
                "pos": (6, 2),
                "id": "fox_minister",
                "name": "Fox-Minister",
                "hunt": True,
                "lord": True,
                "immune": True,
                "hp": 58,
                "atk": 13,
                "defn": 5,
                "exp": 110,
                "sprite": "lord",
            },
            {"kind": "pawn", "pos": (3, 4)},
            {"kind": "pawn", "pos": (9, 4)},
            {"kind": "bushi", "pos": (6, 5)},
            {"kind": "claw", "pos": (4, 6)},
        ],
        intro=[
            ("Kairo", "Fox-Minister is the mark. He does not join us. He is a lord."),
            ("Swallow", "He ignores Issen. Hit him with the blade itself."),
            ("Narrator", "When he falls, the court ends on the next turn."),
        ],
        outro=[
            ("Kairo", "The minister is gone. The capital road is next, and two people are waiting on it."),
            ("Narrator", "He did not join. You can walk the court again."),
        ],
    ),
    _ep(
        id=20,
        name="Capital Road",
        place="Capital road",
        theme="castle",
        heights=flat(band="1"),
        blocked=corner_blocked() + [(2, 2), (9, 2)],
        slots=BOTTOM,
        must=["kairo"],
        recruit_before=["dancer", "deserter"],
        enemies=[
            {"kind": "pawn", "pos": (3, 3)},
            {"kind": "bushi", "pos": (6, 2)},
            {"kind": "claw", "pos": (9, 3)},
            {"kind": "gunner", "pos": (5, 4)},
            {"kind": "bushi", "pos": (7, 5)},
            {"kind": "pawn", "pos": (4, 6)},
        ],
        intro=[
            ("Dancer", "I am Dancer. Sleep or confuse the one beside me. Sleep breaks when they are hit. Confuse does not."),
            ("Deserter", "I am Deserter. I can steal a stone or a recipe. Lords have nothing I can take."),
            ("Kairo", "The road is a rout. Clear them all. The lab is after this."),
        ],
        outro=[
            ("Dancer", "The road is quiet. I will stay behind the line."),
            ("Deserter", "If they carry a recipe, I will take it before they fall."),
            ("Narrator", "The glass lab is next. Something there sings once."),
        ],
    ),
    _ep(
        id=21,
        name="Glass Lab",
        place="Glass lab",
        theme="factory",
        heights=flat(),
        blocked=[(1, 1), (10, 1), (1, 10), (10, 10), (4, 7), (7, 7)],
        slots=BOTTOM,
        must=["kairo"],
        enemies=[
            {
                "kind": "lord",
                "pos": (6, 3),
                "id": "glass_surgeon",
                "name": "Glass-Surgeon",
                "lord": True,
                "immune": True,
                "chant": "once",
                "hp": 48,
                "atk": 11,
                "defn": 4,
                "exp": 110,
                "sprite": "lord",
            },
            {"kind": "pawn", "pos": (3, 2)},
            {"kind": "pawn", "pos": (9, 2)},
            {"kind": "claw", "pos": (4, 5)},
            {"kind": "claw", "pos": (8, 5)},
            {"kind": "gunner", "pos": (6, 1)},
        ],
        intro=[
            ("Kairo", "This is a rout. All of them, including Glass-Surgeon. He is a lord."),
            ("Shio", "At half health he chants once, on a small ring. The red tiles empty on his next turn unless he is hit."),
            ("Narrator", "Any real hit breaks the chant. Issen does not, because a lord ignores it and the blade still connects."),
        ],
        outro=[
            ("Kairo", "The lab is quiet. Remember the ring. The throne will use a wider one."),
            ("Narrator", "You can walk the lab again."),
        ],
    ),
    _ep(
        id=22,
        name="Throne, First Skin",
        place="Throne, first skin",
        theme="throne",
        heights=flat(band="2"),
        blocked=[(2, 2), (9, 2), (2, 8), (9, 8)],
        slots=BOTTOM,
        must=["kairo"],
        win="lord",
        enemies=[
            {
                "kind": "lord",
                "pos": (6, 2),
                "id": "kurogane",
                "name": "Kurogane",
                "hunt": True,
                "lord": True,
                "immune": True,
                "hp": 72,
                "atk": 14,
                "defn": 6,
                "exp": 120,
                "sprite": "lord",
            },
            {"kind": "bushi", "pos": (3, 3)},
            {"kind": "bushi", "pos": (9, 3)},
            {"kind": "claw", "pos": (5, 4)},
            {"kind": "claw", "pos": (7, 4)},
            {"kind": "gunner", "pos": (6, 6)},
        ],
        intro=[
            ("Kairo", "Kurogane. First skin. He is the mark, and he is a lord. Issen will not fell him."),
            ("Shio", "He does not chant in this skin. Save your strength for the one that does."),
            ("Narrator", "Floors 9 to 12 of the depths open after this throne. Floor 12 brings Soot-Child, still at level 1."),
        ],
        outro=[
            ("Kairo", "The first skin is gone. The true one is still on the throne."),
            ("Narrator", "You can walk this throne again."),
        ],
    ),
    _ep(
        id=23,
        name="Throne, True Skin",
        place="Throne, true skin",
        theme="throne",
        heights=flat(band="2"),
        blocked=[(2, 2), (9, 2), (1, 6), (10, 6)],
        slots=BOTTOM,
        must=["kairo"],
        win="lord",
        enemies=[
            {
                "kind": "lord",
                "pos": (6, 2),
                "id": "kurogane_true",
                "name": "Kurogane",
                "hunt": True,
                "lord": True,
                "immune": True,
                "chant": "full",
                "hp": 88,
                "atk": 16,
                "defn": 7,
                "exp": 140,
                "sprite": "lord",
            },
            {"kind": "claw", "pos": (4, 4)},
            {"kind": "claw", "pos": (8, 4)},
            {"kind": "bushi", "pos": (6, 5)},
        ],
        intro=[
            ("Kairo", "True skin. He is the mark. Above half health, if three of us stand in a wide ring he can see, he chants."),
            ("Shio", "Spread out. A hit breaks the chant. Standing together in that ring does not."),
            ("Narrator", "On his next turn the ring empties. Anyone still inside falls, including Kairo."),
        ],
        outro=[
            ("Kairo", "The throne is empty. The courtyard is all that is left, and there is no one left to fight."),
            ("Shio", "Then we walk out."),
            ("Narrator", "You can walk this throne again."),
        ],
    ),
    _ep(
        id=24,
        name="Courtyard",
        place="Courtyard",
        theme="castle",
        heights=flat(8, "1"),
        blocked=[],
        slots=[],
        must=["kairo"],
        battle=False,
        enemies=[],
        intro=[
            ("Narrator", "The courtyard is quiet. There is no one left to fight."),
            ("Kairo", "The gauntlet cracks. The warmth leaves it."),
            ("Shio", "Then we go home, if the village will have us."),
            ("Narrator", "The road is walked. Every level can be walked again."),
        ],
        outro=[],
    ),
]


def _depths() -> list[dict]:
    positions = [(2, 2), (5, 2), (8, 2), (3, 4), (7, 4), (5, 6), (2, 5), (9, 5)]
    floors = []
    for number in range(1, 13):
        if number <= 4:
            stats = {"hp": 20 + number, "atk": 8, "defn": 2, "exp": 40}
            mix = ["pawn", "bushi", "claw", "pawn"]
        elif number <= 8:
            stats = {"hp": 30 + number, "atk": 10, "defn": 3, "exp": 55}
            mix = ["bushi", "claw", "gunner", "bushi"]
        else:
            stats = {"hp": 40 + number, "atk": 12, "defn": 4, "exp": 70, "stone": "void"}
            mix = ["claw", "bushi", "gunner", "claw"]
        count = 3 + number // 4
        enemies = []
        for index in range(count):
            spec = {"kind": mix[index % len(mix)], "pos": positions[index]}
            spec.update(stats)
            enemies.append(spec)
        floors.append(
            {
                "floor": number,
                "name": "Hollow Stone",
                "theme": "hollow",
                "heights": flat(),
                "blocked": corner_blocked(),
                "slots": [(2, 10), (3, 10), (5, 10), (6, 10), (8, 10), (9, 10), (4, 11), (7, 11)],
                "enemies": enemies,
            }
        )
    return floors


DEPTHS = _depths()
