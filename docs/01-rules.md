# Rules

Frozen. Do not add a speed bar, job change, mid-fight inventory, or a timing minigame for Issen.

## Board

- Isometric grid. Story maps are 12×12 to 16×16.
- A tile holds one unit.
- Units may path through allies. They may not path through enemies or end on an occupied tile.
- Height bands: Low, Mid, High.
- Entering a tile whose band differs by 1 costs +1 move on top of the step.
- A band gap of 2 or more blocks movement and blocks attacks, skills, and items that need a target.
- Guns and bows need a straight orthogonal or diagonal line with no unit and no gap-2 tile between shooter and target. Spears do not need an empty tile between (range 2 can strike over an adjacent occupied tile only if that tile is an ally; an enemy in the way blocks the spear).

## Turn

1. Player phase. Each living ally acts once, in an order the player picks. A unit that has already acted this phase cannot be selected again.
2. Enemy phase. Enemies act in a fixed map order (top to bottom, then left to right on ties).
3. That pair is one round.

A unit’s turn is: move up to MOV, then exactly one action, or either half alone.

Actions: Attack, Skill, Item, Issen, Wait. Oni-Wake is a skill Kairo can pick instead of those, and it replaces the action.

Moving back along the path before confirming is free. After the action is chosen, the turn is spent.

## Weapons and range

| Family | Attack range | Issen |
|---|---|---|
| Sword, light sword, dagger, axe | Adjacent (1) | Yes |
| Spear | 2 | Yes |
| Bow, gun | Line, up to 5 tiles | No |

Range is the equipped weapon, not the body. A sword user holding nothing cannot attack.

## Stats

HP, SP, ATK, DEF, MOV. No separate INT or AGL in the first build. Hit chance is flat: 100 on melee, 90 on bow and gun, minus 15 if the target is in a mode that says Dodge.

Damage = max(1, ATK + weapon − DEF). Skills say if they replace this or repeat it.

Level = 100 EXP. Growth is fixed per body (see roster). No allocation.

## Items

Each unit has two item slots, filled on the deploy screen. Using an item is the action. Effects are single-target on self or an adjacent ally unless the item says otherwise. No shared bag during the fight.

## Death and victory

- At 0 HP the unit is removed for this battle only. No permadeath. No mid-battle raise unless a map rule says so (episode 7).
- If Kairo reaches 0 HP, the battle is lost immediately.
- A map may name one extra lose-flag. If that unit reaches 0 HP, the battle is lost.
- Rout: every enemy is gone.
- Lord hunt: the named unit is gone. Other enemies may live. The battle ends at the start of the next player phase, after the kill’s souls resolve.

## Issen

Declare it as the action, after moving or instead of moving. The unit enters Issen until the next time that unit would act, or until it triggers.

During the enemy phase, the first adjacent physical Attack (not a skill, not a bow, not a gun) against that unit:

- misses,
- the attacker is reduced to 0 HP,
- soul gain from that kill is ×4,
- Issen ends.

If several attackers exist, only the first in enemy order is deleted. Later strikes resolve normally.

No trigger if nobody uses a qualifying Attack. Lords are immune: their Attack hits, Issen is consumed, nobody dies from the counter. The episode 9 captain is not a lord for this rule.

## Oni-Wake

Kairo only, after it is unlocked (episode 9).

- Cost: half of maximum SP, rounded down, paid from current SP. If current SP is lower, it cannot be used.
- Kairo transforms. The player issues no further orders to him.
- The form lasts until 3 enemy phases have fully resolved (count the one about to start if he transformed on his turn before it).
- AI: if a lord is on the map, move toward it and use the strongest affordable attack or skill. Otherwise move toward the largest adjacent cluster and do the same. It will not Wait if any attack is legal.
- When the form ends: Kairo cannot transform again this battle, and his next player turn is move only.

## Skills

A body has 2 or 3 personal skills. They are learned by level or by a story flag written on the campaign doc. SP costs:

| Kind | SP |
|---|---|
| Mode (Strongman, Defender, Weakling, Blind, Target, Dodge) | 8 |
| 2-hit or 3-hit melee | 24 |
| 6-hit melee | 40 |
| Line of 3 | 18 |
| Line of up to 8 | 36 |
| Shockwave, one direction | 16 |
| Shockwave, two or four directions | 28 |
| Element shot, one target | 14 |
| Status arrow | 12 |
| Heal one adjacent ally for 40% of the caster’s max HP | 10 |
| Heal allies within 2 tiles for 25% | 22 |
| Full-map heal for 20% | 40 |
| Steal | 8 |
| Aura (all allies, ATK +5 and DEF +5 for this round and the next) | 30 |

Modes last until that unit has taken two further turns. Strongman: ATK +8. Defender: DEF +8. Weakling: target ATK −8. Blind: target bow/gun hit −30. Target: that enemy takes +4 from every hit. Dodge: incoming hit −15. Modes do not stack with themselves.

Steal: one random stone or unlearned recipe on that enemy. Failure if they have none. Not usable on lords.

Multi-hit skills roll damage once per hit against one adjacent target. Line skills hit every enemy in the stated direction, stopped by a gap-2 tile or the map edge. They do not stop on allies (allies are skipped, not hit).

## Chanted kill

Lord-only skill. The lord spends its action chanting. A marker is visible on every ally inside the declared area (a 2-tile radius around a tile the lord can see). On that lord’s next turn, if the chant was not interrupted, every ally still inside the area drops to 0 HP.

Interrupt: any HP damage to the lord breaks the chant. Issen does not, because lords are immune and a normal Attack still deals damage, which does break it.

## Souls

Each non-lord kill grants 10 souls, ×4 on Issen. Lords grant 100, never multiplied. Souls persist between episodes. They are only spent on enhancement.

## Seat stances

After a camp conclusion, one stance can be toggled on the deploy screen. Only one is active.

- White Fang (after episode 7): an ally attacking from a higher band than the target deals +6 damage on the first hit of that attack.
- Cinder Bird (after episode 11): all ally ATK +3.
- River Coil (after episode 15): spears and guns ignore 4 DEF.
- Stone Shell (after episode 18): the first hit each unit takes in a round is halved, rounded down, minimum 1.

## Enemy AI (default)

If a player unit is within MOV + attack range, move to a legal attack tile and Attack, preferring a lose-flag, then the lowest HP. Otherwise step toward the nearest player unit. Skills are used only when the unit’s card says the HP or range condition. Lords chant when three or more allies sit in some 2-tile radius they can see, and they are above half HP.
