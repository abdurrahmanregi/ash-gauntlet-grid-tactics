"""Window for Ash-Gauntlet Tactics. Mouse only, aside from the arrow keys."""

from __future__ import annotations

import ctypes
import random
import sys

import pygame

from ashgauntlet.campaign import (
    Save,
    build_battle,
    default_items,
    default_order,
    new_game,
)
from ashgauntlet.data import (
    BODIES,
    EPISODES,
    GEAR,
    ISSEN_FAMILIES,
    RECIPES,
    SKILLS,
    craft_line,
    episode,
    next_enhance_cost,
    raise_line,
)
from ashgauntlet.paths import bundle_root, user_root

WIDTH, HEIGHT = 1280, 720
HW, HH = 40, 20
BG = (22, 18, 16)
PANEL = (36, 30, 28)
TEXT = (243, 236, 226)
MUTED = (176, 164, 150)
ORANGE = (224, 122, 61)
GOLD = (224, 184, 96)
HP_COLOR = (72, 168, 96)
SP_COLOR = (72, 132, 198)
VILLAGE = {
    0: ((78, 108, 74), (54, 74, 52), (66, 90, 62)),
    1: ((132, 118, 92), (92, 80, 62), (112, 98, 76)),
    2: ((168, 154, 132), (116, 104, 88), (142, 128, 108)),
}
CEDAR = {
    0: ((58, 82, 56), (40, 58, 40), (48, 68, 46)),
    1: ((108, 94, 68), (74, 64, 46), (90, 78, 56)),
    2: ((148, 144, 134), (98, 96, 90), (122, 118, 110)),
}
def closest_diamond(mx, my, diamonds):
    """Return the tile whose ground diamond contains the point.

    diamonds is (tile, center_x, center_y). A taller picture must not decide
    the click: the front fighter covers the tiles behind them.
    """
    best = None
    best_key = None
    for tile, cx, cy in diamonds:
        dist = abs(mx - cx) / HW + abs(my - cy) / HH
        if dist <= 1:
            key = (dist, -(tile[0] + tile[1]))
            if best_key is None or key < best_key:
                best = tile
                best_key = key
    return best


FALLBACK_COLORS = {
    "kairo": (214, 122, 64),
    "shio": (226, 198, 164),
    "sword_two": (108, 128, 158),
    "spear_one": (86, 138, 92),
    "swallow": (64, 148, 146),
    "pawn": (132, 102, 172),
    "bushi": (96, 70, 150),
}
SPEAKER_SPRITE = {
    "Kairo": "kairo",
    "Shio": "shio",
    "Sword-Two": "sword_two",
    "Spear-One": "spear_one",
    "Swallow": "swallow",
}


def wrap(font, text, width):
    words = text.split()
    if not words:
        return [""]
    lines = []
    current = ""
    for word in words:
        trial = word if not current else current + " " + word
        if font.size(trial)[0] <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def blit_lines(surface, font, lines, color, x, y, gap=2):
    step = font.get_height() + gap
    for index, line in enumerate(lines):
        image = font.render(line, True, color)
        surface.blit(image, (x, y + index * step))
    return len(lines) * step


class Button:
    def __init__(self, rect, label, callback, enabled=True):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.callback = callback
        self.enabled = enabled

    def draw(self, surface, font):
        hovered = self.enabled and self.rect.collidepoint(pygame.mouse.get_pos())
        fill = (120, 74, 48) if hovered else (70, 48, 36)
        if not self.enabled:
            fill = (48, 42, 40)
        pygame.draw.rect(surface, fill, self.rect, border_radius=8)
        pygame.draw.rect(surface, (224, 170, 120) if self.enabled else (90, 80, 72), self.rect, 2, border_radius=8)
        color = TEXT if self.enabled else (140, 130, 120)
        image = font.render(self.label, True, color)
        surface.blit(image, image.get_rect(center=self.rect.center))

    def hit(self, pos) -> bool:
        return self.enabled and self.rect.collidepoint(pos)


class Assets:
    def __init__(self):
        self.sprites = {}
        self.props = {}
        self.fx = {}
        root = bundle_root() / "assets"
        self._load(root / "sprites", self.sprites, 120)
        self._load(root / "props", self.props, 110)
        self._load(root / "fx", self.fx, 78)
        if "gauntlet" in self.props:
            image = self.props["gauntlet"]
            scale = 72 / image.get_height()
            self.props["gauntlet"] = pygame.transform.smoothscale(
                image, (max(1, int(image.get_width() * scale)), 72)
            )

    def _load(self, folder, dest, height):
        if not folder.exists():
            return
        for path in folder.glob("*.png"):
            image = pygame.image.load(str(path)).convert_alpha()
            scale = height / image.get_height()
            size = (max(1, int(image.get_width() * scale)), height)
            dest[path.stem] = pygame.transform.smoothscale(image, size)


