# SMA: Multi-Agent Systems Simulations

> Two multi-agent simulations in Python. In the first, autonomous ants sort objects into clusters without any
> central coordination. In the second, a *blocks world* is solved by self-interested agents.

![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-visualization-2E8B57)

Built for a university course on Multi-Agent Systems (*Systèmes Multi-Agents*) by **Rafael Bachourian** and
**Guillaume Baulard**.

## Demo

https://user-images.githubusercontent.com/41969876/140662041-8a63cffb-8ba3-46b5-b92a-1e1ec3c29c8e.mp4

## The simulations

### 1. Ant-based clustering (`TP2.py`)

Two kinds of objects (`A` and `B`) are scattered at random on a grid. Agents move around and pick up or drop
objects using **local perception and short-term memory** only. Clusters of identical objects gradually emerge
on their own.

This is the classic model by Deneubourg et al.:

- Each agent remembers the last **10 cells** it visited and computes `f`, the fraction of those cells that held
  the same kind of object as the current one.
- **Pick-up** probability: `(k⁺ / (k⁺ + f))²`. Isolated objects are likely to be picked up.
- **Drop** probability: `(f / (k⁻ + f))²`. Objects are likely to be dropped near similar ones.
- With `k⁺ = 0.1` and `k⁻ = 0.3`.
- An **error variant** (`--variant`) makes agents confuse `A` and `B` when computing `f`, to study how
  robust the clustering is to perception errors.

The simulation is rendered live with **Pygame**, using sprites for agents, objects, and agents carrying an
object.

### 2. Blocks world (`TP1.py`)

Four blocks (`A`, `B`, `C`, `D`) start in one stack and must be rearranged into the tower
`D` (bottom) → `C` → `B` → `A` (top). Each block is an agent. It *perceives* whether it sits on the right block and whether it is free, then *acts*: it moves to
another column if it is free, or *pushes* (asks the block above it to move) if it isn't. The program prints each
agent's state and the number of iterations needed until every agent is satisfied.

## Getting started

### Requirements

- Python 3.8+
- `pygame`

```bash
git clone https://github.com/Reathe/SMA-1
cd SMA-1
pip install pygame
```

### Run the ant-clustering simulation

```bash
python TP2.py                       # default: 50×50 grid, 200 A, 200 B, 20 agents
python TP2.py -n 80 -m 80 -nA 600 -nB 600 -nAgents 50 -s 10
python TP2.py --variant             # agents make recognition errors
python TP2.py -h                    # list all options
```

| Option | Default | Description |
| --- | --- | --- |
| `-n` / `-m` | 50 / 50 | Grid rows / columns |
| `-nA` / `-nB` | 200 / 200 | Number of `A` / `B` objects |
| `-nAgents` | 20 | Number of agents |
| `-v`, `--variant` | off | Enable the variant with recognition errors |
| `-s`, `--step-per-frame` | 1 | Simulation steps per rendered frame |
| `-t`, `--time-between-frames` | 0 | Delay between frames (seconds) |

#### Controls

| Key | Action |
| --- | --- |
| `Space` | Start / pause |
| `↑` / `↓` | More / fewer steps per frame (hold `Ctrl` to double / halve) |
| `→` / `←` | Speed up / slow down (shorter / longer wait between frames) |

### Run the blocks-world simulation

```bash
python TP1.py
```

## Project structure

```
.
├── TP1.py        # Blocks world: block agents with perceive / act cycle
├── TP2.py        # Ant clustering: board, agents, CLI
├── GUI.py        # Pygame renderer and keyboard controls
├── *.png         # Sprites (agents, objects, agents carrying objects)
├── SujeT_TP2_SMA.pdf                          # Assignment (French)
└── tp2_version_1_rapport_Bachourian_Baulard.pdf  # Our report (French)
```
