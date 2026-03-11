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
    optional_keys: Set[str] = {
        "ALGORITHM",
        "SEED"
    }
    allowed_keys = mandatory_keys | optional_keys
    try:
        with open(config_path) as f:
            lines = f.readlines()

        useful_lines = []

        for line_number, line in enumerate(lines, start=1):
            cleaned = line.strip()

            if not cleaned:
                continue

            if cleaned.startswith('#'):
                continue

            useful_lines.append((line_number, cleaned))

        for (line_number, cleaned) in useful_lines:
            if "=" not in cleaned:
                raise ConfigError(f"Error: Line {line_number}: expected KEY=VALUE")

            left, right = cleaned.split("=")
            key = left.strip().upper()
            value = right.strip()

            if not key:
                raise ConfigError(f"Error: Line {line_number}: empty key")
            if not value:
                raise ConfigError(f"Error: Line {line_number}: empty value")
            if key in raw_data:
                raise ConfigError(f"Error: Line {line_number}:"
                f" duplicate key {key}")
            raw_data[key] = value
        
        missing_keys = mandatory_keys - 

    except FileNotFoundError:
        raise ConfigError(f"Error: file not found: {config_path}")
    except PermissionError:
        raise ConfigError(f"Error: {config_path} cannot be read")
    except IsADirectoryError:
        raise ConfigError(f"Error: {config_path} cannot be a directory")
