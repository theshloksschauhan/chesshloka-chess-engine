# Chesshloka

A playable chess game in Python and Pygame with full move rules, four board themes and a built-in computer opponent.

![Starting position](snapshots/snapshot1.png)

## Features

- **Complete rules:** legal-move generation with check detection, castling, en passant and pawn promotion
- **Computer opponent:** alpha-beta search, 2 plies deep, scored on material and piece-square tables (about 0.4 s per move)
- **Game end:** detects checkmate and stalemate
- **Drag and drop:** legal target squares and the last move are highlighted, with separate move and capture sounds
- **Four themes:** green, brown, blue and gray

## Run it

```bash
pip install -r requirements.txt
python src/main.py      # run from the repository root so assets resolve
```

## Controls

| Key | Action |
|---|---|
| Drag a piece | Make a move |
| `a` | Toggle the computer opponent (it plays black) |
| `t` | Cycle board theme |
| `r` | Restart the game |

## How the AI works

`src/ai.py` searches every legal move for black, then every reply for white, using alpha-beta pruning. Captures are searched first so pruning cuts more branches. Leaf positions are scored by material, plus piece-square tables that reward central knights, advanced pawns and a castled king. Among moves that score the same, it picks at random, so games vary.

## Project structure

```
src/
  main.py     event loop and input
  game.py     rendering, turns, AI hook, game-over state
  board.py    board state, move generation, check detection
  ai.py       search and evaluation
  piece.py    piece types and values
  move.py, square.py, dragger.py, config.py, theme.py, sound.py, const.py
docs/class-diagram.jpeg
```

## Screenshots

| Valid moves | Castling |
|---|---|
| ![Valid moves](snapshots/snapshot5.png) | ![Castling](snapshots/snapshot6.png) |

| Brown | Blue | Gray |
|---|---|---|
| ![Brown](snapshots/snapshot2.png) | ![Blue](snapshots/snapshot3.png) | ![Gray](snapshots/snapshot4.png) |
