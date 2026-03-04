import maze
import os
import random


class Renderer():

    def __init__(self, maze: maze.Maze, ascii: bool = True):
        self.ascii = ascii
        self.maze = maze

    def __render_ascii__(self):
        while True:
            os.system("clear")
            self.maze.draw()

            cmd = input("[r] regenerate  [p] path  [q] quit: ")

            if cmd == "q":
                break
            elif cmd == "r":
                self.maze.redo()
            elif cmd == "p":
                self.show_path = not self.show_path

    def render(self) -> None:
        if ascii:
            self.__render_ascii__()
