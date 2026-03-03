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
    def __init__(self, row: int, col: int, maze: "Maze"):

        self.maze = maze
        self.row: int = row
        self.col: int = col

        self.visited: bool = False

        # Walls. Byte OR of 0001, 0010, 0100 and 1000
        self.walls: int = Wall.N | Wall.E | Wall.S | Wall.W

    def get_neighbor(self) -> list["Cell"]:
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


class Maze():

    def __init__(self, rows: int, cols: int):

        self.rows = rows
        self.cols = cols
        self.matrix: list[list] = (
            [[Cell(row=row, col=col, maze=self)
              for col in range(cols)]
                for row in range(rows)])

    def show(self):
        for row in self.matrix:
            print("row ", end="")
            for cell in row:
                print(f"[{cell.row}{'X' if cell.visited else 'o'}{cell.col}]", end="")
            print()


def pruebavecinos(maze, row, col):
    m = maze.matrix
    print(f"\nVecinos de {row} - {col}")
    print("Celda:" + str(m[row][col].row) + " - " + str(m[row][col].col))

    for row in [m[row][col].get_neighbor()]:
        print("vecinos ", end="")
        for cell in row:
            print(f"[{cell.row}{"X" if cell.visited else "-"}{cell.col}]", end="")
        print()


mz = Maze(5, 5)
mz.show()
pruebavecinos(mz, 0, 0)
pruebavecinos(mz, 2, 2)
pruebavecinos(mz, 4, 4)
