from typing import TypedDict, Tuple, Set, Literal, Optional


class ConfigError(Exception):
    """Raised when the configuration file cannot be parsed or validated."""
    pass


class Config(TypedDict):
    width: int
    height: int
    entry_xy: Tuple[int, int]
    exit_xy: Tuple[int, int]
    output_file: str
    perfect: bool
    algorithm: Optional[Literal["dfs", "prim", "kruskal"]]
    seed: Optional[int]


def config_parse(config_path: str) -> Config:
    raw_data: dict[str, str] = {}
    mandatory_keys: Set[str] = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT"
    }
    try:
        with open(config_path) as f:
            lines = f.readlines()
        useful_lines = []
        for line_number, line in enumerate(lines, start=1):
            cleaned = line.strip()
            if not cleaned:
                continue
            if cleaned.startstwith('#'):
                continue
            useful_lines.append(line_number, cleaned)

    except FileNotFoundError:
        raise ConfigError(f"Error: file not found: {config_path}")
    except PermissionError:
        raise ConfigError(f"Error: {config_path} cannot be read")
    except IsADirectoryError:
        raise ConfigError(f"Error: {config_path} cannot be a directory")
