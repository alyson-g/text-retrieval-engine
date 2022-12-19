import logging
import os
from pathlib import Path
from typing import List


def setup_logging():
    """Get all loggers within the project."""
    root_folder = find_root()
    child_modules = find_child_modules(root_folder)

    log_level = os.getenv("LOG_LEVEL", "INFO")

    for module in child_modules:
        logger = logging.getLogger(module)
        add_handler(logger, log_level)


def add_handler(logger: logging.Logger, log_level: str):
    """Adds a handler to the provided logger."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_format, date_format)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.setLevel(log_level)
    logger.addHandler(console_handler)


def find_root() -> Path:
    """Find the project root directory."""
    curr_dir = Path(__file__)
    parent = curr_dir.parent

    is_parent_module = is_module(parent)

    while is_parent_module:
        parent = parent.parent
        is_parent_module = is_module(parent)

    return parent


def is_module(path: Path) -> bool:
    """Determines if a given directory is a module."""
    init_file_path = os.path.join(path, "__init__.py")
    return os.path.exists(init_file_path)


def find_child_modules(path: Path) -> List[str]:
    """Find all child modules in a given directory."""
    child_modules = []

    for child in os.scandir(path):
        child_path = child.path

        if is_module(child_path):
            child_modules.append(child.name)

    return child_modules
