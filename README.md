<p align="center">
  <img src="https://raw.githubusercontent.com/MechanicsDSL/mechanicsdsl/main/docs/images/logo.png" alt="MechanicsDSL Logo" width="360">
</p>

<h1 align="center">mechanicsdsl-ros2</h1>

<p align="center">
  <em>Compile MechanicsDSL physical systems directly to complete ROS2 packages.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/status-active-green" alt="Active">
  <img src="https://img.shields.io/badge/ROS2-Humble%20%7C%20Iron%20%7C%20Jazzy-blue" alt="ROS2">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License"></a>
  <a href="https://github.com/MechanicsDSL/mechanicsdsl"><img src="https://img.shields.io/badge/core-mechanicsdsl-blue" alt="Core Package"></a>
</p>


## Who's Using MechanicsDSL?

We can see from our download analytics that MechanicsDSL is being used across **54+ countries** and mirrored by institutions worldwide — but PyPI doesn't tell us who you are.

If you're using MechanicsDSL in research, education, industry, or a personal project, we'd love to hear from you. It takes 60 seconds and helps guide the project's direction.

**[→ Tell us about your use case](https://tally.so/r/XxqOqP)**

*All responses are voluntary and confidential. We will not contact you without permission.*

---

## Overview

`mechanicsdsl-ros2` provides a dedicated ROS2 integration layer for MechanicsDSL. Physical systems defined in DSL notation compile to complete, buildable ROS2 packages — no manual C++ required for the physics layer.

---

## Package: `mechanicsdsl_pendulum`

The first generated package, currently including:

### Nodes

| Node | System | Rate | Topics |
|------|--------|------|--------|
| `pendulum_node` | Simple pendulum | 250 Hz | `/mechanicsdsl/pendulum/state`, `/mechanicsdsl/pendulum/energy` |
| `double_pendulum_node` | Double pendulum | 200 Hz | `/double_pendulum/state` |

### Messages

| Message | Fields |
|---------|--------|
| `PendulumState` | `header`, `theta`, `omega`, `energy`, `energy_drift`, `sim_time` |
| `SystemState` | `header`, `q[]`, `q_dot[]`, `q_ddot[]`, `lambda[]`, `energy`, `energy_drift`, `conserved_quantities[]`, `sim_time` |

### Launch Files

```bash
ros2 launch mechanicsdsl_pendulum pendulum.launch.py
ros2 launch mechanicsdsl_pendulum pendulum.launch.py l_m:=0.5 theta0_rad:=0.8
ros2 launch mechanicsdsl_pendulum double_pendulum.launch.py theta1_0:=0.3 theta2_0:=0.2
```

---

## Repository Structure

```
mechanicsdsl-ros2/
├── mechanicsdsl_pendulum/
│   ├── package.xml, CMakeLists.txt
│   ├── msg/  PendulumState.msg, SystemState.msg
│   ├── src/  pendulum_node.cpp, double_pendulum_node.cpp
│   ├── include/mechanicsdsl_pendulum/  pendulum_dynamics.hpp
│   ├── launch/  pendulum.launch.py, double_pendulum.launch.py
│   ├── config/  pendulum_params.yaml
│   └── test/  test_pendulum_eom.cpp, test_pendulum_integration.py
├── docker/  Dockerfile (ROS2 Jazzy + MechanicsDSL)
├── scripts/  build.sh, monitor.sh
└── docs/  getting_started.md, architecture.md, adding_systems.md
```

---

## Quick Start

```bash
# Clone into ROS2 workspace
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone https://github.com/MechanicsDSL/mechanicsdsl-ros2.git

# Build
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select mechanicsdsl_pendulum
source install/setup.bash

# Run
ros2 launch mechanicsdsl_pendulum pendulum.launch.py
```

**Docker:**

```bash
docker build -t mechanicsdsl-ros2:jazzy docker/
docker run --rm -it mechanicsdsl-ros2:jazzy
```

---

## Monitoring

```bash
ros2 topic echo /mechanicsdsl/pendulum/state
ros2 topic hz  /mechanicsdsl/pendulum/state   # should be ~250 Hz

# Reset
ros2 topic pub --once /pendulum/reset std_msgs/msg/Bool "data: true"
```

---

## Testing

```bash
colcon test --packages-select mechanicsdsl_pendulum
colcon test-result --verbose
```

GTests cover EOM correctness, energy conservation, equilibrium stability, and small-angle period accuracy.

---

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full node/message/layer diagram.

## Adding New Systems

See [docs/adding_systems.md](docs/adding_systems.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License — see [LICENSE](LICENSE).
