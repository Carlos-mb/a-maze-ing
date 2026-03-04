from maze import Maze
from renderer import Renderer
import sys

def read_config() -> dict[str, str | int] | None:
    
    output: dict = {}

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return None

    try:
        with open(sys.argv[1]) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    output[key.strip()] = value.strip()

    except FileNotFoundError:
        print("ERROR: config file does not exist")
        return None
    except Exception:
        print("Undefined error. Usage: python3 a_maze_ing.py config.txt")
        return None

    return output


def main():

    config = read_config()
    mz = Maze(20, 20)
    mz.showdraw = False
    mz.do_perfect()
    if not mz.showdraw:
        mz.draw()
    render = Renderer(mz)
    render.render()



if __name__ == "__main__":
    main()
