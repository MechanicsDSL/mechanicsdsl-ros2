<p align="center">
  <img src="https://raw.githubusercontent.com/MechanicsDSL/mechanicsdsl/main/docs/images/logo.png" alt="MechanicsDSL Logo" width="360">
</p>

<h1 align="center">mechanicsdsl-ros2</h1>

<p align="center">
  <em>Compile physical systems directly to ROS2 node packages.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-planned-lightgrey" alt="Status: Planned">
  <img src="https://img.shields.io/badge/ROS2-Humble%20%7C%20Iron%20%7C%20Jazzy-blue" alt="ROS2 Versions">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <a href="https://github.com/MechanicsDSL/mechanicsdsl"><img src="https://img.shields.io/badge/core-mechanicsdsl-blue" alt="Core Package"></a>
</p>

---

## Overview

`mechanicsdsl-ros2` provides a dedicated integration layer between the MechanicsDSL compiler and the Robot Operating System (ROS2). Define manipulator dynamics, mobile robot kinematics, or any constrained mechanical system in DSL notation — the compiler generates a complete, buildable ROS2 package with auto-generated `CMakeLists.txt`, message definitions, topic publishers, and launch files.

---

## Planned Capabilities

### Package Generation
- **Complete ROS2 packages** — Auto-generated `package.xml`, `CMakeLists.txt`, node source, and launch files from a single DSL specification
- **Message definitions** — Custom `.msg` files for generalized coordinates, velocities, constraint forces, and conservation law monitoring
- **Topic architecture** — State publisher, reference subscriber, and diagnostics publisher nodes with configurable QoS profiles
- **Real-time support** — `rclcpp` real-time executor compatibility; priority scheduling configuration for control loops

### Supported Use Cases
- **Manipulator dynamics** — Forward and inverse dynamics nodes for serial-chain and parallel robot arms
- **Mobile robot kinematics** — Differential drive, omnidirectional, and legged locomotion models
- **Constraint-aware control** — Holonomic and non-holonomic constraint forces published as wrench topics
- **State estimation** — Sensor fusion nodes combining DSL-derived dynamics with IMU and encoder measurements

### Example Packages
- 2-DOF planar manipulator with real-time torque feedforward control
- Differential drive mobile robot with constraint-enforced no-slip kinematics
- Pendulum-on-cart system with LQR stabilization
- Coupled oscillator state estimation from noisy sensor topics

### Tooling
- `mechanicsdsl-ros2 generate <dsl_file>` — CLI to scaffold a complete ROS2 package
- `mechanicsdsl-ros2 verify <package_dir>` — Validate generated package builds cleanly against target ROS2 distro
- Docker image with ROS2 Jazzy + MechanicsDSL pre-installed for zero-setup development

---

## Relationship to Core Package

This repository provides ROS2-specific scaffolding and examples. The symbolic engine and C++ code generation live in [mechanicsdsl](https://github.com/MechanicsDSL/mechanicsdsl):

```bash
pip install mechanicsdsl-core
```

The generated C++ is compatible with any ROS2 Humble, Iron, or Jazzy installation with no additional Python dependencies at runtime.

---

## Status

This repository is in the planning stage. The core package already generates ROS2-compatible C++; this repository will formalize the package scaffolding, CLI tooling, and worked examples. Watch this repository for updates.

---

## Contributing

Contributions welcome — particularly ROS2 integration examples and real hardware validation. See [CONTRIBUTING.md](https://github.com/MechanicsDSL/mechanicsdsl/blob/main/CONTRIBUTING.md).

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://github.com/MechanicsDSL/mechanicsdsl">Core Package</a> ·
  <a href="https://mechanicsdsl.readthedocs.io">Documentation</a> ·
  <a href="https://doi.org/10.5281/zenodo.17771040">Zenodo DOI</a>
</p>
