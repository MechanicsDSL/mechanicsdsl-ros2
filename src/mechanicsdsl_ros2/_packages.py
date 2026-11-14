"""
_packages.py
------------
ROS2 package registry and scaffolding utilities for mechanicsdsl-ros2.
"""

from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional


_PACKAGES: Dict[str, Dict] = {
    "mechanicsdsl_pendulum": {
        "description": "Simple and double pendulum nodes with custom messages",
        "nodes": ["pendulum_node", "double_pendulum_node"],
        "messages": ["PendulumState", "SystemState"],
        "ros_distros": ["humble", "iron", "jazzy"],
    },
}


def list_packages() -> List[str]:
    """Return all bundled ROS2 packages."""
    return sorted(_PACKAGES.keys())


def get_package_path(name: str) -> Optional[Path]:
    """
    Return the path to a bundled ROS2 package.

    Parameters
    ----------
    name : str
        Package name. Use list_packages() to see available options.

    Returns
    -------
    Path or None
    """
    if name not in _PACKAGES:
        raise ValueError(f"Unknown package '{name}'. Available: {list_packages()}")
    pkg_dir = Path(__file__).parent
    bundled = pkg_dir / "packages" / name
    if bundled.exists():
        return bundled
    repo_root = pkg_dir.parent.parent
    local = repo_root / name
    if local.exists():
        return local
    return None
