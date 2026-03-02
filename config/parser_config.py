from typing import TypedDict,Tuple, Set


class ConfigError(Exception):
      """Raised when the configuration file cannot be parsed or validated."""
      pass


class Config(TypedDict):
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    # algorithm:


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
    except FileNotFoundError:
        raise ConfigError(f"Error: file not found: {config_path}")
    except PermissionError:
        raise ConfigError(f"Error: {config_path} cannot be read")
    except IsADirectoryError:
        raise ConfigError(f"Error: {config_path} cannot be a directory")
