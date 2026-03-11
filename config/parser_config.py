from typing import TypedDict, Tuple, Set, Literal, Optional

MANDATORY_KEYS: Set[str] = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT"
    }

OPTIONAL_KEYS: Set[str] = {
        "ALGORITHM",
        "SEED"
    }

ALLOWED_KEYS: Set[str] = MANDATORY_KEYS | OPTIONAL_KEYS

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

    try:
        with open(config_path) as f:
            lines = f.readlines()

        useful_lines: list[tuple[int, str]] = []

        for line_number, line in enumerate(lines, start=1):
            cleaned = line.strip()

            if not cleaned:
                continue

            if cleaned.startswith('#'):
                continue

            useful_lines.append((line_number, cleaned))

        for line_number, cleaned in useful_lines:
            if "=" not in cleaned:
                raise ConfigError(f"Error: Line {line_number}:"
                                  " expected KEY=VALUE")

            left, right = cleaned.split("=", 1)
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

        unknown_keys = raw_data.keys() - ALLOWED_KEYS
        if unknown_keys:
            unknown_keys_str = ", ".join(sorted(unknown_keys))
            if len(unknown_keys) == 1:
                raise ConfigError(f"Error: unkown key: {unknown_keys_str}")
            else:
                raise ConfigError(f"Error: unkown keys:"
                                  f" {unknown_keys_str}")

        missing_keys = MANDATORY_KEYS - raw_data.keys()
        if missing_keys:
            missing_keys_str = ", ".join(sorted(missing_keys))
            if len(missing_keys) == 1:
                raise ConfigError(f"Error: missing required key:"
                                  f" {missing_keys_str}")
            else:
                raise ConfigError(f"Error: missing required keys:"
                                  f" {missing_keys_str}")

    except FileNotFoundError:
        raise ConfigError(f"Error: file not found: {config_path}")
    except PermissionError:
        raise ConfigError(f"Error: {config_path} cannot be read")
    except IsADirectoryError:
        raise ConfigError(f"Error: {config_path} cannot be a directory")
