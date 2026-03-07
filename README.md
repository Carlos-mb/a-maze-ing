*This project has been created as part of the 42 curriculum by cmelero-, smarin-s.*

# A-Maze-Ing

Python implementation of a configurable maze generator and solver with ASCII and graphical (MLX) rendering backends.

## Description

This project builds and solves mazes with deterministic generation, optional visual rendering, and export to the required hexadecimal format.

Main goals:

- Generate perfect and imperfect mazes from configurable parameters
- Solve the maze with shortest path (BFS)
- Visualize the maze in ASCII or MLX mode
- Export structure + path in evaluator-friendly format

Project structure:

```text
a_maze_ing.py      → Application entry point
maze.py            → MazeGenerator, Cell, and Wall classes
renderer.py        → ASCII + MLX rendering backend
```

## Instructions

### Requirements

- Python 3.10+
- MinilibX (optional, only for graphical mode)
- XPM assets (for MLX mode)

ASCII mode works independently from MLX.

### Installation / Setup


```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # only if your environment uses one
```

### Execution

```bash
python3 a_maze_ing.py config.txt
```

### Complete `config.txt` Structure and Format

Expected format: one `KEY=VALUE` pair per line.

```ini
WIDTH=20
HEIGHT=20
ENTRY=0,0
EXIT=19,19
SEED=94
PERFECT=true
OUTPUT_FILE=maze.txt
SHOWDRAW=true
GRAPHIC_MODE=Mlx
CAMERA_SPEED=32
CANVAS_WIDTH=1920
CANVAS_HEIGHT=1080
```

Supported keys and defaults:

| Key | Description | Default |
| --- | --- | --- |
| WIDTH | Maze width | 20 |
| HEIGHT | Maze height | 20 |
| ENTRY | Entry coordinate (row,col) | 0,0 |
| EXIT | Exit coordinate (row,col) | bottom-right |
| SEED | Random seed | 94 |
| PERFECT | true / false | true |
| OUTPUT_FILE | Export filename | maze.txt |
| SHOWDRAW | Show generation animation | true |
| GRAPHIC_MODE | ASCII / Mlx | Mlx |
| CAMERA_SPEED | Camera speed (MLX) | 32 |
| CANVAS_WIDTH | Window width (MLX) | 1920 |
| CANVAS_HEIGHT | Window height (MLX) | 1080 |

Validation includes file format, bounds, booleans, and backend availability.

### Controls

ASCII mode:

| Key | Action |
| --- | --- |
| r | Regenerate maze |
| p | Toggle shortest path |
| s | Toggle generation animation |
| c | Change color |
| Arrow keys | Resize maze |
| Shift + Arrows | Move entry/exit |
| q | Quit |

MLX mode includes camera movement, tile rendering, entry/exit sprites, and path overlay.

## Technical Choices

### Maze generation algorithm

We use **recursive backtracking** (depth-first randomized carving) to generate a perfect maze.

Why this algorithm:

- Guarantees connectivity and a unique path between two cells in perfect mode
- Easy to implement and debug with cell-wall bitmasks
- Produces good-looking mazes with low overhead
- Integrates naturally with our wall representation and animation flow

When `PERFECT=false`, we mutate the perfect maze by opening additional walls to create loops (imperfect maze).

### Maze solving algorithm

Shortest path uses **Breadth-First Search (BFS)** with parent tracking and reverse reconstruction, then direction encoding (`N/E/S/W`).

## Output File Format

Exported file contains:

1. Maze rows encoded in hexadecimal (one line per row)
2. Empty line
3. Entry coordinate `(col,row)`
4. Exit coordinate `(col,row)`
5. Direction string of the shortest path

Wall bitmask encoding:

- `1` → North
- `2` → East
- `4` → South
- `8` → West

## Code Reusability

Reusable core: `MazeGenerator` in `maze.py`.

- Independent from CLI logic (`a_maze_ing.py`)
- Independent from rendering (`renderer.py`)
- Can be imported in other projects for programmatic generation and solving

Example:

```python
from maze import MazeGenerator

maze = MazeGenerator(rows=20, cols=20)
maze.create()
path = maze.solve()
```

## Team and Project Management

### Roles

**cmelero-**

- ASCII renderer
- Configuration parsing
- Export format
- Maze generation structure

**smarin-s**

- MLX backend
- Texture management
- Camera system
- Event hooks

**Joint work**

- BFS solver
- Path direction encoding
- ASCII movement interaction
- Integration and testing

### Planning: expected vs real execution

Initial idea: dedicate several weeks to iterate in phases (core generation, solver, rendering, polishing).

What actually happened: we got very motivated, worked full time, and finished the core implementation in just a few days, then used extra time for stabilization and validation.

### Retrospective

What worked well:

- Clear module split (`maze.py` / `renderer.py` / entrypoint)
- Fast feedback loop by testing ASCII mode first with interactive movement and maze resize

What can be improved:

- Ask more students to know their experience
- Earlier formal test plan for edge cases

### Tools used

- Git / GitHub for version control and collaboration
- Python virtual environments for reproducible setup
- Terminal-based manual tests + output validator

## Resources

Classic references related to the topic:

- Graph traversal fundamentals (BFS/DFS): https://cp-algorithms.com/graph/breadth-first-search.html
- Maze generation (recursive backtracking): https://en.wikipedia.org/wiki/Maze_generation_algorithm
- Python documentation: https://docs.python.org/3/
- MinilibX references/man pages (included in project): `mlx_CLXV/man/man3/`

AI usage in this project:

- Algorithms explanation, bug finder and drafting documentation.

## Error Handling

The program validates:

- Configuration file format
- Coordinate bounds
- Boolean parameters
- Rendering backend availability

Graceful interruption is supported via `Ctrl+C`.
