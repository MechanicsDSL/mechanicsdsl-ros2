"""
cli.py
------
Command-line interface for ``mechanicsdsl-ros2``.

Performs *real* scaffolding: compiles a DSL spec through ``mechanicsdsl-core``
and emits a complete, colcon-buildable ROS2 package whose node integrates the
DSL-derived equations of motion.

Usage
-----
    mechanicsdsl-ros2 packages
    mechanicsdsl-ros2 scaffold pendulum -o ros2_ws/src
    mechanicsdsl-ros2 scaffold my_system.msl -o ros2_ws/src
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from ._bridge import CoreNotInstalled, DSLCompileError, compile_spec
from ._packages import _PACKAGES
from ._scaffold import scaffold_package


def _scaffold(args: argparse.Namespace) -> int:
    try:
        system = compile_spec(args.spec)
    except CoreNotInstalled as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except DSLCompileError as exc:
        print(f"DSL compilation failed: {exc}", file=sys.stderr)
        return 1

    root = scaffold_package(system, args.out)
    print(
        f"Compiled '{system.name}' "
        f"({len(system.coordinates)} DOF: {', '.join(system.coordinates)})"
    )
    print(f"Scaffolded ROS2 package -> {root}")
    print("Build with:  colcon build --packages-select "
          f"mechanicsdsl_{system.name}")
    return 0


def _packages(_: argparse.Namespace) -> int:
    print("Bundled MechanicsDSL ROS2 packages:")
    for name, info in _PACKAGES.items():
        print(f"  {name}")
        print(f"    Nodes:    {', '.join(info['nodes'])}")
        print(f"    Messages: {', '.join(info['messages'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-ros2",
        description="Compile MechanicsDSL specs to complete ROS2 packages.",
    )
    sub = parser.add_subparsers(dest="command")

    p_pkgs = sub.add_parser("packages", help="List bundled ROS2 packages")
    p_pkgs.set_defaults(func=_packages)

    p_scaf = sub.add_parser("scaffold", help="Scaffold a ROS2 package from a DSL spec")
    p_scaf.add_argument(
        "spec",
        help="Path to a .msl file, a raw DSL string, or a core preset name.",
    )
    p_scaf.add_argument(
        "--out", "-o", default=".",
        help="Output directory (typically a ROS2 workspace 'src/').",
    )
    p_scaf.set_defaults(func=_scaffold)
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
