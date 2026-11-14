"""
mechanicsdsl-ros2
-----------------
ROS2 integration and package scaffolding for MechanicsDSL.
Compile physical systems defined in DSL notation to complete ROS2 packages.

Quick start:
    pip install mechanicsdsl-ros2
    mechanicsdsl-ros2 scaffold pendulum.msl --out ~/ros2_ws/src/
    mechanicsdsl-ros2 scaffold pendulum.msl --lang python --out ~/ros2_ws/src/

    # Documentation and examples:
    # https://github.com/MechanicsDSL/mechanicsdsl-ros2
"""

from mechanicsdsl_ros2._version import __version__
from mechanicsdsl_ros2._packages import list_packages, get_package_path
from mechanicsdsl_ros2._bridge import (
    CompiledSystem,
    CoreNotInstalled,
    DSLCompileError,
    compile_spec,
    energy_drift,
    list_presets,
    numeric_energy,
    simulate,
)
from mechanicsdsl_ros2._cppgen import render_dynamics_header
from mechanicsdsl_ros2._scaffold import render_params_yaml, scaffold_package
from mechanicsdsl_ros2._pyscaffold import (
    render_dynamics_py,
    render_python_package,
    scaffold_python_package,
)

__all__ = [
    "__version__",
    "list_packages",
    "get_package_path",
    "compile_spec",
    "list_presets",
    "simulate",
    "numeric_energy",
    "energy_drift",
    "render_dynamics_header",
    "render_params_yaml",
    "scaffold_package",
    "render_dynamics_py",
    "render_python_package",
    "scaffold_python_package",
    "CompiledSystem",
    "CoreNotInstalled",
    "DSLCompileError",
]
