import maze
import os


class Renderer():

    def __init__(self, maze_obj: maze.Maze, ascii: bool = True) -> None:
        self.ascii: bool = ascii
        self.maze: maze.Maze = maze_obj
        maze_obj.do_perfect()
        if not maze_obj.perfect:
            maze_obj.unperfect()

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

    def __render_ascii__(self) -> None:
        os.system("clear")
        self.maze.draw()
        path: bool = False

        while True:
            try:
                cmd: str = input("[r] regenerate  [p] path  [q] quit: ")
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                break

            if cmd == "q":
                break
            elif cmd == "r":
                self.maze.redo()
            elif cmd == "s":
                self.maze.showdraw = not self.maze.showdraw
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
            elif cmd == '\x1b[C':
                self.maze.cols += 1
                self.maze.redo()
            elif cmd == '\x1b[D':
                self.maze.cols = max(self.maze.cols - 1, 2)
                self.maze.redo()
            elif cmd == '\x1b[B':
                self.maze.rows += 1
                self.maze.redo()
            elif cmd == '\x1b[A':
                self.maze.rows = max(self.maze.rows - 1, 2)
                self.maze.redo()
            else:
                try:
                    number: int = int(cmd)
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
