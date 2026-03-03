from enum import IntFlag


class Wall(IntFlag):
    """
    Bitmask representation of the four possible walls of a maze cell.

    Each member represents a cardinal direction and corresponds to a single bit
    in a 4-bit integer. A wall being present (closed) means its bit is set to 1
    A wall being absent (open) means its bit is set to 0.

    Bit mapping (LSB first):

        Bit 0 (1)  -> North
        Bit 1 (2)  -> East
        Bit 2 (4)  -> South
        Bit 3 (8)  -> West

    This class inherits from IntFlag instead of Enum because multiple walls
    can exist simultaneously in a single cell. IntFlag allows bitwise
    combination using operators such as |, &, and ~.

    Example:
        >>> cell_walls = Wals.N | Wall.E
        >>> int(cell_walls)
        3
        >>> bool(cell_walls & Wall.N)
        True
        >>> bool(cell_walls & Wall.S)
        False

    This representation directly matches the hexadecimal encoding required
    for the maze output file format.
    """
    N = 1
    E = 2
    S = 4
    W = 8


class Cell():

    # Relative position of a cell according to N/E/S/W
    relative: dict[int, tuple[int, int]] = {
        Wall.N: (-1, 0),
        Wall.E: (0, +1),
        Wall.S: (+1, 0),
        Wall.W: (0, -1)
        }

    oposite_wall: dict[int, int] = {
        Wall.N: Wall.S,
        Wall.E: Wall.W,
        Wall.S: Wall.N,
        Wall.W: Wall.E
        }

    def __init__(self, row: int, col: int, maze: "Maze"):

        self.maze = maze
        self.row: int = row
        self.col: int = col

        self.visited: bool = False

        # Walls. Byte OR of 0001, 0010, 0100 and 1000
        self.walls: int = Wall.N | Wall.E | Wall.S | Wall.W

    def get_neighbors(self) -> list["Cell"]:
        neighbors: list["Cell"] = []
        matrix = self.maze.matrix

        if self.row > 0:
            neighbors.append(matrix[self.row - 1][self.col])
        if self.row < self.maze.rows - 1:
            neighbors.append(matrix[self.row + 1][self.col])
        if self.col > 0:
            neighbors.append(matrix[self.row][self.col - 1])
        if self.col < self.maze.cols - 1:
            neighbors.append(matrix[self.row][self.col + 1])

        return (neighbors)

    def open_wall(self, wall: int) -> None:

        self.walls &= ~wall  # Open the wall (and not wall.X)

        neighbor_row = self.row + Cell.relative[wall][0]
        neighbor_col = self.col + Cell.relative[wall][1]

        if (self.maze.cell_exist(neighbor_row, neighbor_col)):
            self.maze.matrix[neighbor_row][neighbor_col].walls\
                &= ~self.oposite_wall[wall]


class Maze():

    def __init__(self, rows: int, cols: int):

        self.rows = rows
        self.cols = cols
        self.matrix: list[list] = (
            [[Cell(row=row, col=col, maze=self)
              for col in range(cols)]
                for row in range(rows)])

    def show(self):

        print("|" + "-----" * self.cols + "|")

        for r in range(self.rows):

            line = "|"
            for c in range(self.cols):
                line += "+"
                cell: Cell = self.matrix[r][c]
                if cell.walls & Wall.N:  # I'll see double walls, for check
                    line += "---"
                else:
                    line += "   "
                line += "+"
            line += "|"
            print(line) 

            line = "|"
            for c in range(self.cols):
                cell: Cell = self.matrix[r][c]
                if cell.walls & Wall.W:  # I'll see double walls, for check
                    line += "|"
                else:
                    line += " "
                line += "   "
                if cell.walls & Wall.E:
                    line += "|"
                else:
                    line += " "
            line += "|"
            print(line)

            line = "|"
            for c in range(self.cols):
                line += "+"
                cell: Cell = self.matrix[r][c]
                if cell.walls & Wall.S:  # I'll see double walls, for check
                    line += "---"
                else:
                    line += "   "
                line += "+"
            line += "|"
            print(line)

        print("|" + "-----" * self.cols + "|")

    def cell_exist(self, row: int, col: int):
        return (row >= 0 and col >= 0 and row < self.rows and col < self.cols)


def pruebavecinos(maze, row, col):
    m = maze.matrix
    print(f"\nVecinos de {row} - {col}")
    print("Celda:" + str(m[row][col].row) + " - " + str(m[row][col].col))

    for row in [m[row][col].get_neighbors()]:
        print("vecinos ", end="")
        for cell in row:
            print(f"[{cell.row}{"X" if cell.visited else "-"}{cell.col}]", end="")
        print()


def abrecierra(maze: Maze, row: int, col: int):

    my_cell: Cell = maze.matrix[row][col]
    print("="*20 + "Abre-Cierra" + "="*20)
    print(f"CELDA: {row}, {col}")
    maze.show()
    print(format(my_cell.walls, "04b"))
    print("Abro N")
    my_cell.open_wall(Wall.N)
    maze.show()
    print("Abro S")
    my_cell.open_wall(Wall.S)
    maze.show()
    print("Abro E")
    my_cell.open_wall(Wall.E)
    maze.show()
    print("Abro W")
    my_cell.open_wall(Wall.W)
    maze.show()




mz = Maze(3, 3)
mz.show()
# pruebavecinos(mz, 0, 0)
# pruebavecinos(mz, 2, 2)
# pruebavecinos(mz, 4, 4)

# abrecierra(mz, 0, 0)

abrecierra(mz, 2, 2)
mz = Maze(3, 3)
abrecierra(mz, 1, 1)
# abrecierra(mz, 4, 4)