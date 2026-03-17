"""
mechanicsdsl-ros2
-----------------
ROS2 integration and package scaffolding for MechanicsDSL.
Compile physical systems defined in DSL notation to complete ROS2 packages.

Quick start:
    pip install mechanicsdsl-ros2
    mechanicsdsl-ros2 scaffold pendulum.msl --out ~/ros2_ws/src/

    # Documentation and examples:
    # https://github.com/MechanicsDSL/mechanicsdsl-ros2
"""

from mechanicsdsl_ros2._version import __version__
from mechanicsdsl_ros2._packages import list_packages, get_package_path

__all__ = ["__version__", "list_packages", "get_package_path"]
