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
    repo_root = pkg_dir.parent.parent.parent.parent
    local = repo_root / name
    if local.exists():
        return local
    return None


def main() -> None:
    """Entry point for mechanicsdsl-ros2 CLI."""
    import argparse
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-ros2",
        description="MechanicsDSL ROS2 integration tools"
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("packages", help="List bundled ROS2 packages")

    scaf = sub.add_parser("scaffold", help="Scaffold a new ROS2 package from DSL spec")
    scaf.add_argument("spec", help="Path to .msl DSL specification file")
    scaf.add_argument("--out", "-o", default=".", help="Output directory (ROS2 workspace src/)")
    scaf.add_argument("--distro", "-d", default="jazzy",
                      choices=["humble", "iron", "jazzy"], help="ROS2 distribution")

    args = parser.parse_args()

    if args.command == "packages":
        print("Bundled MechanicsDSL ROS2 packages:")
        for p, info in _PACKAGES.items():
            print(f"  {p}")
            print(f"    Nodes:    {', '.join(info['nodes'])}")
            print(f"    Messages: {', '.join(info['messages'])}")

    elif args.command == "scaffold":
        try:
            import mechanicsdsl
            mechanicsdsl.generate(args.spec, target="ros2", out=args.out,
                                  ros_distro=args.distro)
        except ImportError:
            print("mechanicsdsl-core is required for code generation.")
            print("Install with: pip install mechanicsdsl-core")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
