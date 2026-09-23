"""Party, workshop, and the two fights in v0.0.1."""

from __future__ import annotations

import json
import random
from pathlib import Path

from ashgauntlet.data import (
    BODIES,
    ENEMIES,
    GEAR,
    RECIPES,
    SKILLS,
    STONES,
    episode,
    gear_bonus,
    grid_from_rows,
    next_enhance_cost,
)
from ashgauntlet.rules import Battle, Unit


class Gear:
    def __init__(self, uid: int, kind: str, plus: int = 0, owner: str | None = None):
        self.uid = uid
        self.kind = kind
        self.plus = plus
        self.owner = owner


class Save:
    def __init__(self):
        self.souls = 0
        self.stones = {"ash": 0, "bone": 0, "cinder": 0, "void": 0}
        self.recipes = []
        self.gear = []
        self.herbs = 0
        self.roster = []
        self.units = {}
        self.cleared = []
        self.next_episode = 1
        self._next_uid = 1

    def to_dict(self) -> dict:
        return {
            "version": "0.0.1",
            "souls": self.souls,
            "stones": dict(self.stones),
            "recipes": list(self.recipes),
            "gear": [
                {"uid": g.uid, "kind": g.kind, "plus": g.plus, "owner": g.owner}
                for g in self.gear
            ],
            "herbs": self.herbs,
            "roster": list(self.roster),
            "units": {key: dict(value) for key, value in self.units.items()},
            "cleared": list(self.cleared),
            "next_episode": self.next_episode,
            "next_uid": self._next_uid,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Save":
        save = cls()
        save.souls = int(data.get("souls", 0))
        stones = data.get("stones", {})
        for key in save.stones:
            save.stones[key] = int(stones.get(key, 0))
        save.recipes = list(data.get("recipes", []))
        save.herbs = int(data.get("herbs", 0))
        save.roster = list(data.get("roster", []))
        save.units = {key: dict(value) for key, value in data.get("units", {}).items()}
        save.cleared = list(data.get("cleared", []))
        save.next_episode = int(data.get("next_episode", 1))
        save._next_uid = int(data.get("next_uid", 1))
        for raw in data.get("gear", []):
            save.gear.append(Gear(int(raw["uid"]), raw["kind"], int(raw.get("plus", 0)), raw.get("owner")))
        return save

    def write(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "Save | None":
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        if data.get("version") != "0.0.1":
            return None
        return cls.from_dict(data)

    def recruit(self, body_id: str) -> None:
        if body_id in self.roster:
            return
        self.roster.append(body_id)
        self.units[body_id] = {"level": 1, "exp": 0}
        self.add_gear(BODIES[body_id]["start_weapon"], owner=body_id)

    def add_gear(self, kind: str, owner: str | None = None, plus: int = 0) -> Gear:
        gear = Gear(self._next_uid, kind, plus, owner)
        self._next_uid += 1
        self.gear.append(gear)
        return gear

    def gear_by(self, uid: int) -> Gear | None:
        for gear in self.gear:
            if gear.uid == uid:
                return gear
        return None

    def equipped(self, body_id: str, slot: str) -> Gear | None:
        found = [g for g in self.gear if g.owner == body_id and GEAR[g.kind]["slot"] == slot]
        return found[0] if found else None

    def gear_choices(self, body_id: str, slot: str) -> list[Gear]:
        family = BODIES[body_id]["family"]
        choices = []
        for gear in self.gear:
            meta = GEAR[gear.kind]
            if meta["slot"] != slot:
                continue
            if slot == "weapon" and meta["family"] != family:
                continue
            if gear.owner not in (None, body_id):
                continue
            choices.append(gear)
        return choices

    def equip(self, body_id: str, uid: int) -> None:
        gear = self.gear_by(uid)
        if gear is None:
            return
        slot = GEAR[gear.kind]["slot"]
        for other in self.gear:
            if other.owner == body_id and other.uid != gear.uid and GEAR[other.kind]["slot"] == slot:
                other.owner = None
        gear.owner = body_id

    def unequip_slot(self, body_id: str, slot: str) -> None:
        for gear in self.gear:
            if gear.owner == body_id and GEAR[gear.kind]["slot"] == slot:
                gear.owner = None

    def known(self, recipe_id: str) -> bool:
        return recipe_id in self.recipes

    def can_craft(self, recipe_id: str) -> bool:
        if recipe_id not in self.recipes:
            return False
        cost = RECIPES[recipe_id]["stones"]
        return all(self.stones.get(key, 0) >= amount for key, amount in cost.items())

    def craft(self, recipe_id: str) -> bool:
        if not self.can_craft(recipe_id):
            return False
        for key, amount in RECIPES[recipe_id]["stones"].items():
            self.stones[key] -= amount
        self.add_gear(RECIPES[recipe_id]["gear"], owner=None)
        return True

    def enhance(self, uid: int) -> bool:
        gear = self.gear_by(uid)
        if gear is None:
            return False
        cost = next_enhance_cost(gear.kind, gear.plus)
        if cost is None or self.souls < cost:
            return False
        self.souls -= cost
        gear.plus += 1
        return True

    def prepare_episode(self, episode_id: int) -> None:
        for body_id in episode(episode_id)["recruit_before"]:
            self.recruit(body_id)
        if self.herbs < 4:
            self.herbs += 2

    def grant_exp(self, exp_map: dict) -> list[str]:
        notes = []
        for body_id, amount in exp_map.items():
            if body_id not in self.units:
                continue
            record = self.units[body_id]
            record["exp"] += int(amount)
            body = BODIES[body_id]
            while record["exp"] >= 100 and record["level"] < 40:
                record["exp"] -= 100
                record["level"] += 1
                notes.append(f"{body['name']} reaches level {record['level']}.")
        return notes

    def finish_victory(self, episode_id: int, battle: Battle) -> list[str]:
        for body_id in episode(episode_id)["recruit_after"]:
            self.recruit(body_id)
        notes = []
        for recipe_id in battle.loot_recipes:
            if recipe_id not in self.recipes and recipe_id in RECIPES:
                self.recipes.append(recipe_id)
                notes.append(f"Recipe learned: {RECIPES[recipe_id]['name']}.")
        notes.extend(self.grant_exp(battle.loot_exp))
        self.souls += battle.loot_souls
        for stone in battle.loot_stones:
            self.stones[stone] = self.stones.get(stone, 0) + 1
        if episode_id not in self.cleared:
            self.cleared.append(episode_id)
        self.next_episode = max(self.next_episode, episode_id + 1)
        if battle.loot_souls:
            notes.append(
                f"Souls kept: {battle.loot_souls}. Souls only raise a piece you already own."
            )
        if battle.loot_stones:
            names = [STONES[stone]["name"] if stone in STONES else stone for stone in battle.loot_stones]
            notes.append(
                "Stones kept: "
                + ", ".join(names)
                + ". Stones make a new piece in the workshop. Pawns drop Ash. Spear fighters drop Bone."
            )
        return notes


def new_game() -> Save:
    save = Save()
    save.recruit("kairo")
    save.recruit("sword_two")
    return save


def default_order(save: Save, ep: dict) -> list[str]:
    must = [body for body in ep["must"] if body in save.roster]
    rest = [body for body in save.roster if body not in must]
    return (must + rest)[: len(ep["slots"])]


def default_items(save: Save, order: list[str]) -> dict:
    plan = {body: [None, None] for body in order}
    stock = save.herbs
    sequence = sorted(order, key=lambda body: (body != "shio", body))
    for slot in (0, 1):
        for body in sequence:
            if stock <= 0:
                return plan
            plan[body][slot] = "herb"
            stock -= 1
    return plan


def _piece_name(gear: Gear | None) -> str:
    if gear is None:
        return ""
    return f"{GEAR[gear.kind]['name']} +{gear.plus}"


def _skills_for(body_id: str, level: int, gears: list[Gear | None]) -> list[str]:
    known = []
    for skill_id, needed in BODIES[body_id]["skills"]:
        if level >= needed and skill_id in SKILLS and skill_id not in known:
            known.append(skill_id)
    for gear in gears:
        if gear is None:
            continue
        meta = GEAR[gear.kind]
        gate = meta["gate"]
        skill_id = meta["skill"]
        if gate and gear.plus >= gate and skill_id and skill_id in SKILLS and skill_id not in known:
            known.append(skill_id)
    return known


def materialize(save: Save, body_id: str, pos, lose_flag: bool = False) -> Unit:
    body = BODIES[body_id]
    record = save.units[body_id]
    steps = record["level"] - 1
    hp_g, sp_g, atk_g, def_g = body["growth"]
    weapon = save.equipped(body_id, "weapon")
    armor = save.equipped(body_id, "armor")
    charm = save.equipped(body_id, "accessory")
    weapon_meta = GEAR[weapon.kind] if weapon else None
    return Unit(
        id=body_id,
        name=body["name"],
        side="player",
        sprite=body_id,
        pos=tuple(pos),
        hp=body["hp"] + hp_g * steps,
        max_hp=body["hp"] + hp_g * steps,
        sp=body["sp"] + sp_g * steps,
        max_sp=body["sp"] + sp_g * steps,
        atk=body["atk"] + atk_g * steps,
        defn=body["defn"] + def_g * steps,
        mov=body["mov"],
        weapon_family=weapon_meta["family"] if weapon_meta else None,
        weapon_atk=gear_bonus(weapon.kind, weapon.plus) if weapon else 0,
        armor_def=gear_bonus(armor.kind, armor.plus) if armor else 0,
        acc_def=gear_bonus(charm.kind, charm.plus) if charm else 0,
        weapon_name=_piece_name(weapon) or "Empty hands",
        armor_name=_piece_name(armor),
        charm_name=_piece_name(charm),
        weapon_kind=weapon.kind if weapon else None,
        weapon_plus=weapon.plus if weapon else 0,
        armor_kind=armor.kind if armor else None,
        armor_plus=armor.plus if armor else 0,
        charm_kind=charm.kind if charm else None,
        charm_plus=charm.plus if charm else 0,
        level=record["level"],
        exp=record["exp"],
        skills=_skills_for(body_id, record["level"], [weapon, armor, charm]),
        lose_flag=lose_flag or body_id == "kairo",
    )


def fresh_unit(body_id: str, pos, lose_flag: bool = False) -> Unit:
    body = BODIES[body_id]
    meta = GEAR[body["start_weapon"]]
    return Unit(
        id=body_id,
        name=body["name"],
        side="player",
        sprite=body_id,
        pos=tuple(pos),
        hp=body["hp"],
        max_hp=body["hp"],
        sp=body["sp"],
        max_sp=body["sp"],
        atk=body["atk"],
        defn=body["defn"],
        mov=body["mov"],
        weapon_family=meta["family"],
        weapon_name=f"{meta['name']} +0",
        weapon_kind=body["start_weapon"],
        weapon_plus=0,
        armor_name="",
        charm_name="",
        level=1,
        exp=0,
        skills=_skills_for(body_id, 1, []),
        lose_flag=lose_flag or body_id == "kairo",
    )


def make_enemy(spec: dict) -> Unit:
    kind = ENEMIES[spec["kind"]]
    return Unit(
        id=f"{spec['kind']}{spec['pos']}",
        name=kind["name"],
        side="enemy",
        sprite=kind["sprite"],
        pos=tuple(spec["pos"]),
        hp=kind["hp"],
        max_hp=kind["hp"],
        sp=kind["sp"],
        max_sp=kind["sp"],
        atk=kind["atk"],
        defn=kind["defn"],
        mov=kind["mov"],
        weapon_family=kind["family"],
        skills=list(kind["skills"]),
        stone=kind["stone"],
        recipe=spec.get("recipe"),
        exp_value=kind["exp"],
    )


def make_guest(save: Save, body_id: str, pos, lose_flag: bool) -> Unit:
    if body_id in save.roster:
        return materialize(save, body_id, pos, lose_flag)
    return fresh_unit(body_id, pos, lose_flag)


def build_battle(save: Save, episode_id: int, order: list[str], items: dict, rng=None) -> Battle:
    ep = episode(episode_id)
    heights, width, height = grid_from_rows(ep["heights"])
    units = []
    for index, body_id in enumerate(order):
        unit = materialize(save, body_id, ep["slots"][index], lose_flag=(body_id == "kairo"))
        unit.items = list(items.get(body_id, [None, None]))
        units.append(unit)
    for spec in ep["enemies"]:
        units.append(make_enemy(spec))
    reinforcements = []
    for spec in ep["reinforcements"]:
        guest = make_guest(save, spec["body"], spec["pos"], spec.get("lose_flag", False))
        if spec.get("gift_herb") and spec["body"] not in save.roster:
            guest.items = ["herb", None]
        reinforcements.append({"round": spec["round"], "pos": tuple(spec["pos"]), "unit": guest})
    battle = Battle(width, height, heights, ep["blocked"], units, reinforcements, rng or random.Random())
    battle.theme = ep["theme"]
    battle.title = ep["name"]
    battle.episode_id = episode_id
    return battle
