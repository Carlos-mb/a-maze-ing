from enum import IntFlag
import random
import os
import time
import collections


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

    # List of oposite walls to simplify open neighbor's walls
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

    def notvisited(self) -> list["Cell"]:
        """Get NON VISITED neighbors"""
        neighbors: list["Cell"] = []
        matrix = self.maze.matrix

        if self.row > 0:
            if (not matrix[self.row - 1][self.col].visited and
                    matrix[self.row - 1][self.col] not in self.maze.coords42):
                neighbors.append(matrix[self.row - 1][self.col])
        if self.row < self.maze.rows - 1:
            if (not matrix[self.row + 1][self.col].visited and
                    matrix[self.row + 1][self.col] not in self.maze.coords42):
                neighbors.append(matrix[self.row + 1][self.col])
        if self.col > 0:
            if (not matrix[self.row][self.col - 1].visited and
                    matrix[self.row][self.col - 1] not in self.maze.coords42):
                neighbors.append(matrix[self.row][self.col - 1])
        if self.col < self.maze.cols - 1:
            if (not matrix[self.row][self.col + 1].visited and
                    matrix[self.row][self.col + 1] not in self.maze.coords42):
                neighbors.append(matrix[self.row][self.col + 1])

        return (neighbors)

    def open_wall(self, wall: int) -> None:

        # Get the neighbor coordinates using the wall position
        neighbor_row = self.row + Cell.relative[wall][0]
        neighbor_col = self.col + Cell.relative[wall][1]

        # If there is a valid neighbor
        if (self.maze.cell_exist(neighbor_row, neighbor_col)):

            # Open my wall
            self.walls &= ~wall  # Open the wall doing "and not wall.X")

            # Open neighbor's wall
            self.maze.matrix[neighbor_row][neighbor_col].walls\
                &= ~self.oposite_wall[wall]

    def able_neighbors(self) -> list["Cell"]:
        """Get able neighbors (with open walls) and not in 42 number"""

        neighbors: list["Cell"] = []
        matrix = self.maze.matrix

        # walls = 0101
        # N     = 0001
        # walls & N == wall exist

        if ((self.row > 0) and not (self.walls & Wall.N) and
            not matrix[self.row - 1][self.col].visited and
                matrix[self.row - 1][self.col] not in self.maze.coords42):
            neighbors.append(matrix[self.row - 1][self.col])
        if ((self.row < self.maze.rows - 1) and not (self.walls & Wall.S) and
            not matrix[self.row + 1][self.col].visited and
                matrix[self.row + 1][self.col] not in self.maze.coords42):
            neighbors.append(matrix[self.row + 1][self.col])
        if ((self.col > 0) and not (self.walls & Wall.W) and
            not matrix[self.row][self.col - 1].visited and
                matrix[self.row][self.col - 1] not in self.maze.coords42):
            neighbors.append(matrix[self.row][self.col - 1])
        if ((self.col < self.maze.cols - 1) and not (self.walls & Wall.E) and
            not matrix[self.row][self.col + 1].visited and
                matrix[self.row][self.col + 1] not in self.maze.coords42):
            neighbors.append(matrix[self.row][self.col + 1])

        return neighbors


