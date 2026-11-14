"""
test_scaffold.py
----------------
Exercises the real DSL -> ROS2 package scaffolding pipeline.

Run with: pytest tests/test_scaffold.py -v
"""
import pytest

pytest.importorskip(
    "mechanics_dsl", reason="mechanicsdsl-core required for scaffolding tests"
)

from mechanicsdsl_ros2 import compile_spec, scaffold_package
from mechanicsdsl_ros2._cppgen import render_dynamics_header
from mechanicsdsl_ros2.cli import main as cli_main


EXPECTED_FILES = [
    "package.xml",
    "CMakeLists.txt",
    "msg/SystemState.msg",
]


def test_scaffold_produces_complete_package(tmp_path):
    system = compile_spec("pendulum")
    root = scaffold_package(system, str(tmp_path))
    import os

    name = system.name  # 'pendulum' preset compiles to 'simple_pendulum'
    for rel in EXPECTED_FILES:
        assert os.path.isfile(os.path.join(root, rel)), f"missing {rel}"
    node = os.path.join(root, "src", f"{name}_node.cpp")
    hdr = os.path.join(
        root, "include", f"mechanicsdsl_{name}", f"{name}_dynamics.hpp"
    )
    assert os.path.isfile(node)
    assert os.path.isfile(hdr)


def test_header_embeds_real_eom():
    system = compile_spec("pendulum")
    hdr = render_dynamics_header(system, "GUARD_H")
    # Real derived physics transcribed by cxxcode.
    assert "std::sin(theta)" in hdr
    assert "rk4_step" in hdr
    assert "PendulumParams" in hdr


def test_double_pendulum_is_two_dof():
    system = compile_spec("double_pendulum")
    hdr = render_dynamics_header(system, "GUARD_H")
    assert "qdd[0]" in hdr and "qdd[1]" in hdr
    assert "DOF = 2" in hdr


def test_cli_scaffold_returns_zero(tmp_path):
    rc = cli_main(["scaffold", "pendulum", "-o", str(tmp_path)])
    assert rc == 0
