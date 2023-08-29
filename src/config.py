"""Configurations module for secrets as stuff"""
import toml
import pydash as py_


class CONFIG:
    """
    Config file for storing TOML variables
    Define a singleton instance
    Allows all the functions to access it
    """

    _instance = None
    _config = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CONFIG, cls).__new__(cls)
            cls.load_config_toml()
        return cls._instance

    @classmethod
    def load_config_toml(cls) -> None:
        """Load the TOMLs"""
        CONFIG._config = load_config_toml()

    @classmethod
    def get_key(cls, path) -> str:
        """Return toml variable for given path"""
        if not cls._config:  # checks if _config is empty
            cls._config = cls.load_config_toml()
        try:
            return py_.get(cls._config, path)
        except KeyError as exc:
            raise KeyError(f"Key {path} not found in configuration.") from exc


def load_config_toml() -> dict:
    """Load the configuration file"""
    return toml.load("./config.toml")
