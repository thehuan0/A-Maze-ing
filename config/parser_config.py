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
    """Raise an error for an invalid config file."""
    pass


class Config(TypedDict):
    """Store the parsed maze configuration."""
    width: int
    height: int
    entry_xy: Tuple[int, int]
    exit_xy: Tuple[int, int]
    output_file: str
    perfect: bool
    algorithm: Optional[Literal["dfs", "prim", "kruskal"]]
    seed: Optional[int]

# Helper functions to convert raw config values to typed values.


def parse_int(key_name: str, raw_value: str) -> int:
    """Convert a config value to an integer."""
    try:
        int_value = int(raw_value)
    except ValueError:
        raise ConfigError(
            f"Error: {key_name} must be an integer, got '{raw_value}'"
        )
    return int_value


def parse_bool(key_name: str, raw_value: str) -> bool:
    """Convert a config value to a boolean."""
    value = raw_value.strip().lower()

    if value == "true":
        return True

    if value == "false":
        return False

    raise ConfigError(
        f"Error: {key_name} must be True or False, got '{raw_value}'"
    )


def parse_coordinates(key_name: str, raw_coord: str) -> Tuple[int, int]:
    """Convert a config value to x,y coordinates."""
    parts = raw_coord.split(",")
    if len(parts) != 2:
        raise ConfigError(f"Error: {key_name} must be in format x,y")
    x_raw, y_raw = parts

    x = parse_int(key_name, x_raw.strip())
    y = parse_int(key_name, y_raw.strip())

    return (x, y)


def config_parse(config_path: str) -> Config:
    """Parse and validate a maze config file."""
    raw_data: dict[str, str] = {}
    try:

        # Read config file and collect meaningful lines (skip comments/empty).
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

        # Parse KEY=VALUE pairs and build the raw config dictionary.
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

        # Validate allowed keys and required keys.
        unknown_keys = raw_data.keys() - ALLOWED_KEYS
        if unknown_keys:
            unknown_keys_str = ", ".join(sorted(unknown_keys))
            if len(unknown_keys) == 1:
                raise ConfigError(f"Error: unknown key: {unknown_keys_str}")
            else:
                raise ConfigError(f"Error: unknown keys:"
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

        # Convert raw string values to typed configuration values.
        width = parse_int("WIDTH", raw_data["WIDTH"])
        height = parse_int("HEIGHT", raw_data["HEIGHT"])

        entry_xy = parse_coordinates("ENTRY", raw_data["ENTRY"])
        exit_xy = parse_coordinates("EXIT", raw_data["EXIT"])

        perfect = parse_bool("PERFECT", raw_data["PERFECT"])
        output_file = raw_data["OUTPUT_FILE"]

        if "SEED" in raw_data:
            seed = parse_int("SEED", raw_data["SEED"])
        else:
            seed = None
        if "ALGORITHM" in raw_data:
            algo = raw_data["ALGORITHM"].lower()
            if algo not in {"dfs", "prim", "kruskal"}:
                raise ConfigError(
                    "Error: ALGORITHM must be one of:"
                    " dfs, prim, kruskal"
                )
        else:
            algo = None

        # Validate maze dimensions and entry/exit positions.
        if width <= 0 or height <= 0:
            raise ConfigError("WIDTH and HEIGHT must be positive integers")

        entry_x, entry_y = entry_xy
        exit_x, exit_y = exit_xy

        if entry_x < 0 or entry_y < 0 or entry_x >= width or entry_y >= height:
            raise ConfigError(
                "Error: ENTRY coordinates must be positive"
                " integers and within the maze size"
                )
        if exit_x < 0 or exit_y < 0 or exit_x >= width or exit_y >= height:
            raise ConfigError(
                "Error: EXIT coordinates must be positive"
                " integers and within the maze size"
                )
        if entry_xy == exit_xy:
            raise ConfigError("Error: ENTRY and EXIT cannot be the same")

    except FileNotFoundError:
        raise ConfigError(f"Error: file not found: {config_path}")
    except PermissionError:
        raise ConfigError(f"Error: {config_path} cannot be read")
    except IsADirectoryError:
        raise ConfigError(f"Error: {config_path} cannot be a directory")

    return {
        "width": width,
        "height": height,
        "entry_xy": entry_xy,
        "exit_xy": exit_xy,
        "output_file": output_file,
        "perfect": perfect,
        "algorithm": algo,
        "seed": seed,
    }
