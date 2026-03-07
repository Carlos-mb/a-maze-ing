from maze import Maze

class MazeGenerator:

    def __init__(self, maze: Maze):
        self.maze = maze

    def generate(self) -> None:
        self.maze.do_perfect()
        if not self.maze.perfect:
            self.maze.unperfect()
