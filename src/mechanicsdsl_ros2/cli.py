"""
cli.py
------
Command-line interface for ``mechanicsdsl-ros2``.

Compiles a DSL spec through ``mechanicsdsl-core`` and emits a complete,
colcon-buildable ROS2 package whose node integrates the DSL-derived
equations of motion.

Usage
-----
    mechanicsdsl-ros2 packages
    mechanicsdsl-ros2 presets
    mechanicsdsl-ros2 scaffold pendulum -o ros2_ws/src
    mechanicsdsl-ros2 scaffold double_pendulum --lang python --rate 100 -o ros2_ws/src
    mechanicsdsl-ros2 scaffold my_system.msl -o ros2_ws/src
    mechanicsdsl-ros2 header double_pendulum -o include/
    mechanicsdsl-ros2 inspect double_pendulum
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Optional

from ._bridge import CompiledSystem, CoreNotInstalled, DSLCompileError, compile_spec, list_presets
from ._cppgen import render_dynamics_header
from ._packages import _PACKAGES
from ._pyscaffold import scaffold_python_package
from ._scaffold import scaffold_package


def _compile(spec: str) -> Optional[CompiledSystem]:
    try:
        return compile_spec(spec)
    except CoreNotInstalled as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
    except DSLCompileError as exc:
        print(f"DSL compilation failed: {exc}", file=sys.stderr)
        return None


def _scaffold(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1
    if args.rate <= 0:
        print("--rate must be positive", file=sys.stderr)
        return 1

    if args.lang == "python":
        root = scaffold_python_package(system, args.out, rate_hz=args.rate)
    else:
        root = scaffold_package(system, args.out, rate_hz=args.rate)
    pkg = os.path.basename(root)
    print(f"Compiled '{system.name}' ({system.dof} DOF: {', '.join(system.coordinates)})")
    print(f"Scaffolded {args.lang} ROS2 package -> {root}")
    print(f"Build with:  colcon build --packages-select {pkg}")
    print(f"Run with:    ros2 launch {pkg} {system.name}.launch.py")
    return 0


def _header(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1
    os.makedirs(args.out, exist_ok=True)
    path = os.path.join(args.out, f"{system.name}_dynamics.hpp")
    guard = f"MECHANICSDSL_{system.name.upper()}_DYNAMICS_HPP"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_dynamics_header(system, guard))
    print(f"Wrote header-only C++17 dynamics -> {path}")
    return 0


def _packages(_: argparse.Namespace) -> int:
    print("Bundled MechanicsDSL ROS2 packages:")
    for name, info in _PACKAGES.items():
        print(f"  {name}")
        print(f"    Nodes:    {', '.join(info['nodes'])}")
        print(f"    Messages: {', '.join(info['messages'])}")
    return 0


def _presets(_: argparse.Namespace) -> int:
    print("Presets shipped with mechanicsdsl-core:")
    for name in list_presets():
        print(f"  {name}")
    return 0


def _inspect(args: argparse.Namespace) -> int:
    system = _compile(args.spec)
    if system is None:
        return 1
    print(system.describe())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mechanicsdsl-ros2",
        description="Compile MechanicsDSL specs to complete ROS2 packages.",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("packages", help="List bundled ROS2 packages").set_defaults(func=_packages)
    sub.add_parser("presets", help="List core presets").set_defaults(func=_presets)

    spec_help = "Path to a .msl file, a raw DSL string, or a core preset name."
    p_scaf = sub.add_parser("scaffold", help="Scaffold a ROS2 package from a DSL spec")
    p_scaf.add_argument("spec", help=spec_help)
    p_scaf.add_argument("--out", "-o", default=".",
                        help="Output directory (typically a ROS2 workspace 'src/').")
    p_scaf.add_argument("--lang", choices=["cpp", "python"], default="cpp",
                        help="cpp: ament_cmake + rclcpp (default); python: ament_python + rclpy")
    p_scaf.add_argument("--rate", type=float, default=250.0, help="Node update rate [Hz]")
    p_scaf.set_defaults(func=_scaffold)

    p_hdr = sub.add_parser("header", help="Write only the header-only C++17 dynamics")
    p_hdr.add_argument("spec", help=spec_help)
    p_hdr.add_argument("--out", "-o", default=".", help="Output directory")
    p_hdr.set_defaults(func=_header)

    p_ins = sub.add_parser("inspect", help="Print coordinates, parameters, EOM and energy")
    p_ins.add_argument("spec", help=spec_help)
    p_ins.set_defaults(func=_inspect)
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
