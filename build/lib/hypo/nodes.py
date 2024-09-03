import os
from loguru import logger
from dataclasses import dataclass, field
from pathlib import Path


def _get_dataroot():
    """Set the dataroot for different nodes."""

    # node config
    return Path(os.environ["DATA_ROOT", "/data"])


@dataclass
class Nodes:
    """Different config for each node."""

    dataroot: Path = field(default_factory=_get_dataroot)
