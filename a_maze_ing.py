from mazegen.generator import MazeGenerator, Cell, Wall
from renderer import Renderer
import sys
from typing import cast
import os

def read_config() -> dict[str, str | int | tuple[int, int]] | None:
    """Read and validate maze configuration from a file path in CLI args.

    The function expects exactly one CLI argument: the config file path.
    It parses `KEY=VALUE` pairs, applies defaults, converts values to typed
    fields, and validates coordinate bounds.

    Returns:
        dict[str, str | int | tuple[int, int]] | None:
            A normalized configuration dictionary if valid, otherwise `None`.
    """

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

        output["GRAPHIC_MODE"] = output.get("GRAPHIC_MODE", "Mlx")

        if output["GRAPHIC_MODE"] not in ("ASCII", "Mlx"):
            raise ValueError("Error: GRAPHIC_MODE should be ASCII | Mlx")

        output["CAMERA_SPEED"] = int(output.get("CAMERA_SPEED", "32"
                                                ))
        output["CANVAS_WIDTH"] = int(output.get("CANVAS_WIDTH", "1920"))
        output["CANVAS_HEIGHT"] = int(output.get("CANVAS_HEIGHT", "1080"))
    except ValueError as e:
        print(e)
        return None

    return output


def export_file(maze: MazeGenerator, outputfile: str) -> None:

    directions = maze.directions

    if not maze or directions == "":
        return

    hex_matrix: list[str] = []

    for row in maze.matrix:
        hex_matrix.append("")
        for cell in row:
            hex_matrix[-1] += cell.to_hex()

    if outputfile != "":
        with open(outputfile, "w") as f:
            for row in hex_matrix:
                f.write(row + "\n")
            f.write("\n")
            f.write(str(maze.entry[1]) + "," + str(maze.entry[0]) + "\n")
            f.write(str(maze.exit[1]) + "," + str(maze.exit[0]) + "\n")
            f.write(directions + "\n")


def main() -> None:
    """Run the maze application entry point.

    Reads configuration, builds a [`maze.Maze`](code/maze.py), initializes
    a [`renderer.Renderer`](code/renderer.py), and starts rendering.

    Returns:
        None
    """
    config: dict[str, str | int | tuple[int, int]] | None = read_config()
    if config is None:
        return

    try:

        mz: MazeGenerator = MazeGenerator(
            cols=cast(int, config["WIDTH"]),
            rows=cast(int, config["HEIGHT"]),
            seed=cast(int, config["SEED"]),
            perfect=cast(bool, config["PERFECT"]),
            entry=cast(tuple[int, int], config["ENTRY"]),
            exit=cast(tuple[int, int], config["EXIT"]),
            speed=cast(int, config["CAMERA_SPEED"]),
            canv_w=cast(int, config["CANVAS_WIDTH"]),
            canv_h=cast(int, config["CANVAS_HEIGHT"]))

        graphic_mode = cast(str, config["GRAPHIC_MODE"])
        is_ascii = graphic_mode == "ASCII"
        render: Renderer = Renderer(mz,
                                    ascii=is_ascii,
                                    showdraw=cast(bool, config["SHOWDRAW"]))
        filename: str = cast(str, config["OUTPUT_FILE"])
        export_file(mz, filename)
        if os.path.exists(filename):
            print("File created: "+filename)
        render.render()

    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Runtime error: {e}")


if __name__ == "__main__":
    main()