class Maze():

    def __init__(self,
                 rows: int, cols: int,
                 seed: int = 94,
                 perfect: bool = True,
                 entry: tuple[int, int] = (0, 0),
                 exit: tuple[int, int] | None = None):

        self.rows = rows
        self.cols = cols
        self.rnd = random.Random(seed)
        self.perfect = perfect
        self.matrix: list[list] = (
            [[Cell(row=row, col=col, maze=self)
              for col in range(cols)]
                for row in range(rows)])
        self.showdraw = False
        self.shortest_path: list[Cell] = []
        self.coords42: list[tuple[int, int]] = []
        self.entry = entry
        if exit is None:
            self.exit = (rows - 1, cols - 1)
        else:
            self.exit = exit

    def draw(self, pos: Cell | None = None, path: list = []):

        # color_reset = "\033[0m"
        color0 = "\033[0m"
        color1 = "\033[92m"
        color2 = "\033[91m"
        color3 = "\033[93m"
        color4 = "\033[94m"

        line = "╔"
        for c in range(self.cols):
            line += "═══"
            if c < self.cols - 1:
                line += "╦"
            else:
                line += "╗"
        print(line)

        for r in range(self.rows):

            # interior line
            line = "║"
            for c in range(self.cols):

                cell = self.matrix[r][c]

                if cell == pos:
                    content = color2 + " X " + color0
                elif cell in path:
                    if (r, c) == self.entry:
                        content = color1 + " E " + color0
                    elif (r, c) == self.exit:
                        content = color2 + " X " + color0
                    else:
                        content = color3 + " * " + color0
                elif cell in self.coords42:
                    content = color4 + " # " + color0
                else:
                    content = "   "

                line += content

                if cell.walls & Wall.E:
                    line += "║"
                else:
                    line += " "

            print(line)

            if r < self.rows - 1:
                line = "╠"
                for c in range(self.cols):

                    cell = self.matrix[r][c]

                    if cell.walls & Wall.S:
                        line += "═══"
                    else:
                        line += "   "

                    if c < self.cols - 1:
                        line += "╬"
                    else:
                        line += "╣"

                print(line)

        line = "╚"
        for c in range(self.cols):
            line += "═══"
            if c < self.cols - 1:
                line += "╩"
            else:
                line += "╝"
        print(line)

    def cell_exist(self, row: int, col: int):
        return (row >= 0 and col >= 0 and row < self.rows and col < self.cols
                and self.matrix[row][col] not in self.coords42)

    def connect(self, origin: Cell, destination: Cell) -> None:

        if destination.row > origin.row:
            origin.open_wall(Wall.S)
        elif destination.row < origin.row:
            origin.open_wall(Wall.N)
        elif destination.col > origin.col:
            origin.open_wall(Wall.E)
        elif destination.col < origin.col:
            origin.open_wall(Wall.W)
        else:
            raise ValueError("Cells are not adjacent")

    def tunnel(self, cell: Cell):
        cell.visited = True
        neighbors = cell.notvisited()

        if self.showdraw:
            os.system("clear")
            self.draw()
            time.sleep(0.1)

        if len(neighbors) > 0:
            dest = self.rnd.choice(neighbors)
            self.connect(cell, dest)
            self.tunnel(dest)

    def pending_neighbors(self):

        notvisited = []
        for row in self.matrix:
            for cell in row:
                # If cell is visited and had no visited neighbors
                if cell.visited:
                    if len(cell.notvisited()) > 0:
                        if cell not in self.coords42:
                            notvisited.append(cell)
        return list(notvisited)

    def unperfect(self) -> None:
        """Do imperfect an perfect maze"""
        # Enumarete generates a tupla of pairs [0, value1], [1, value2]        
        for i, row in enumerate(self.matrix):  # [1:-1]
            if i % 2 == 0 or self.rows == 2:
                cell: Cell = self.rnd.choice(row)  # [1:-1]
                closed = [wall for wall in Wall if cell.walls & wall]
                if closed:
                    # cell.open_wall(self.rnd.choice(closed))
                    cell.open_wall(self.rnd.choice(closed))

    def do_perfect(self):
        """Create a perfect maze"""
        start = self.matrix[0][0]
        self.draw42((self.rows // 2, self.cols // 2))
        self.tunnel(start)

        while any(not cell.visited for row in self.matrix for cell in row):
            pendings = self.pending_neighbors()
            self.tunnel(self.rnd.choice(pendings))
            # self.tunnel(self.rnd.choice([self.pending_neighbors()]))

    def redo(self) -> None:
        self.rnd = random.Random()
        self.matrix: list[list] = (
            [[Cell(row=row, col=col, maze=self)
              for col in range(self.cols)]
                for row in range(self.rows)])        
        self.do_perfect()
        if not self.perfect:
            self.unperfect()

    def get_path(self) -> None:

        for row in self.matrix:
            for cell in row:
                cell.visited = False

        current: Cell = self.matrix[self.entry[0]][self.entry[1]]

        parents: dict[Cell, Cell] = {}
        queue = collections.deque()

        queue.append(current)
        current.visited = True

        while queue:
            if self.showdraw:
                os.system("clear")
                # create path
                path: list[Cell] = [current]
                while parents.get(current, False):
                    path.append(parents[current])
                    current = parents[current]
                self.draw(current, path=path)
                time.sleep(0.1)

            current = queue.popleft()
            neighbors: list[Cell] = current.able_neighbors()
            if neighbors:
                for next in neighbors:
                    queue.append(next)
                    next.visited = True
                    parents[next] = current
                    if next == self.matrix[self.exit[0]][self.exit[1]]:
                        current = next
                        queue = None
                        break

        # create and draw path
        path: list[Cell] = [current]
        while parents.get(current, False):
            path.append(parents[current])
            current = parents[current]

        os.system("clear")
        self.draw(path=path)

        # Create directions from path
        directions = []
        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]

            diff = (b.row - a.row, b.col - a.col)

            for wall, rel in Cell.relative.items():
                if rel == diff:
                    directions.append(wall.name)
                    break

    def draw42(self, center: tuple[int, int]) -> None:
        r, c = center

        pattern = [
            (-2, -3),                      (-2, +1), (-2, +2), (-2, +3),
            (-1, -3),                                          (-1, +3),
            (+0, -3), (+0, -2), (+0, -1),  (+0, +1), (+0, +2), (+0, +3),
                                (+1, -1),  (+1, +1),
                                (+2, -1),  (+2, +1), (+2, +2), (+2, +3)
        ]

        self.coords42 = []
        for dr, dc in pattern:
            rr, cc = r + dr - 1, c + dc - 1
            if self.cell_exist(rr, cc):
                self.coords42.append((self.matrix[rr][cc]))                
            else:
                self.coords42 = []
                break

        for cell in self.coords42:
            cell.visited = True
