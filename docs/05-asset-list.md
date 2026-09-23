# Asset list

Nothing in this folder is generated yet. When Imagine is used, lock style on the first batch and reuse those images as references.

## Style lock

Super-deformed isometric chibi, three-quarter view, readable at GBA scale. Thick dark outline. Palette is muted ash, cedar green, and paper white, with one accent per faction:

- Allies: cinder orange
- Ash Court pawns: dull violet
- Seat beasts: bone white, with the seat’s accent (fang silver, bird red, coil teal, shell stone)
- Lords: black-red

Portraits are separate from map sprites: painted bust, same face, not the chibi body.

UI frames, move highlights, and the soul slider are drawn in code later. Do not generate them. Exceptions: the gauntlet icon and the recipe-book cover.

## First batch (anchors)

Generate these before any other asset, and do not continue if they disagree with each other:

1. Kairo, map sprite, idle, sword, orange accent, gauntlet on the left arm.
2. Shio, map sprite, idle, short blade, smaller silhouette than Kairo.
3. Pawn, map sprite, idle, violet, no unique face.
4. One village diamond tile, Low band.
5. One castle-yard diamond tile, Mid band.
6. Issen flash, a short white arc over a tile, transparent background.

## Map sprites

17 allies. Each: idle, plus two attack frames. Same body for Oni-Wake as Kairo, with horns and a darker outline, not a new person.

Enemy sheets, recolored rather than redrawn as individuals:

- Pawn
- Bushi
- Claw-beast
- Bomb-twin (two palette swaps of one body)
- Gun-nest (object, not a person)
- Beast-champion (one body, four palette accents)
- Lord (one body, portrait carries the identity)

## Tiles

One diamond cell each. Low / Mid / High only where listed.

| Set | Bands |
|---|---|
| Village | Low, Mid |
| Cedar slope | Low, Mid, High |
| Riverbank | Low |
| Castle yard | Mid |
| Camp plateau | Mid, High |
| Ash factory | Low, Mid |
| Hollow stone | Low, Mid |
| Throne | High |

Plus straight bridge (Low) and a slope connector between bands.

## Portraits

17 allies. Kurogane first skin, Kurogane true skin, Fox-Minister, Glass-Surgeon, four beasts, Ash Warden, Stair Captain. 25 busts. Bomb-twins and nests do not get portraits.

## VFX

- Souls leaving a dying tile and entering the gauntlet.
- Issen flash (anchor 6).
- Chant marker: a thin ring on threatened tiles.
- Oni-Wake: silhouette swap only.

## Audio

Out of scope until a board exists. Later: one world loop, one battle loop, one workshop sting. No voice.

## Do not generate

Full equipment icons for items that are not in the starter workshop. Dialogue backgrounds. A world map illustration. Any image that needs an original character’s name or likeness.
