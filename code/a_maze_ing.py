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

    try:
        output["WIDTH"] = int(output.get("WIDTH", "20"))
        output["HEIGHT"] = int(output.get("HEIGHT", "20"))
        output["ENTRY"] = tuple(map(
                                int, output.get("ENTRY", "0,0").split(",")))
        if len(output["ENTRY"]) != 2:
            raise ValueError("Error: ENTRY must be int, int")

        if output["ENTRY"][0] < 0 or output["ENTRY"][1] < 0 or\
           output["ENTRY"][0] > output["WIDTH"] - 1 or\
           output["ENTRY"][1] > output["HEIGHT"] - 1:

            raise ValueError("Error: ENTRY must be inside maze limits")

        output["EXIT"] = tuple(map(int, output.get("EXIT", "0,0").split(",")))
        if len(output["EXIT"]) != 2:
            raise ValueError("Error: EXIT must be int, int")

        if output["EXIT"][0] < 0 or output["EXIT"][1] < 0 or\
           output["EXIT"][0] > output["WIDTH"] - 1 or\
           output["EXIT"][1] > output["HEIGHT"] - 1:

            raise ValueError("Error: EXIT must be inside maze limits")

        # Not sure of this:
        # if output["ENTRY"][0] == output["EXIT"][0] and\
        #    output["ENTRY"][1] == output["EXIT"][1]:
        #     raise ValueError("Error: ENTRY and EXIT must be different points")

        output["OUTPUT_FILE"] = output.get("HEIGHT", "maze.txt")
        output["PERFECT"] = bool(output.get("PERFECT", "True"))
        output["SEED"] = int(output.get("SEED", "94"))

    except ValueError as e:
        print(e)
        return None

    return output


def main():

    config: dict[str, str | int] | None = read_config()
    if config is None:
        return

    mz = Maze(config["WIDTH"],
              config["HEIGHT"],
              config["SEED"])
    mz.showdraw = False
    mz.do_perfect()
    mz.draw()
    mz.unperfect()
    mz.draw()
    # if not mz.showdraw:
    #     mz.draw()
    # render = Renderer(mz)
    # render.render()



if __name__ == "__main__":
    main()
