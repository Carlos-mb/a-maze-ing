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
                self.maze.redo()
                os.system("clear")
                self.maze.draw()
            elif cmd == "p":
                os.system("clear")
                self.maze.get_path()
            elif cmd.startswith("k"):


                # Cambialo para que primero calcule las coordenadas destin
                # y luego valide si son válidas con el método de existe la celda
                # y que no coincida Entrada con Salida

                if self.maze.exit[1] < self.maze.cols - 1:
                    self.maze.exit = (self.maze.exit[0], self.maze.exit[1] + 1)
                os.system("clear")
                self.maze.get_path()
            elif cmd.startswith("j"):
                if self.maze.exit[1] > 0:
                    self.maze.exit = (self.maze.exit[0], self.maze.exit[1] - 1)
                os.system("clear")
                self.maze.get_path()
            elif cmd.startswith("m"):
                if self.maze.exit[0] < self.maze.rows - 1:
                    self.maze.exit = (self.maze.exit[0] + 1, self.maze.exit[1])
                os.system("clear")
                self.maze.get_path()
            elif cmd.startswith("i"):
                if self.maze.exit[0] > 0:
                    self.maze.exit = (self.maze.exit[0] - 1, self.maze.exit[1])
                os.system("clear")
                self.maze.get_path()                
            else:
                try:
                    number = int(cmd)
                    self.maze.rows = number
                    self.maze.cols = number
                    self.maze.redo()
                    os.system("clear")
                    self.maze.draw()
                except TypeError:
                    pass

    def render(self) -> None:
        if True:
            self.__render_ascii__()
