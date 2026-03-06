from maze import Maze
from renderer import Renderer
import sys


def read_config() -> dict[str, str | int | tuple[int, int]] | None:

    output: dict = {}

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return None

    try:
        with open(sys.argv[1]) as f:
            for i, line in enumerate(f, start=1):
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" not in line:
                        msg = (
                            f"Error: invalid config line {i}. "
                            "Expected KEY=VALUE"
                        )
                        raise ValueError(msg)
                    key, value = line.split("=", 1)
                    output[key.strip()] = value.strip()

    except FileNotFoundError:
        print("ERROR: config file does not exist")
        return None
    except ValueError as e:
        print(e)
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
        #    raise ValueError("Error: ENTRY and EXIT must be different points")

        output["OUTPUT_FILE"] = output.get("OUTPUT_FILE", "maze.txt")

        output["PERFECT"] = output.get("PERFECT", "true").lower()
        if output["PERFECT"] not in ("true", "false"):
            raise ValueError("Error: PERFECT should be true | false")
        output["PERFECT"] = output["PERFECT"] == "true"

        output["SHOWDRAW"] = output.get("SHOWDRAW", "true").lower()
        if output["SHOWDRAW"] not in ("true", "false"):
            raise ValueError("Error: SHOWDRAW should be true | false")
        output["SHOWDRAW"] = output["SHOWDRAW"] == "true"

        output["SEED"] = int(output.get("SEED", "94"))

    except ValueError as e:
        print(e)
        return None

    return output


def main():

    config: dict[str, str | int | tuple[int, int]] | None = read_config()
    if config is None:
        return

    try:
        mz = Maze(cols=config["WIDTH"],
                  rows=config["HEIGHT"],
                  seed=config["SEED"],
                  perfect=config["PERFECT"],
                  entry=config["ENTRY"],
                  exit=config["EXIT"])

        mz.showdraw = config["SHOWDRAW"]

        # mz.do_perfect()
        # mz.unperfect()
        # mz.draw()

        render = Renderer(mz)
        render.render()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Runtime error: {e}")


if __name__ == "__main__":
    main()
