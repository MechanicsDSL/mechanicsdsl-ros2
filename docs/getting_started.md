# Getting Started with mechanicsdsl-ros2

## Prerequisites

- ROS2 Humble, Iron, or Jazzy
- `mechanicsdsl-core` Python package (`pip install mechanicsdsl-core`)
- Standard ROS2 build tools (`colcon`, `rosdep`)

---

## Installation

### From Source

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/MechanicsDSL/mechanicsdsl-ros2.git
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select mechanicsdsl_pendulum
source install/setup.bash
```

### Docker

```bash
docker build -t mechanicsdsl-ros2:jazzy docker/
docker run --rm -it mechanicsdsl-ros2:jazzy
```

---

## Running the Pendulum Node

```bash
# Default parameters
ros2 launch mechanicsdsl_pendulum pendulum.launch.py

# Custom rod length and initial angle
ros2 launch mechanicsdsl_pendulum pendulum.launch.py l_m:=0.5 theta0_rad:=0.8

# Using params file
ros2 run mechanicsdsl_pendulum pendulum_node \
    --ros-args --params-file mechanicsdsl_pendulum/config/pendulum_params.yaml
```

---

## Subscribing to State

```bash
# Watch state topic
ros2 topic echo /mechanicsdsl/pendulum/state

# Check publication rate
ros2 topic hz /mechanicsdsl/pendulum/state

# Plot energy in rqt
rqt_plot /mechanicsdsl/pendulum/state/energy
```

---

## Resetting and Parameter Updates

```bash
# Reset to initial conditions
ros2 topic pub --once /pendulum/reset std_msgs/msg/Bool "data: true"

# Update parameters live (m, l, g as Vector3 x, y, z)
ros2 topic pub --once /pendulum/set_params geometry_msgs/msg/Vector3 \
    "{x: 1.5, y: 0.3, z: 9.81}"
```

---

## Topics

| Topic | Type | Direction | Rate |
|-------|------|-----------|------|
| `/mechanicsdsl/pendulum/state` | `PendulumState` | Published | 250 Hz |
| `/mechanicsdsl/pendulum/energy` | `Float64` | Published | 250 Hz |
| `/pendulum/reset` | `Bool` | Subscribed | On demand |
| `/pendulum/set_params` | `Vector3` | Subscribed | On demand |

---

## Running Tests

```bash
colcon test --packages-select mechanicsdsl_pendulum
colcon test-result --verbose
```
