from enum import IntFlag
import random
import os
import time
import collections


class Wall(IntFlag):
    """Bitmask flags representing walls of a maze cell.

    Values:
        N: North wall.
        E: East wall.
        S: South wall.
        W: West wall.
    """
    N = 1
    E = 2
    S = 4
    W = 8


class Cell:
    """Represent a single maze cell.

    Attributes:
        row (int): Row index.
        col (int): Column index.
        maze (Maze): Parent maze.
        visited (bool): Traversal state.
        walls (int): Bitmask of closed walls.
    """

    # Relative position of a cell according to N/E/S/W
    relative: dict[Wall, tuple[int, int]] = {
        Wall.N: (-1, 0),
        Wall.E: (0, +1),
        Wall.S: (+1, 0),
        Wall.W: (0, -1)
    }

    # List of oposite walls to simplify open neighbor's walls
    oposite_wall: dict[Wall, Wall] = {
        Wall.N: Wall.S,
        Wall.E: Wall.W,
        Wall.S: Wall.N,
        Wall.W: Wall.E
    }

    def __init__(self, row: int, col: int, maze: "Maze") -> None:
        """Initialize a cell.

        Args:
            row (int): Row index.
            col (int): Column index.
            maze (Maze): Parent maze reference.

        Returns:
            None
        """
        self.maze: Maze = maze
        self.row: int = row
        self.col: int = col

        self.visited: bool = False

        # Walls. Byte OR of 0001, 0010, 0100 and 1000
        self.walls: int = Wall.N | Wall.E | Wall.S | Wall.W

    def notvisited(self) -> list["Cell"]:
        """Return unvisited neighbor cells excluding blocked pattern cells.

        Returns:
            list[Cell]: Unvisited adjacent cells.
        """
        neighbors: list[Cell] = []
        matrix: list[list[Cell]] = self.maze.matrix

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

    def open_wall(self, wall: Wall) -> None:
        """Open one wall in this cell and opposite wall in adjacent cell.

        Args:
            wall (Wall): Wall direction to open.

        Returns:
            None
        """
        # Get the neighbor coordinates using the wall position
        neighbor_row: int = self.row + Cell.relative[wall][0]
        neighbor_col: int = self.col + Cell.relative[wall][1]

        # If there is a valid neighbor
        if (self.maze.cell_exist(neighbor_row, neighbor_col)):

            # Open my wall
            self.walls &= ~wall  # Open the wall doing "and not wall.X"

            # Open neighbor's wall
            self.maze.matrix[neighbor_row][neighbor_col].walls\
                &= ~self.oposite_wall[wall]

    def able_neighbors(self) -> list["Cell"]:
        """Return traversable unvisited neighbors via open walls.

        Returns:
            list[Cell]: Reachable adjacent cells.
        """
        neighbors: list[Cell] = []
        matrix: list[list[Cell]] = self.maze.matrix

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

    def to_hex(self) -> str:
        return format(int(self.walls), "X")


