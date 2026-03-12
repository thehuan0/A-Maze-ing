import sys
from config import config_parse, ConfigError


def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 a_maze_ing.py <config_file.txt>\n")
        sys.exit(1)

    config_path = sys.argv[1]

    try:
        config = config_parse(config_path)
    except ConfigError as e:
        sys.stderr.write(f"{e}\n")
        sys.exit(1)

    print(config)


if __name__ == "__main__":
    main()
