from mazegen.generator import MazeGenerator, Cell, Wall
import os
import random
import sys
from typing import Any, Callable


"""
    # type: ignore makes a typo fix
    In case use don't have mlx, we can safely ignore the import error.
"""
try:
    import mlx  # type: ignore
except ImportError:
    mlx = None


class Renderer:
    """Render and interact with a maze in text mode.

    Attributes:
        ascii (bool): Whether ASCII rendering mode is enabled.
        maze (maze.Maze): Maze instance managed by the renderer.
    """

    def __init__(self, maze_obj: MazeGenerator,
                 ascii: bool = True,
                 showdraw: bool = False) -> None:
        """Initialize renderer and generate maze layout.

        Args:
            maze_obj (maze.Maze): Maze object to render.
            ascii (bool): Enable ASCII mode.

        Returns:
            None
        """
        self.ascii: bool = ascii
        self.maze: MazeGenerator = maze_obj

        self.mlx_core: Any = None
        self.mlx_ptr: Any = None
        self.win_ptr: Any = None

        self.wall_sprites: dict[int, Any] = {}
        self.t_42: Any = None
        self.t_walk: Any = None
        self.show_path: bool = False
        self.t_start: Any = None
        self.t_end: Any = None

        self.cam_x = 0 
        self.cam_y = 0
        self.win_w = self.maze.canv_w
        self.win_h = self.maze.canv_h
        speed: dict = {}
        self.color: str = "\033[0m"
        self.showdraw = showdraw

    def draw(self,
             pos: Cell | None = None,
             path: list[Cell] | None = None) -> None:
        """Draw maze in terminal.

        Args:
            pos (Cell | None): Optional highlighted position.
            path (list[Cell] | None): Optional path to highlight.

        Returns:
            None
        """

        maze = self.maze

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
        for c in range(maze.cols):
            line += "═══"
            if c < maze.cols - 1:
                line += "╦"
            else:
                line += "╗"
        print(line)

        for r in range(maze.rows):

            # interior line
            line = "║"
            for c in range(maze.cols):

                cell: Cell = maze.matrix[r][c]

                content: str
                if cell == pos and not path:
                    content = color2 + " X " + color0
                elif cell in path:
                    if (r, c) == maze.entry:
                        content = color1 + " E " + color0
                    elif (r, c) == maze.exit:
                        content = color2 + " X " + color0
                    else:
                        content = color3 + " * " + color0
                elif cell in maze.coords42:
                    content = color4 + " # " + color0
                else:
                    content = "   "

                line += content

                if cell.walls & Wall.E:
                    line += "║"
                else:
                    line += " "

            print(line)

            if r < self.maze - 1:
                line = "╠"
                for c in range(maze.cols):

                    cell = maze.matrix[r][c]

                    if cell.walls & Wall.S:
                        line += "═══"
                    else:
                        line += "   "

                    if c < maze.cols - 1:
                        line += "╬"
                    else:
                        line += "╣"

                print(line)

        line = "╚"
        for c in range(maze.cols):
            line += "═══"
            if c < maze.cols - 1:
                line += "╩"
            else:
                line += "╝"
        print(line + color_reset)


    def newcoordX(self, row: int, col: int) -> bool:
        """Move exit coordinate if target cell is valid.

        Args:
            row (int): Target row.
            col (int): Target column.

        Returns:
            bool: `True` if exit was updated, else `False`.
        """
        if (self.maze._cell_exist(row, col) and
           (row, col) != (self.maze.entry[0], self.maze.entry[1])):
            self.maze.exit = (row, col)
            return True
        return False

    def newcoordE(self, row: int, col: int) -> bool:
        """Move entry coordinate if target cell is valid.

        Args:
            row (int): Target row.
            col (int): Target column.

        Returns:
            bool: `True` if entry was updated, else `False`.
        """
        if (self.maze._cell_exist(row, col) and
           (row, col) != (self.maze.exit[0], self.maze.exit[1])):
            self.maze.entry = (row, col)
            return True
        return False

    def __render_ascii__(self) -> None:
        """Run interactive ASCII render loop.

        Handles keyboard commands for regeneration, path toggle,
        entry/exit movement, and maze resizing.

        Returns:
            None
        """
        colors: list[str] = [
            "\033[91m",  # Red
            "\033[92m",  # Green
            "\033[93m",  # Yellow
            "\033[94m",  # Blue
            "\033[95m",  # Magenta
            "\033[96m",  # Cyan
        ]

        os.system("clear")
        self.maze.generate()
        self.drawer()
        path: bool = False
        cmd: str = ""

        while True:
            try:
                cmd = input("[r]egen [p]ath  [c]olor [s]how [q]uit: ")
            except EOFError:
                break
            except KeyboardInterrupt:
                print()
                break

            if cmd == "q":
                break
            elif cmd == "r":
                self.maze.rnd = random.Random()
                self.maze.generate()
            elif cmd == "s":
                self.maze.showdraw = not self.maze.showdraw
            elif cmd == "p":
                path = not path
            elif cmd == '\x1b[1;2C':
                self.newcoordX(self.maze.exit[0], self.maze.exit[1] + 1)
            elif cmd == '\x1b[1;2D':
                self.newcoordX(self.maze.exit[0], self.maze.exit[1] - 1)
            elif cmd == '\x1b[1;2B':
                self.newcoordX(self.maze.exit[0] + 1, self.maze.exit[1])
            elif cmd == '\x1b[1;2A':
                self.newcoordX(self.maze.exit[0] - 1, self.maze.exit[1])
            elif cmd == '\x1b[1;5C':
                self.newcoordE(self.maze.entry[0], self.maze.entry[1] + 1)
            elif cmd == '\x1b[1;5D':
                self.newcoordE(self.maze.entry[0], self.maze.entry[1] - 1)
            elif cmd == '\x1b[1;5B':
                self.newcoordE(self.maze.entry[0] + 1, self.maze.entry[1])
            elif cmd == '\x1b[1;5A':
                self.newcoordE(self.maze.entry[0] - 1, self.maze.entry[1])
            elif cmd == '\x1b[C':
                self.maze.cols += 1
                self.maze.generate()
            elif cmd == '\x1b[D':
                self.maze.cols = max(self.maze.cols - 1,
                                     2,
                                     self.maze.entry[1] + 1,
                                     self.maze.exit[1] + 1
                                     )
                self.maze.generate()
            elif cmd == '\x1b[B':
                self.maze.rows += 1
                self.maze.generate()
            elif cmd == '\x1b[A':
                self.maze.rows = max(self.maze.rows - 1,
                                     2,
                                     self.maze.entry[0] + 1,
                                     self.maze.exit[0] + 1
                                     )                                      
                self.maze.generate()
            elif cmd == "c":
                self.maze.color = random.choice(
                    [c for c in colors if c != self.maze.color])
            os.system("clear")
            if path:
                self.maze.solve()
            else:
                self.maze.draw()

        print(cmd)

    def load_resources(self) -> None:
        """Carga los XPM una vez que MLX está inicializado."""
        base_dir = os.path.dirname(os.path.dirname(__file__))
        img_dir = os.path.join(base_dir, "img")

        try:
            for i in range(16):
                bit_str = format(i, '04b')
                path = os.path.join(img_dir, f"t_wall_{bit_str}.xpm")
                img = self.mlx_core.mlx_xpm_file_to_image(self.mlx_ptr, path)
                if not img or not img[0]:
                    raise FileNotFoundError(f"No se pudo cargar {path}")
                self.wall_sprites[i] = img[0]

            self.t_42 = self.mlx_core.mlx_xpm_file_to_image(self.mlx_ptr, os.path.join(img_dir, "t_42.xpm"))[0]
            self.t_walk = self.mlx_core.mlx_xpm_file_to_image(self.mlx_ptr, os.path.join(img_dir, "t_walk.xpm"))[0]
            self.t_start = self.mlx_core.mlx_xpm_file_to_image(self.mlx_ptr, os.path.join(img_dir, "t_start.xpm"))[0]
            self.t_end = self.mlx_core.mlx_xpm_file_to_image(self.mlx_ptr, os.path.join(img_dir, "t_end.xpm"))[0]
        except Exception as e:
            print(f"Error cargando recursos: {e}")
            sys.exit(1)

    def draw_maze_mlx(self) -> None:
        self.mlx_core.mlx_clear_window(self.mlx_ptr, self.win_ptr)
        TILE_SIZE = 64
        WALK_SIZE = 32
        OFFSET = (TILE_SIZE - WALK_SIZE) // 2

        # Determinamos qué celdas son visibles según la cámara
        start_col = max(0, self.cam_x // TILE_SIZE)
        end_col = min(self.maze.cols, (self.cam_x + self.win_w) // TILE_SIZE + 1)
        start_row = max(0, self.cam_y // TILE_SIZE)
        end_row = min(self.maze.rows, (self.cam_y + self.win_h) // TILE_SIZE + 1)

        # Solo iteramos por la sección visible
        for r in range(start_row, end_row):
            for c in range(start_col, end_col):
                cell = self.maze.matrix[r][c]
                
                # POSICIÓN RELATIVA A LA CÁMARA
                x = c * TILE_SIZE - self.cam_x
                y = r * TILE_SIZE - self.cam_y

                # 1. Capa de suelo/pared
                if cell in self.maze.coords42:
                    img = self.t_42
                else:
                    img = self.wall_sprites.get(int(cell.walls))
                
                if img:
                    self.mlx_core.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, img, x, y)

                # 2. Capa de entrada/salida/camino
                if (r, c) == self.maze.entry:
                    self.mlx_core.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.t_start, x + OFFSET, y + OFFSET)
                elif (r, c) == self.maze.exit:
                    self.mlx_core.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.t_end, x + OFFSET, y + OFFSET)
                elif self.show_path and cell in self.maze.shortest_path:
                    self.mlx_core.mlx_put_image_to_window(self.mlx_ptr, self.win_ptr, self.t_walk, x + OFFSET, y + OFFSET)

    def __render_mlx__(self) -> None:
        if mlx is None:
            print("Error: Mlx backend not available.")
            return

        self.mlx_core = mlx.Mlx()
        self.mlx_ptr = self.mlx_core.mlx_init()
        
        self.load_resources()

        win_width = min(self.maze.cols * 64, self.maze.canv_w)
        win_height = min(self.maze.rows * 64, self.maze.canv_h)
        self.win_ptr = self.mlx_core.mlx_new_window(self.mlx_ptr, win_width, win_height, "A_Maze_Ing MLX")

        def key_hook(keycode: int, param: Any) -> None:
            
            speed = self.maze.speed

            if keycode in (65307, 53, 113): 
                os._exit(0)
            
            elif keycode == 114:  # [R]egen
                self.maze.generate()
                self.maze.shortest_path = []
                if self.show_path:
                    self.maze.solve()

            elif keycode == 112:  # [P]ath
                self.show_path = not self.show_path
                if self.show_path:
                    self.maze.solve()
                else:
                    self.maze.shortest_path = []
        
            elif keycode == 65361:  # Left
                self.cam_x -= speed
            elif keycode == 65363:  # Right
                self.cam_x += speed
            elif keycode == 65362:  # Up
                self.cam_y -= speed
            elif keycode == 65364:  # Down
                self.cam_y += speed

            self.draw_maze_mlx()

        self.mlx_core.mlx_hook(self.win_ptr, 33, 0, lambda *a: os._exit(0), None)
        self.mlx_core.mlx_hook(self.win_ptr, 2, 1, key_hook, None)

        self.draw_maze_mlx()
        self.mlx_core.mlx_loop(self.mlx_ptr)

    def render(self) -> None:
        """Render maze using the configured backend.
        """
        if self.ascii:
            self.__render_ascii__()
        elif mlx:
            self.__render_mlx__()
        else:
            raise RuntimeError("Error: No rendering backend available.")
