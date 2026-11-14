# Changelog

## [0.2.0] - 2026-11-14

### Added
- `--lang python`: a pure-Python `ament_python` / rclpy package whose `dynamics.py` uses only the standard library.
- Generated nodes publish `sensor_msgs/JointState`, report energy and energy drift, accept live parameter updates (`ros2 param set`), take `substeps` and `paused` parameters, and offer a `<system>/reset` `std_srvs/Trigger` service.
- C++ packages include a gtest (finite state; energy conservation for conservative systems) wired into CMake.
- `header`, `inspect`, `presets` commands and `--rate`.
- The C++ dynamics header gains `initial_state()`, `energy()`, CSE, and overloads so several systems can share one translation unit.
- Shared bridge to core: energy E = sum(qdot dL/dqdot) - L derived from the Lagrangian, a `conservative` flag, `simulate()` (fixed-step RK4 reference), `energy_drift()`, `operation_count()`, `list_presets()`, and `CompiledSystem.describe()`.
- Core's mass-matrix output (`__mass_matrix__`, used for large systems such as the three-body `figure8` preset) is converted to explicit accelerations, so every core preset now generates.

### Fixed
- The generated launch file never loaded the parameter YAML (`parameters=[...] if False else []`), and the YAML used a node key that matched no node. The launch file now loads `config/<system>_params.yaml`, keyed `/**`.
- `get_package_path()` looked for a local clone one directory above the repository.
- Internal identifiers are prefixed so they cannot collide with user names (generated Python broke for a coordinate named `y`).

### Infrastructure
- CI workflow: pytest on Python 3.9-3.12 (Linux) plus Windows and macOS, a syntax/undefined-name lint, and an sdist/wheel build check.
- Dependabot (pip and GitHub Actions), issue and PR templates, pre-commit config, `SECURITY.md`, `CODE_OF_CONDUCT.md`.
- Single-source version (`_version.py`, read by hatch); requires `mechanicsdsl-core>=2.1.4`.

## [Unreleased]

### Added
- `mechanicsdsl_pendulum` ROS2 package with full pendulum dynamics node
- Custom messages: `PendulumState.msg`, `SystemState.msg`
- Launch files: `pendulum.launch.py`
- Parameter config: `pendulum_params.yaml`
- C++ dynamics header: `pendulum_dynamics.hpp`
- GTest unit tests: `test_pendulum_eom.cpp`
- Docker environment for ROS2 Jazzy
- Build scripts and documentation

## [0.1.0] — 2026-03-13

- Initial repository scaffold