class Game:
    def __init__(self):
        self._dpi()
        pygame.init()
        pygame.display.set_caption("Ash-Gauntlet Tactics")
        self.canvas = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("segoeui", 20)
        self.font_sm = pygame.font.SysFont("segoeui", 16)
        self.font_b = pygame.font.SysFont("segoeuibold", 22)
        self.font_lg = pygame.font.SysFont("segoeuibold", 40)
        self.font_xl = pygame.font.SysFont("segoeuibold", 54)
        self.assets = Assets()
        self.fallbacks = {}
        self.widgets = []
        self.mode = "title"
        self.running = True
        self.save_path = user_root() / "save.json"
        self.save = Save.load(self.save_path)
        self.confirm_new = False
        self.pending = None
        self.toast = ""
        self.toast_t = 0
        self.lines = []
        self.line_i = 0
        self.after_lines = "deploy"
        self.ep_id = 1
        self.order = []
        self.item_plan = {}
        self.deploy_focus = "kairo"
        self.battle = None
        self.snap = None
        self.sel = None
        self.preview = None
        self.aim = None
        self.anims = []
        self.override = {}
        self.dying = {}
        self.floaters = []
        self.cam = [0, 0]
        self.resolved = False
        self.result_title = ""
        self.result_notes = []
        self.banner = ""
        self.banner_t = 0
        if self.assets.props.get("gauntlet"):
            pygame.display.set_icon(pygame.transform.smoothscale(self.assets.props["gauntlet"], (32, 32)))

    def _dpi(self):
        if sys.platform != "win32":
            return
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

    def sprite(self, key):
        image = self.assets.sprites.get(key) or self.assets.props.get(key)
        if image is not None:
            return image
        if key not in self.fallbacks:
            color = FALLBACK_COLORS.get(key, (180, 160, 140))
            surf = pygame.Surface((70, 108), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, color, (8, 4, 54, 50))
            pygame.draw.rect(surf, color, (20, 50, 30, 42), border_radius=10)
            pygame.draw.circle(surf, (40, 30, 28), (26, 24), 3)
            pygame.draw.circle(surf, (40, 30, 28), (44, 24), 3)
            self.fallbacks[key] = surf
        return self.fallbacks[key]

    def loop(self):
        while self.running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.handle(event)
            self.update()
            self.draw()
        pygame.quit()

    def handle(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
            if self.mode == "story":
                self.advance_story()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for widget in self.widgets:
                if widget.hit(event.pos):
                    widget.callback()
                    return
            self.click(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.mode == "battle":
                if self.aim:
                    self.aim = None
                else:
                    self.sel = None
                    self.preview = None

    def update(self):
        if self.toast_t > 0:
            self.toast_t -= 1
        if self.banner_t > 0:
            self.banner_t -= 1
        for gid in list(self.dying):
            self.dying[gid] -= 1
            if self.dying[gid] <= 0:
                del self.dying[gid]
        self.floaters = [item for item in self.floaters if item["life"] > 0]
        for item in self.floaters:
            item["y"] -= 0.7
            item["life"] -= 1
        if self.mode == "battle" and self.battle:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.cam[0] += 6
            if keys[pygame.K_RIGHT]:
                self.cam[0] -= 6
            if keys[pygame.K_UP]:
                self.cam[1] += 6
            if keys[pygame.K_DOWN]:
                self.cam[1] -= 6
            self.cam[0] = max(-240, min(240, self.cam[0]))
            self.cam[1] = max(-180, min(180, self.cam[1]))
            if self.anims:
                self.tick_anim()
                return
            if self.battle.outcome and not self.resolved:
                self.open_results()
                return
            if self.battle.phase == "enemy" and not self.battle.outcome:
                self.enqueue(self.battle.enemy_step())

    def say(self, text):
        self.toast = text
        self.toast_t = 160

    def click(self, pos):
        if self.mode == "story":
            self.advance_story()
        elif self.mode == "battle":
            self.click_battle(pos)

    def draw(self):
        self.widgets = []
        self.canvas.fill(BG)
        draw = {
            "title": self.draw_title,
            "help": self.draw_help,
            "story": self.draw_story,
            "deploy": self.draw_deploy,
            "battle": self.draw_battle,
            "results": self.draw_results,
            "workshop": self.draw_workshop,
            "world": self.draw_world,
        }[self.mode]
        draw()
        if self.toast_t > 0 and self.mode in ("battle", "deploy", "workshop"):
            bar = pygame.Rect(24, HEIGHT - 46, 860, 32)
            pygame.draw.rect(self.canvas, (48, 28, 24), bar, border_radius=6)
            self.canvas.blit(self.font.render(self.toast, True, GOLD), (36, HEIGHT - 42))
        pygame.display.flip()

    def add_button(self, rect, label, callback, enabled=True):
        button = Button(rect, label, callback, enabled)
        self.widgets.append(button)
        button.draw(self.canvas, self.font)
        return button

    def draw_title(self):
        self.canvas.blit(self.sprite("kairo"), (120, 250))
        self.canvas.blit(self.sprite("shio"), (250, 280))
        title = self.font_xl.render("ASH-GAUNTLET", True, TEXT)
        sub = self.font_lg.render("TACTICS", True, ORANGE)
        self.canvas.blit(title, (460, 150))
        self.canvas.blit(sub, (460, 214))
        blurb = "Aim the diamond at their feet. Overlapping pictures do not take the click."
        self.canvas.blit(self.font.render(blurb, True, MUTED), (460, 280))
        self.canvas.blit(self.font_sm.render("v0.0.1  ·  the first march", True, MUTED), (460, 314))
        label = "Erase the saved march?" if self.confirm_new else "Begin the march"
        y = 380
        self.add_button((460, y, 320, 52), label, self.begin)
        y += 68
        if self.save and not self.confirm_new:
            self.add_button((460, y, 320, 52), "Continue", self.continue_game)
            y += 68
        self.add_button((460, y, 320, 52), "How to play", lambda: self.set_mode("help"))
        y += 68
        self.add_button((460, y, 320, 52), "Quit", self.stop)

    def draw_help(self):
        self.canvas.blit(self.font_lg.render("How a fight works", True, TEXT), (80, 48))
        lines = [
            "1. A bright diamond follows the pointer. That diamond is the tile you use.",
            "2. Point it at a fighter's feet and click. Rings stay visible when pictures pile up. Blue tiles are steps. Kairo always has to go.",
            "3. Red diamonds can be struck. Click the diamond on that enemy's tile, not the picture covering it.",
            "4. The buttons on the right are skills, herbs, Issen, and Wait. Heal works on that fighter or on a friend on the next tile. A herb does too.",
            "5. Issen means you only step and set it. The next sword, spear, or axe that swings at that fighter misses, and the attacker falls.",
            "6. Low, mid, and high ground are drawn as steps. A two-step gap blocks walking and striking.",
            "7. After the fight, stones make gear and souls raise it. Nothing is bought with coins.",
            "8. If Kairo falls, the fight is lost. On the first map, Shio is the same once she arrives.",
        ]
        y = 130
        for line in lines:
            y += blit_lines(self.canvas, self.font, wrap(self.font, line, 1000), TEXT, 80, y, 4) + 16
        self.add_button((80, 640, 220, 48), "Back", lambda: self.set_mode("title"))

    def set_mode(self, mode):
        self.mode = mode
        self.confirm_new = False
        self.pending = None

    def stop(self):
        self.running = False

    def begin(self):
        if self.save and not self.confirm_new:
            self.confirm_new = True
            return
        self.save = new_game()
        self.confirm_new = False
        self.open_episode(1)

    def continue_game(self):
        loaded = Save.load(self.save_path)
        if loaded is None:
            self.say("No saved march.")
            return
        self.save = loaded
        if self.save.cleared:
            self.mode = "world"
        else:
            self.open_episode(self.save.next_episode)

    def open_episode(self, episode_id):
        self.ep_id = episode_id
        self.save.prepare_episode(episode_id)
        self.save.write(self.save_path)
        ep = episode(episode_id)
        self.lines = list(ep["intro"])
        self.line_i = 0
        self.after_lines = "deploy"
        self.mode = "story"
        self.prepare_deploy()

    def prepare_deploy(self):
        ep = episode(self.ep_id)
        self.order = default_order(self.save, ep)
        self.item_plan = default_items(self.save, self.order)
        self.deploy_focus = self.order[0]

    def advance_story(self):
        if self.line_i < len(self.lines) - 1:
            self.line_i += 1
            return
        self.mode = self.after_lines

    def draw_story(self):
        speaker, text = self.lines[self.line_i]
        card = pygame.Rect(140, 160, 1000, 360)
        pygame.draw.rect(self.canvas, PANEL, card, border_radius=12)
        key = SPEAKER_SPRITE.get(speaker)
        if key:
            self.canvas.blit(self.sprite(key), (170, 190))
            text_x = 320
        else:
            text_x = 180
        name_color = ORANGE if speaker != "Narrator" else GOLD
        self.canvas.blit(self.font_b.render(speaker, True, name_color), (text_x, 200))
        blit_lines(self.canvas, self.font_lg, wrap(self.font_lg, text, 760 if key else 900), TEXT, text_x, 260)
        self.canvas.blit(self.font_sm.render("Click to continue", True, MUTED), (180, 470))

    def draw_deploy(self):
        ep = episode(self.ep_id)
        self.canvas.blit(self.font_lg.render(ep["name"], True, TEXT), (40, 24))
        self.canvas.blit(self.font.render("Choose who walks out. Kairo is required.", True, MUTED), (40, 78))
        self.canvas.blit(self.font_b.render("Going", True, ORANGE), (40, 120))
        y = 160
        for index, body_id in enumerate(self.order):
            self._deploy_row(body_id, index, y, going=True)
            y += 58
        self.canvas.blit(self.font_b.render("Staying back", True, MUTED), (40, y + 8))
        y += 48
        for body_id in self.save.roster:
            if body_id in self.order:
                continue
            self.add_button((40, y, 220, 40), BODIES[body_id]["name"], lambda b=body_id: self.add_deploy(b))
            y += 48
        self._draw_kit(ep)
        self.add_button((900, 650, 340, 48), "Start the fight", self.start_battle)

    def _deploy_row(self, body_id, index, y, going):
        name = BODIES[body_id]["name"]
        locked = body_id in episode(self.ep_id)["must"]
        self.add_button((40, y, 210, 44), name, lambda b=body_id: self.focus(b))
        if index > 0:
            self.add_button((260, y, 64, 44), "Up", lambda i=index: self.move_order(i, -1))
        if index < len(self.order) - 1:
            self.add_button((332, y, 80, 44), "Down", lambda i=index: self.move_order(i, 1))
        if not locked:
            self.add_button((420, y, 90, 44), "Bench", lambda b=body_id: self.bench(b))

    def focus(self, body_id):
        self.deploy_focus = body_id

    def move_order(self, index, step):
        other = index + step
        if other < 0 or other >= len(self.order):
            return
        self.order[index], self.order[other] = self.order[other], self.order[index]

    def bench(self, body_id):
        if body_id in episode(self.ep_id)["must"]:
            self.say("They have to come on this march.")
            return
        self.order = [body for body in self.order if body != body_id]
        self.item_plan.pop(body_id, None)
        if self.deploy_focus == body_id and self.order:
            self.deploy_focus = self.order[0]

    def add_deploy(self, body_id):
        ep = episode(self.ep_id)
        if len(self.order) >= len(ep["slots"]):
            self.say(f"This map only has room for {len(ep['slots'])}.")
            return
        self.order.append(body_id)
        self.item_plan[body_id] = [None, None]
        self.deploy_focus = body_id

    def _draw_kit(self, ep):
        body_id = self.deploy_focus if self.deploy_focus in self.order else self.order[0]
        self.deploy_focus = body_id
        body = BODIES[body_id]
        panel = pygame.Rect(820, 24, 430, 600)
        pygame.draw.rect(self.canvas, PANEL, panel, border_radius=12)
        self.canvas.blit(self.sprite(body_id), (840, 40))
        self.canvas.blit(self.font_b.render(body["name"], True, ORANGE), (980, 50))
        self.canvas.blit(self.font_sm.render(body["family"].replace("_", " "), True, MUTED), (980, 82))
        weapon = self.save.equipped(body_id, "weapon")
        armor = self.save.equipped(body_id, "armor")
        charm = self.save.equipped(body_id, "accessory")
        self._cycle_row(200, "Weapon", self._gear_label(weapon), lambda b=body_id: self.cycle(b, "weapon", 1))
        self._cycle_row(276, "Armor", self._gear_label(armor) if armor else "None", lambda b=body_id: self.cycle(b, "armor", 1))
        self._cycle_row(352, "Charm", self._gear_label(charm) if charm else "None", lambda b=body_id: self.cycle(b, "accessory", 1))
        slots = self.item_plan.setdefault(body_id, [None, None])
        for index in (0, 1):
            label = "Herb" if slots[index] == "herb" else "Empty"
            self.add_button(
                (850, 440 + index * 52, 370, 44),
                f"Item {index + 1}: {label}",
                lambda i=index, b=body_id: self.toggle_herb(b, i),
            )
        held = sum(slot == "herb" for plan in self.item_plan.values() for slot in plan)
        left = max(0, self.save.herbs - held)
        self.canvas.blit(
            self.font_sm.render(f"Herbs left to hand out: {left}", True, MUTED),
            (850, 552),
        )
        self.canvas.blit(
            self.font_sm.render(f"Spots on this map: {len(ep['slots'])}", True, MUTED),
            (850, 578),
        )

    def _gear_label(self, gear):
        if gear is None:
            return "None"
        plus = f" +{gear.plus}" if gear.plus else ""
        return GEAR[gear.kind]["name"] + plus

    def _cycle_row(self, y, title, value, callback):
        self.canvas.blit(self.font_sm.render(title, True, MUTED), (850, y))
        self.add_button((850, y + 22, 370, 40), value, callback)

    def cycle(self, body_id, slot, step):
        if slot == "weapon":
            choices = self.save.gear_choices(body_id, "weapon")
            if len(choices) <= 1:
                self.say("They only have one weapon they can hold.")
                return
            current = self.save.equipped(body_id, "weapon")
            index = next(i for i, gear in enumerate(choices) if current and gear.uid == current.uid)
            self.save.equip(body_id, choices[(index + step) % len(choices)].uid)
            return
        choices = self.save.gear_choices(body_id, slot)
        row = [None] + choices
        current = self.save.equipped(body_id, slot)
        if current is None:
            index = 0
        else:
            index = 1 + next(i for i, gear in enumerate(choices) if gear.uid == current.uid)
        nxt = row[(index + step) % len(row)]
        if nxt is None:
            self.save.unequip_slot(body_id, slot)
        else:
            self.save.equip(body_id, nxt.uid)

    def toggle_herb(self, body_id, slot):
        plan = self.item_plan.setdefault(body_id, [None, None])
        if plan[slot] == "herb":
            plan[slot] = None
            return
        used = sum(item == "herb" for items in self.item_plan.values() for item in items)
        if used >= self.save.herbs:
            self.say("No herbs left in the bag.")
            return
        plan[slot] = "herb"

    def start_battle(self):
        if not self.order:
            self.say("Send at least Kairo.")
            return
        plan = {body: list(self.item_plan.get(body, [None, None])) for body in self.order}
        used = sum(item == "herb" for items in plan.values() for item in items)
        if used > self.save.herbs:
            self.say("Not enough herbs.")
            return
        self.snap = self.save.to_dict()
        self.save.herbs -= used
        self.battle = build_battle(self.save, self.ep_id, self.order, plan, random.Random())
        self.mode = "battle"
        self.sel = None
        self.preview = None
        self.aim = None
        self.anims = []
        self.override = {}
        self.dying = {}
        self.floaters = []
        self.cam = [0, 0]
        self.resolved = False
        self.banner = "YOUR TURN"
        self.banner_t = 50
        self.enqueue([{"t": "phase", "phase": "player", "round": 1}])

    def open_results(self):
        if self.resolved:
            return
        self.resolved = True
        if self.battle.outcome == "win":
            self._refund_herbs()
            self.result_notes = self.save.finish_victory(self.ep_id, self.battle)
            self.result_title = "The field is clear"
        else:
            fallen = "Kairo"
            for unit in self.battle.units:
                if not unit.alive and (unit.id == "kairo" or unit.lose_flag):
                    fallen = unit.name
                    break
            self.result_title = f"{fallen} has fallen"
            self.result_notes = ["Nothing was kept. You can try this fight again."]
            self.save = Save.from_dict(self.snap)
        self.save.write(self.save_path)
        self.mode = "results"

    def _refund_herbs(self):
        for unit in self.battle.units:
            if unit.side != "player":
                continue
            for slot in unit.items:
                if slot == "herb":
                    self.save.herbs += 1

    def retry_battle(self):
        self.save = Save.from_dict(self.snap)
        self.start_battle()

    def draw_results(self):
        self.canvas.blit(self.font_lg.render(self.result_title, True, TEXT), (80, 60))
        y = 140
        for note in self.result_notes or ["The gauntlet took nothing new."]:
            y += blit_lines(self.canvas, self.font, wrap(self.font, note, 900), TEXT, 80, y) + 8
        if self.battle and self.battle.outcome == "win":
            self.add_button((80, 620, 280, 52), "Continue", self.after_win)
        else:
            self.add_button((80, 620, 280, 52), "Try this fight again", self.retry_battle)
            self.add_button((380, 620, 280, 52), "Leave", self.leave_loss)

    def after_win(self):
        ep = episode(self.ep_id)
        self.lines = list(ep["outro"])
        self.line_i = 0
        self.after_lines = "workshop"
        self.mode = "story"

    def leave_loss(self):
        self.mode = "world" if self.save.cleared else "title"

    def draw_workshop(self):
        if self.assets.props.get("gauntlet"):
            self.canvas.blit(self.assets.props["gauntlet"], (40, 24))
        self.canvas.blit(self.font_lg.render("Workshop", True, TEXT), (130, 36))
        stone_line = "   ".join(f"{name} {self.save.stones.get(name, 0)}" for name in ("ash", "bone", "cinder", "void"))
        self.canvas.blit(self.font.render(f"Souls {self.save.souls}", True, ORANGE), (40, 120))
        self.canvas.blit(self.font.render(stone_line, True, TEXT), (40, 154))
        self.canvas.blit(
            self.font_sm.render("Stones make a piece. Souls raise it. A click asks before anything is spent.", True, MUTED),
            (40, 190),
        )
        self.canvas.blit(self.font_b.render("Recipes", True, GOLD), (40, 230))
        y = 270
        if not self.save.recipes:
            self.canvas.blit(self.font.render("None yet. They come off the dead.", True, MUTED), (40, y))
        for recipe_id in self.save.recipes:
            recipe = RECIPES[recipe_id]
            cost = ", ".join(f"{amount} {name}" for name, amount in recipe["stones"].items())
            self.add_button(
                (40, y, 560, 48),
                f"Craft {recipe['name']} ({cost})",
                lambda rid=recipe_id: self.ask_craft(rid),
                enabled=self.pending is None and self.save.can_craft(recipe_id),
            )
            y += 58
        self.canvas.blit(self.font_b.render("What you carry", True, GOLD), (680, 230))
        y = 270
        for gear in self.save.gear:
            cost = next_enhance_cost(gear.kind, gear.plus)
            plus = f" +{gear.plus}" if gear.plus else ""
            owner = BODIES[gear.owner]["name"] if gear.owner in BODIES else "spare"
            if cost is None:
                label = f"{GEAR[gear.kind]['name']}{plus}  ·  {owner}  ·  max"
                enabled = False
            else:
                label = f"{GEAR[gear.kind]['name']}{plus}  ·  {owner}  ·  {cost} souls"
                enabled = self.save.souls >= cost
            self.add_button((680, y, 560, 42), label, lambda uid=gear.uid: self.ask_raise(uid), enabled=self.pending is None and enabled)
            y += 48
            if y > 600:
                break
        if self.pending is None:
            self.add_button((40, 650, 280, 48), "Back to the road", self.to_world)
        else:
            self.draw_pending()

    def ask_craft(self, recipe_id):
        if self.save.can_craft(recipe_id):
            self.pending = ("craft", recipe_id)

    def ask_raise(self, uid):
        gear = self.save.gear_by(uid)
        if gear is None:
            return
        cost = next_enhance_cost(gear.kind, gear.plus)
        if cost is not None and self.save.souls >= cost:
            self.pending = ("raise", uid)

    def cancel_pending(self):
        self.pending = None

    def confirm_pending(self):
        if not self.pending:
            return
        kind, target = self.pending
        self.pending = None
        if kind == "craft":
            self.do_craft(target)
        else:
            self.do_enhance(target)

    def draw_pending(self):
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((12, 8, 8, 170))
        self.canvas.blit(shade, (0, 0))
        card = pygame.Rect(240, 180, 800, 320)
        pygame.draw.rect(self.canvas, PANEL, card, border_radius=12)
        pygame.draw.rect(self.canvas, (224, 170, 120), card, 2, border_radius=12)
        self.canvas.blit(self.font_lg.render("Crafting", True, GOLD), (280, 210))
        kind, target = self.pending
        if kind == "craft":
            text = craft_line(target)
        else:
            gear = self.save.gear_by(target)
            text = raise_line(gear.kind, gear.plus) if gear else "That piece is gone."
        blit_lines(self.canvas, self.font, wrap(self.font, text, 720), TEXT, 280, 280, 6)
        self.add_button((280, 410, 240, 52), "Continue", self.confirm_pending)
        self.add_button((560, 410, 240, 52), "Cancel", self.cancel_pending)

    def do_craft(self, recipe_id):
        if not self.save.craft(recipe_id):
            self.say("You need the stones and the recipe.")
            return
        self.save.write(self.save_path)
        self.say(f"Made {RECIPES[recipe_id]['name']}.")

    def do_enhance(self, uid):
        gear = self.save.gear_by(uid)
        if gear is None or not self.save.enhance(uid):
            self.say("Not enough souls, or it cannot be raised.")
            return
        self.save.write(self.save_path)
        self.say(f"{GEAR[gear.kind]['name']} is now +{gear.plus}.")

    def to_world(self):
        self.save.write(self.save_path)
        self.mode = "world"

    def draw_world(self):
        self.canvas.blit(self.font_lg.render("The road", True, TEXT), (60, 36))
        if self.save.next_episode > 2:
            banner = "The first march is done. You can walk these fights again."
        elif self.save.cleared:
            banner = "The next fight is open. The ones behind you can be walked again."
        else:
            banner = "Kureha is burning."
        self.canvas.blit(self.font.render(banner, True, MUTED), (60, 96))
        for index, ep in enumerate(EPISODES):
            locked = ep["id"] > self.save.next_episode
            status = "Cleared" if ep["id"] in self.save.cleared else ("Locked" if locked else "Next")
            label = f"{ep['name']}  ·  {status}"
            self.add_button(
                (60, 170 + index * 90, 520, 70),
                label,
                lambda eid=ep["id"]: self.open_episode(eid),
                enabled=not locked,
            )
        if self.save.cleared:
            self.add_button((60, 560, 280, 48), "Workshop", lambda: self.set_mode("workshop"))
        self.add_button((360, 560, 220, 48), "Title", lambda: self.set_mode("title"))

    def enqueue(self, events):
        for event in events:
            kind = event.get("t")
            if kind == "move" and len(event["path"]) > 1:
                self.override[event["gid"]] = event["path"][0]
                self.anims.append({"t": "move", "gid": event["gid"], "path": event["path"], "f": 0})
            elif kind == "hit":
                text = "Miss" if event.get("miss") else f"-{event['amount']}"
                self.anims.append({"t": "pop", "gid": event["gid"], "text": text, "n": 10, "f": 0, "popped": False})
            elif kind == "heal":
                self.anims.append({"t": "pop", "gid": event["gid"], "text": f"+{event['amount']}", "n": 10, "f": 0, "popped": False})
            elif kind == "die":
                self.dying[event["gid"]] = 36
            elif kind == "phase":
                label = "ENEMY TURN" if event["phase"] == "enemy" else f"YOUR TURN   ·   ROUND {event['round']}"
                self.anims.append({"t": "banner", "label": label, "n": 28, "f": 0})
            elif kind == "spawn":
                self.anims.append({"t": "banner", "label": "Someone reaches the field", "n": 28, "f": 0})
            elif kind == "issen":
                self.anims.append({"t": "banner", "label": "ISSEN", "n": 22, "f": 0})
        if events and not self.anims:
            self.anims.append({"t": "banner", "label": "", "n": 6, "f": 0})

    def tick_anim(self):
        step = self.anims[0]
        if step["t"] == "move":
            segment = 6
            hops = max(1, len(step["path"]) - 1)
            if step["f"] >= hops * segment:
                self.override.pop(step["gid"], None)
                self.anims.pop(0)
                return
            travel = step["f"] / segment
            index = min(hops - 1, int(travel))
            frac = travel - index
            x0, y0 = step["path"][index]
            x1, y1 = step["path"][index + 1]
            self.override[step["gid"]] = (x0 + (x1 - x0) * frac, y0 + (y1 - y0) * frac)
            step["f"] += 1
            return
        if step["t"] == "pop" and not step["popped"]:
            step["popped"] = True
            self._floater(step["gid"], step["text"])
        if step["t"] == "banner":
            self.banner = step["label"]
            self.banner_t = 8
        step["f"] += 1
        if step["f"] >= step.get("n", 12):
            self.anims.pop(0)

    def _floater(self, gid, text):
        unit = self.battle.unit_by_gid(gid) if self.battle else None
        if unit is None:
            return
        x, y = self.foot(unit)
        self.floaters.append({"text": text, "x": x, "y": y - 70, "life": 36})

    def click_battle(self, pos):
        battle = self.battle
        if battle is None or self.anims or battle.phase != "player" or battle.outcome:
            return
        if pos[0] >= 900:
            return
        picked = self.pick(*pos)
        if picked is None:
            return
        kind, data = picked
        if self.aim and kind == "tile" and self.selected() and data in self._stand():
            self.aim = None
            self.preview = data
            return
        if self.aim:
            self.finish_aim(kind, data)
            return
        if kind == "unit" and data.side == "player" and data.alive and not data.acted:
            self.sel = data.gid
            self.preview = data.pos
            return
        if kind == "unit" and data.side == "enemy":
            self.try_attack(data)
            return
        if kind == "tile":
            occ = battle.unit_at(data)
            if occ and occ.side == "player" and occ.alive and not occ.acted:
                self.sel = occ.gid
                self.preview = occ.pos
                return
            if occ and occ.side == "enemy":
                self.try_attack(occ)
                return
            unit = self.selected()
            if unit and data in self._stand():
                self.preview = data
                return
            self.say("Out of reach.")

    def selected(self):
        if self.sel is None or self.battle is None:
            return None
        unit = self.battle.unit_by_gid(self.sel)
        if unit is None or not unit.alive or unit.acted:
            return None
        return unit

    def _stand(self):
        unit = self.selected()
        if unit is None:
            return {}
        stand, _prev = self.battle.movement(unit)
        return stand

    def try_attack(self, enemy):
        unit = self.selected()
        if unit is None:
            self.say("Click one of your fighters first.")
            return
        preview = self.preview or unit.pos
        if preview not in self._stand():
            preview = unit.pos
        legal = {target.gid for target in self.battle.attack_targets(unit, preview)}
        if enemy.gid not in legal:
            self.say("Too far from that tile, or the height blocks it.")
            return
        self.act(preview, {"type": "attack", "target": enemy.gid})

    def finish_aim(self, kind, data):
        unit = self.selected()
        if unit is None:
            self.aim = None
            return
        preview = self.preview or unit.pos
        mode = self.aim[0]
        if mode == "attack":
            enemy = data if kind == "unit" else self.battle.unit_at(data)
            if enemy and enemy.side == "enemy":
                self.try_attack(enemy)
            else:
                self.say("Click the enemy you want to strike.")
            return
        if mode == "item":
            target = data if kind == "unit" else self.battle.unit_at(data)
            if target is None:
                self.say("Click the fighter who needs the herb.")
                return
            self.act(preview, {"type": "item", "slot": self.aim[1], "target": target.gid})
            return
        skill_id = self.aim[1]
        skill = SKILLS[skill_id]
        if skill["kind"] == "line":
            tile = data.pos if kind == "unit" else data
            from ashgauntlet.rules import ortho_dir

            direction = ortho_dir(preview, tile)
            if direction is None:
                self.say("Click a tile in a straight line.")
                return
            self.act(preview, {"type": "skill", "skill": skill_id, "dir": direction})
            return
        target = data if kind == "unit" else self.battle.unit_at(data)
        if target is None:
            self.say("Click a fighter.")
            return
        self.act(preview, {"type": "skill", "skill": skill_id, "target": target.gid})

    def act(self, dest, action):
        unit = self.selected()
        if unit is None:
            return
        events, err = self.battle.player_act(unit.gid, dest, action)
        if err:
            self.say(err)
            return
        self.sel = None
        self.preview = None
        self.aim = None
        self.enqueue(events)

    def end_phase(self):
        if self.battle is None or self.anims or self.battle.phase != "player" or self.battle.outcome:
            return
        self.enqueue(self.battle.end_player_phase())
        self.sel = None
        self.preview = None
        self.aim = None

    def use_skill(self, skill_id):
        unit = self.selected()
        if unit is None:
            self.say("Click one of your fighters first.")
            return
        skill = SKILLS[skill_id]
        preview = self.preview or unit.pos
        if skill["kind"] in ("mode", "nova", "heal_aura", "heal_all"):
            self.act(preview, {"type": "skill", "skill": skill_id})
            return
        options = self.battle.skill_options(unit, preview, skill_id)
        if skill["kind"] == "heal" and options["gids"] == [unit.gid]:
            self.act(preview, {"type": "skill", "skill": skill_id, "target": unit.gid})
            return
        self.aim = ("skill", skill_id)
        self.say(skill["blurb"])

    def draw_battle(self):
        if self.battle is None:
            return
        self.draw_map()
        self.draw_highlights()
        mx, my = pygame.mouse.get_pos()
        picked = self.pick(mx, my) if mx < 900 else None
        self.draw_units()
        self.draw_range_marks()
        hot = picked[1].gid if picked is not None and picked[0] == "unit" else None
        self.draw_foot_marks(hot)
        self.draw_cursor(picked)
        for item in self.floaters:
            image = self.font_b.render(item["text"], True, GOLD if item["text"].startswith("+") or item["text"] == "Miss" else (255, 220, 210))
            self.canvas.blit(image, image.get_rect(center=(item["x"], item["y"])))
        if self.banner_t > 0 and self.banner:
            banner = self.font_lg.render(self.banner, True, TEXT)
            rect = banner.get_rect(center=(450, 36))
            pygame.draw.rect(self.canvas, (20, 16, 14), rect.inflate(24, 12), border_radius=8)
            self.canvas.blit(banner, rect)
        if picked is not None:
            if picked[0] == "tile":
                spot = picked[1]
                who = ""
                blocked = spot in self.battle.blocked
            else:
                spot = picked[1].pos
                who = picked[1].name
                blocked = False
            if blocked:
                label = "Blocked"
            else:
                label = ("Low ground", "Mid ground", "High ground")[self.battle.height(spot)]
            if who:
                label = f"{who}  ·  {label}"
            tag = self.font.render(label, True, TEXT)
            self.canvas.blit(tag, (24, 72))
        self.draw_panel()

    def origin(self):
        battle = self.battle
        cx = (battle.w - 1) / 2
        cy = (battle.h - 1) / 2
        sx = (cx - cy) * HW
        sy = (cx + cy) * HH
        return 450 + self.cam[0] - sx, 360 + self.cam[1] - sy

    def iso(self, x, y):
        ox, oy = self.origin()
        return ox + (x - y) * HW, oy + (x + y) * HH

    def tile_poly(self, x, y):
        cx, cy = self.iso(x, y)
        lift = self.battle.height((x, y)) * 16
        top = [
            (cx, cy - HH - lift),
            (cx + HW, cy - lift),
            (cx, cy + HH - lift),
            (cx - HW, cy - lift),
        ]
        return top, lift, cx, cy

    def draw_map(self):
        battle = self.battle
        palette = CEDAR if battle.theme == "cedar" else VILLAGE
        for x, y in self.cells():
            top, lift, cx, cy = self.tile_poly(x, y)
            height = battle.height((x, y))
            top_c, left_c, right_c = palette[min(height, 2)]
            blocked = (x, y) in battle.blocked
            if blocked:
                top_c = tuple(max(0, c - 28) for c in top_c)
            if lift:
                left = [(cx - HW, cy - lift), (cx, cy + HH - lift), (cx, cy + HH), (cx - HW, cy)]
                right = [(cx + HW, cy - lift), (cx, cy + HH - lift), (cx, cy + HH), (cx + HW, cy)]
                pygame.draw.polygon(self.canvas, left_c, left)
                pygame.draw.polygon(self.canvas, right_c, right)
            pygame.draw.polygon(self.canvas, top_c, top)
            pygame.draw.polygon(self.canvas, (28, 22, 18), top, 1)
            if blocked and height == 0:
                prop = self.assets.props.get("house" if (x + y) % 2 == 0 else "tree")
                if prop:
                    self.canvas.blit(prop, prop.get_rect(midbottom=(cx, cy - lift + 8)))

    def paint(self, tile, color):
        top, _lift, _cx, _cy = self.tile_poly(*tile)
        xs = [p[0] for p in top]
        ys = [p[1] for p in top]
        minx, miny = int(min(xs)), int(min(ys))
        width = int(max(xs) - minx) + 2
        height = int(max(ys) - miny) + 2
        if width < 2 or height < 2:
            return
        temp = pygame.Surface((width, height), pygame.SRCALPHA)
        local = [(p[0] - minx, p[1] - miny) for p in top]
        pygame.draw.polygon(temp, color, local)
        self.canvas.blit(temp, (minx, miny))

    def draw_highlights(self):
        unit = self.selected()
        if unit is None or self.battle.phase != "player":
            return
        stand = self._stand()
        preview = self.preview if self.preview in stand else unit.pos
        for tile in stand:
            self.paint(tile, (64, 132, 214, 90))
        self.paint(preview, (230, 190, 90, 130))
        if self.aim and self.aim[0] == "skill":
            options = self.battle.skill_options(unit, preview, self.aim[1])
            for tile in options["tiles"]:
                self.paint(tile, (230, 200, 80, 130))
        elif self.aim and self.aim[0] == "item":
            for gid in self.battle.item_targets(unit, preview, self.aim[1]):
                target = self.battle.unit_by_gid(gid)
                if target:
                    self.paint(target.pos, (80, 190, 120, 140))
        else:
            for target in self.battle.attack_targets(unit, preview):
                self.paint(target.pos, (210, 72, 64, 130))

    def marked_tiles(self):
        unit = self.selected()
        if unit is None or self.battle.phase != "player":
            return []
        stand = self._stand()
        preview = self.preview if self.preview in stand else unit.pos
        marks = [(tile, (120, 186, 240), 2) for tile in stand]
        marks.append((preview, (240, 210, 120), 3))
        if self.aim and self.aim[0] == "skill":
            options = self.battle.skill_options(unit, preview, self.aim[1])
            marks.extend((tile, (240, 210, 110), 3) for tile in options["tiles"])
        elif self.aim and self.aim[0] == "item":
            for gid in self.battle.item_targets(unit, preview, self.aim[1]):
                target = self.battle.unit_by_gid(gid)
                if target:
                    marks.append((target.pos, (120, 210, 150), 3))
        else:
            for target in self.battle.attack_targets(unit, preview):
                marks.append((target.pos, (230, 96, 86), 3))
        return marks

    def draw_range_marks(self):
        for tile, color, width in self.marked_tiles():
            top, _lift, _cx, _cy = self.tile_poly(*tile)
            pygame.draw.polygon(self.canvas, color, top, width)

    def draw_cursor(self, picked):
        if picked is None:
            return
        spot = picked[1].pos if picked[0] == "unit" else picked[1]
        top, _lift, _cx, _cy = self.tile_poly(*spot)
        color = (255, 244, 210)
        for tile, mark_color, _width in self.marked_tiles():
            if tile == spot:
                color = mark_color
                break
        pygame.draw.polygon(self.canvas, color, top, 4)
        if picked[0] != "unit":
            return
        name = self.font_sm.render(picked[1].name, True, TEXT)
        rect = name.get_rect(midbottom=(top[0][0], top[0][1] - 6))
        rect.clamp_ip(pygame.Rect(8, 8, 884, HEIGHT - 16))
        pygame.draw.rect(self.canvas, (20, 16, 14), rect.inflate(12, 6), border_radius=4)
        self.canvas.blit(name, rect)

    def cells(self):
        battle = self.battle
        for total in range(battle.w + battle.h - 1):
            for x in range(battle.w):
                y = total - x
                if 0 <= y < battle.h:
                    yield x, y

    def draw_xy(self, unit):
        if unit.gid in self.override:
            return self.override[unit.gid]
        return unit.pos

    def visible(self, unit):
        return unit.alive or self.dying.get(unit.gid, 0) > 0

    def foot(self, unit):
        x, y = self.draw_xy(unit)
        cx, cy = self.iso(x, y)
        lift = self.battle.height((int(round(x)), int(round(y)))) * 16
        return cx, cy - lift + 8

    def draw_units(self):
        units = [unit for unit in self.battle.units if self.visible(unit)]
        units.sort(key=lambda unit: sum(self.draw_xy(unit)))
        for unit in units:
            self.draw_one(unit)

    def draw_one(self, unit):
        cx, cy = self.foot(unit)
        color = ORANGE if unit.side == "player" else (150, 110, 190)
        pygame.draw.ellipse(self.canvas, color, (cx - 16, cy - 8, 32, 12))
        image = self.sprite(unit.sprite)
        rect = image.get_rect(midbottom=(cx, cy))
        self.canvas.blit(image, rect)
        if unit.issen and self.assets.fx.get("issen"):
            flash = self.assets.fx["issen"]
            self.canvas.blit(flash, flash.get_rect(center=(cx, rect.top + 10)))
        elif unit.issen:
            pygame.draw.arc(self.canvas, (255, 255, 255), (cx - 18, rect.top, 36, 24), 0.4, 2.7, 3)
        frac = 0 if unit.max_hp <= 0 else max(0, unit.hp) / unit.max_hp
        bar = pygame.Rect(cx - 20, rect.top - 10, 40, 5)
        pygame.draw.rect(self.canvas, (20, 16, 14), bar)
        pygame.draw.rect(self.canvas, HP_COLOR, (bar.x, bar.y, int(40 * frac), 5))
        if unit.lose_flag or unit.id == "kairo":
            pygame.draw.circle(self.canvas, GOLD, (cx, rect.top - 16), 4)

    def draw_foot_marks(self, hot_gid):
        for unit in self.battle.units:
            if not self.visible(unit):
                continue
            cx, cy = self.foot(unit)
            hot = unit.gid == hot_gid
            color = (255, 236, 200) if hot else (ORANGE if unit.side == "player" else (220, 130, 140))
            radius = 8 if hot else 5
            pygame.draw.circle(self.canvas, (20, 16, 14), (int(cx), int(cy)), radius + 2, 2)
            pygame.draw.circle(self.canvas, color, (int(cx), int(cy)), radius, 2)

    def tile_at(self, mx, my):
        diamonds = []
        for x, y in self.cells():
            _top, lift, cx, cy = self.tile_poly(x, y)
            diamonds.append(((x, y), cx, cy - lift))
        return closest_diamond(mx, my, diamonds)

    def pick(self, mx, my):
        # Pictures are taller than a tile, so the body in front covers the
        # fighter and the attack tile behind it. The click follows the ground
        # diamond and ignores the pictures.
        if self.battle is None:
            return None
        tile = self.tile_at(mx, my)
        if tile is None:
            return None
        occ = self.battle.unit_at(tile)
        if occ is not None and self.visible(occ):
            return ("unit", occ)
        return ("tile", tile)

    def draw_panel(self):
        pygame.draw.rect(self.canvas, PANEL, (900, 0, 380, HEIGHT))
        battle = self.battle
        phase = "Your turn" if battle.phase == "player" else "Enemy turn"
        self.canvas.blit(self.font_b.render(f"{battle.title}", True, TEXT), (920, 16))
        self.canvas.blit(self.font.render(f"{phase}   ·   round {battle.rnd}", True, ORANGE), (920, 48))
        unit = self.selected()
        if unit is None:
            help_text = "Point the diamond at a fighter's feet and click. A gold dot means the fight ends if they fall."
            y = 100
            y += blit_lines(self.canvas, self.font, wrap(self.font, help_text, 340), TEXT, 920, y) + 8
        else:
            self.canvas.blit(self.font_b.render(unit.name, True, ORANGE if unit.side == "player" else TEXT), (920, 92))
            self.canvas.blit(self.font_sm.render(unit.weapon_name or "No weapon", True, MUTED), (920, 120))
            self._bar(920, 150, 340, 16, max(unit.hp, 0) / unit.max_hp, HP_COLOR, f"HP {max(unit.hp, 0)}/{unit.max_hp}")
            sp_frac = 0 if unit.max_sp == 0 else unit.sp / unit.max_sp
            self._bar(920, 176, 340, 16, sp_frac, SP_COLOR, f"SP {unit.sp}/{unit.max_sp}")
            atk = battle.attack_power(unit)
            defense = battle.defense_power(unit)
            extra = f"   {unit.mode}" if unit.mode else ""
            issen = "   ISSEN" if unit.issen else ""
            self.canvas.blit(self.font_sm.render(f"ATK {atk}   DEF {defense}   MOV {unit.mov}{extra}{issen}", True, TEXT), (920, 202))
            if unit.lose_flag or unit.id == "kairo":
                self.canvas.blit(self.font_sm.render("If they fall, the march ends.", True, GOLD), (920, 224))
            help_text = "Point the diamond at a foot ring. Blue steps. Red strikes."
            if self.aim:
                help_text = "Click the bright diamond. Right-click cancels."
            blit_lines(self.canvas, self.font_sm, wrap(self.font_sm, help_text, 340), MUTED, 920, 248)
        self.canvas.blit(self.font_sm.render("Recent", True, MUTED), (920, 300))
        for index, line in enumerate(battle.log[-5:]):
            blit_lines(self.canvas, self.font_sm, wrap(self.font_sm, line, 340)[:1], TEXT, 920, 324 + index * 22)
        if unit and battle.phase == "player":
            preview = self.preview if self.preview in self._stand() else unit.pos
            y = 450
            self.add_button((920, y, 160, 36), "Attack", lambda: self.set_aim(("attack",)))
            self.add_button((1090, y, 160, 36), "Wait", lambda: self.act(preview, {"type": "wait"}))
            y += 42
            if unit.weapon_family in ISSEN_FAMILIES:
                self.add_button((920, y, 330, 36), "Issen", lambda: self.act(preview, {"type": "issen"}))
                y += 42
            for skill_id in unit.skills:
                skill = SKILLS[skill_id]
                ready = battle.skill_options(unit, preview, skill_id)["ok"]
                self.add_button(
                    (920, y, 330, 36),
                    f"{skill['name']}  {skill['sp']} SP",
                    lambda sid=skill_id: self.use_skill(sid),
                    enabled=ready,
                )
                y += 40
            for slot, item in enumerate(unit.items):
                if item != "herb":
                    continue
                self.add_button((920, y, 330, 36), f"Herb {slot + 1}", lambda s=slot: self.set_aim(("item", s)))
                y += 40
        remaining = len(battle.unacted_players()) if battle.phase == "player" else 0
        label = f"End phase ({remaining} left)" if remaining else "End phase"
        self.add_button((920, 668, 330, 40), label, self.end_phase, enabled=battle.phase == "player" and not battle.outcome)

    def set_aim(self, aim):
        if self.selected() is None:
            self.say("Click one of your fighters first.")
            return
        self.aim = aim

    def _bar(self, x, y, width, height, frac, color, label):
        pygame.draw.rect(self.canvas, (20, 16, 14), (x, y, width, height), border_radius=3)
        pygame.draw.rect(self.canvas, color, (x, y, int(width * max(0, min(1, frac))), height), border_radius=3)
        self.canvas.blit(self.font_sm.render(label, True, TEXT), (x + 6, y - 1))


def run():
    if "--shots" in sys.argv:
        import os

        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    game = Game()
    if "--shots" in sys.argv:
        game.shoot()
        pygame.quit()
        return
    game.loop()


def _shot_extension(game: Game):
    shots = user_root() / "shots"
    shots.mkdir(exist_ok=True)
    game.draw()
    pygame.image.save(game.canvas, str(shots / "title.png"))
    game.save = new_game()
    game.ep_id = 1
    game.save.prepare_episode(1)
    game.prepare_deploy()
    game.mode = "deploy"
    game.draw()
    pygame.image.save(game.canvas, str(shots / "deploy.png"))
    game.start_battle()
    game.draw()
    pygame.image.save(game.canvas, str(shots / "battle.png"))
    game.save.souls = 40
    game.save.recipes = ["cedar_coat", "ash_blade"]
    game.mode = "workshop"
    game.draw()
    pygame.image.save(game.canvas, str(shots / "workshop.png"))
    game.save.cleared = [1]
    game.save.next_episode = 2
    game.mode = "world"
    game.draw()
    pygame.image.save(game.canvas, str(shots / "world.png"))


Game.shoot = _shot_extension