class MazeGenerator:
    """Generate, mutate, and solve a maze.

    Attributes:
        rows (int): Number of rows.
        cols (int): Number of columns.
        matrix (list[list[Cell]]): Grid of cells.
        entry (tuple[int, int]): Start coordinate.
        exit (tuple[int, int]): End coordinate.
    """

    def __init__(
        self,
        rows: int = 10,
        cols: int = 10,
        seed: int = 94,
        perfect: bool = True,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
        outputfile: str = "",
        speed: int = 32,
        canv_w: int = 1920,
        canv_h: int = 1080
    ) -> None:
        """Initialize maze grid and generation options.

        Args:
            rows (int): Row count.
            cols (int): Column count.
            seed (int): RNG seed.
            perfect (bool): Whether maze remains perfect.
            entry (tuple[int, int]): Entry coordinate.
            exit (tuple[int, int] | None): Exit coordinate or default bottom-right.

        Returns:
            None
        """
        self.rows: int = rows
        self.cols: int = cols
        self.rnd: random.Random = random.Random(seed)
        self.perfect: bool = perfect
        self.matrix: list[list[Cell]] = (
            [[Cell(row=row, col=col, maze=self)
              for col in range(cols)]
                for row in range(rows)])
        self.showdraw: bool = False
        self.shortest_path: list[Cell] = []
        self.coords42: list[Cell] = []
        self.entry: tuple[int, int] = entry
        if exit is None:
            self.exit: tuple[int, int] = (rows - 1, cols - 1)
        else:
            self.exit = exit
        self.outputfile: str = outputfile
        self.speed: int = speed
        self.canv_w: int = canv_w
        self.canv_h: int = canv_h
        self.color: str = "\033[0m"

    def draw(self, pos: Cell | None = None, path: list[Cell] | None = None) -> None:
        """Draw maze in terminal.

        Args:
            pos (Cell | None): Optional highlighted position.
            path (list[Cell] | None): Optional path to highlight.

        Returns:
            None
        """
        if path is None:
            path = []

        color_reset = "\033[0m"
        # color0: str = "\033[0m"
        color0: str = self.color
        color1: str = "\033[92m"
        color2: str = "\033[91m"
        color3: str = "\033[93m"
        color4: str = "\033[94m"

        line: str = self.color + "╔"
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

                cell: Cell = self.matrix[r][c]

                content: str
                if cell == pos and not path:
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
        print(line + color_reset)

    def cell_exist(self, row: int, col: int) -> bool:
        """Check whether a coordinate is inside bounds and not blocked.

        Args:
            row (int): Row index.
            col (int): Column index.

        Returns:
            bool: `True` if the coordinate is valid.
        """
        return (row >= 0 and col >= 0 and
                row < self.rows and col < self.cols
                and self.matrix[row][col] not in self.coords42)

    def connect(self, origin: Cell, destination: Cell) -> None:
        """Open wall between two adjacent cells.

        Args:
            origin (Cell): Source cell.
            destination (Cell): Adjacent destination cell.

        Returns:
            None
        """
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

    def tunnel(self, cell: Cell) -> None:
        """Recursively carve maze passages from a cell.

        Args:
            cell (Cell): Current cell.

        Returns:
            None
        """
        cell.visited = True
        neighbors: list[Cell] = cell.notvisited()

        if self.showdraw:
            os.system("clear")
            self.draw()
            time.sleep(0.1)

        if len(neighbors) > 0:
            dest: Cell = self.rnd.choice(neighbors)
            self.connect(cell, dest)
            self.tunnel(dest)

    def pending_neighbors(self) -> list[Cell]:
        """Collect visited cells that still have unvisited neighbors.

        Returns:
            list[Cell]: Candidate cells to continue carving.
        """
        notvisited: list[Cell] = []
        for row in self.matrix:
            for cell in row:
                # If cell is visited and had no visited neighbors
                if cell.visited:
                    if len(cell.notvisited()) > 0:
                        if cell not in self.coords42:
                            notvisited.append(cell)
        return list(notvisited)

    def unperfect(self) -> None:
        """Open extra walls to make the maze imperfect.

        Returns:
            None
        """
        # Enumarete generates a tupla of pairs [0, value1], [1, value2]
        for i, row in enumerate(self.matrix):  # [1:-1]
            if i % 2 == 0 or self.rows == 2:
                cell: Cell = self.rnd.choice(row)  # [1:-1]
                while cell in self.coords42:
                    cell = self.rnd.choice(row)  # [1:-1]
                closed: list[Wall] = [
                    wall for wall in Wall if cell.walls & wall]
                if closed:
                    # cell.open_wall(self.rnd.choice(closed))
                    cell.open_wall(self.rnd.choice(closed))

    def do_perfect(self) -> None:
        """Generate a perfect maze.

        Returns:
            None
        """
        start: Cell = self.matrix[0][0]
        self.draw42(((self.rows - 1) // 2, (self.cols - 1) // 2))
        self.tunnel(start)

        # while any(not cell.visited for row in self.matrix for cell in row):
        pendings: list[Cell] = self.pending_neighbors()
        while pendings:
            self.tunnel(self.rnd.choice(pendings))
            pendings = self.pending_neighbors()
            # self.tunnel(self.rnd.choice([self.pending_neighbors()]))

    def create(self) -> None:
        """Regenerate maze with current dimensions/options.

        Returns:
            None
        """
        # self.rnd = random.Random()
        self.matrix = (
            [[Cell(row=row, col=col, maze=self)
              for col in range(self.cols)]
                for row in range(self.rows)])
        self.do_perfect()
        if not self.perfect:
            self.unperfect()    

    def get_path(self) -> None:
        """Compute and draw shortest path from entry to exit.

        Returns:
            None
        """
        for row in self.matrix:
            for cell in row:
                cell.visited = False

        current: Cell = self.matrix[self.entry[0]][self.entry[1]]

        parents: dict[Cell, Cell] = {}
        queue: collections.deque[Cell] = collections.deque()

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
                        queue.clear()
                        break

        # create and draw path
        path = [current]
        while parents.get(current, False):
            path.append(parents[current])
            current = parents[current]

        self.draw(path=path)

        # Create directions from path
        directions: str = ""
        for i in range(len(path) - 1, 0, -1):  # reverse range: start,stop,step
            a: Cell = path[i]
            b: Cell = path[i - 1]

            diff: tuple[int, int] = (b.row - a.row, b.col - a.col)

            for wall, rel in Cell.relative.items():
                if rel == diff:
                    wall_name: str | None = wall.name
                    if wall_name:
                        directions += (wall_name)
                    break
        
        self.export_file(directions)

        self.shortest_path = path

    def __try_to_draw42(self, center: tuple[int, int]) -> None:
        """Try placing the 42-pattern obstacle centered at given coordinates.

        Args:
            center (tuple[int, int]): Candidate center coordinate.

        Returns:
            None
        """
        # pattern: list[tuple[int, int]] = [
        #     (-2, -3),                      (-2, +1), (-2, +2), (-2, +3),
        #     (-1, -3),                                          (-1, +3),
        #     (+0, -3), (+0, -2), (+0, -1),  (+0, +1), (+0, +2), (+0, +3),
        #                         (+1, -1),  (+1, +1),
        #                         (+2, -1),  (+2, +1), (+2, +2), (+2, +3)
        # ]
        pattern: list[tuple[int, int]] = [
            (-2, -2),           (-2, +1), (-2, +2),
            (-1, -2),                     (-1, +2),
            (+0, -2), (+0, -1), (+0, +1), (+0, +2),
                      (+1, -1), (+1, +1),
                      (+2, -1), (+2, +1), (+2, +2)
        ]

        r: int
        c: int
        r, c = center
        if self.cols - c < 2:
            return
        self.coords42 = []
        for dr, dc in pattern:
            rr: int = r + dr
            cc: int = c + dc
            if self.cell_exist(rr, cc):
                self.coords42.append(self.matrix[rr][cc])
            else:
                self.coords42 = []
                break

    def draw42(self, center: tuple[int, int]) -> None:
        """Place a valid 42-pattern obstacle while preserving entry/exit.

        Args:
            center (tuple[int, int]): Preferred center coordinate.

        Returns:
            None
        """
        self.__try_to_draw42(center)

        for coord in self.coords42:  # only enter if 42 has been drawed
            if ((coord.row, coord.col) == self.entry or
                    (coord.row, coord.col) == self.exit):
                self.coords42 = []

                for row in self.matrix:  # no [3:] -> Good for any pattern size
                    for cell in row:
                        self.__try_to_draw42((cell.row, cell.col))

                        for coord in self.coords42:
                            if ((coord.row, coord.col) == self.entry or
                                    (coord.row, coord.col) == self.exit):
                                self.coords42 = []
                                break

                        if len(self.coords42) > 0:
                            break
                    if len(self.coords42) > 0:
                        break
                break
        for cell in self.coords42:
            cell.visited = True

    def matrix_to_hex(self) -> list[str]:

        hex_matrix: list[str] = []

        for row in self.matrix:
            hex_matrix.append("")
            for cell in row:
                hex_matrix[-1] += cell.to_hex()

        return hex_matrix

    def export_file(self, directions: str) -> None:
        hex_matrix = self.matrix_to_hex()

        if self.outputfile != "":
            with open(self.outputfile, "w") as f:
                for row in hex_matrix:
                    f.write(row + "\n")
                f.write("\n")
                f.write(str(self.entry[1]) + "," + str(self.entry[0]) + "\n")
                f.write(str(self.exit[1]) + "," + str(self.exit[0]) + "\n")
                f.write(directions + "\n")


    def is_wall(self, row: int, col: int) -> bool:

        if 0 <= row < self.rows and 0 <= col < self.cols:
            return True
        cell = self.matrix[row][col]
        return cell.walls == (Wall.N | Wall.E | Wall.S | Wall.W) or cell in self.coords42