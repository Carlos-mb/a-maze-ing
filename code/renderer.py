import maze
import os
import random


class Renderer():

    def __init__(self, maze: maze.Maze, ascii: bool = True):
        self.ascii = ascii
        self.maze = maze

    def __render_ascii__(self):
        os.system("clear")
        self.maze.draw()

        while True:

            cmd = input("[r] regenerate  [p] path  [q] quit: ")

            if cmd == "q":
                break
            elif cmd == "r":
                os.system("clear")
                self.maze.redo()
                self.maze.draw()
            elif cmd == "p":
                os.system("clear")
                self.maze.get_path()

    def render(self) -> None:
        if True:
            self.__render_ascii__()
