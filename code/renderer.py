import maze
import os


class Renderer():

    def __init__(self, maze: maze.Maze, ascii: bool = True):
        self.ascii = ascii
        self.maze = maze
        maze.do_perfect()
        if not maze.perfect:
            maze.unperfect()

    def newcoordX(self, row: int, col: int) -> bool:
        if (self.maze.cell_exist(row, col) and
           (row, col) != (self.maze.entry[0], self.maze.entry[1])):
            self.maze.exit = (row, col)
            return True
        return False

    def newcoordE(self, row: int, col: int) -> bool:
        if (self.maze.cell_exist(row, col) and
           (row, col) != (self.maze.exit[0], self.maze.exit[1])):
            self.maze.entry = (row, col)
            return True
        return False

    def __render_ascii__(self):
        os.system("clear")
        self.maze.draw()
        path = False

        while True:

            cmd = input("[r] regenerate  [p] path  [q] quit: ")

            if cmd == "q":
                break
            elif cmd == "r":
                self.maze.redo()
            elif cmd == "p":
                path = not path
            elif cmd.startswith("k"):
                self.newcoordX(self.maze.exit[0], self.maze.exit[1] + 1)
            elif cmd.startswith("j"):
                self.newcoordX(self.maze.exit[0], self.maze.exit[1] - 1)
            elif cmd.startswith("m"):
                self.newcoordX(self.maze.exit[0] + 1, self.maze.exit[1])
            elif cmd.startswith("i"):
                self.newcoordX(self.maze.exit[0] - 1, self.maze.exit[1])
            elif cmd.startswith("K"):
                self.newcoordE(self.maze.entry[0], self.maze.entry[1] + 1)
            elif cmd.startswith("J"):
                self.newcoordE(self.maze.entry[0], self.maze.entry[1] - 1)
            elif cmd.startswith("M"):
                self.newcoordE(self.maze.entry[0] + 1, self.maze.entry[1])
            elif cmd.startswith("I"):
                self.newcoordE(self.maze.entry[0] - 1, self.maze.entry[1])
            else:
                try:
                    number = int(cmd)
                    if (self.maze.entry[0] < number and
                            self.maze.entry[1] < number and
                            self.maze.exit[0] < number and
                            self.maze.exit[1] < number):
                        self.maze.rows = number
                        self.maze.cols = number
                        self.maze.redo()
                    else:
                        print("ERROR: cant reduce maze "
                              "with current E and X values")
                except ValueError:
                    pass

            os.system("clear")
            if path:
                self.maze.get_path()
            else:
                self.maze.draw()

    def render(self) -> None:
        if True:
            self.__render_ascii__()
