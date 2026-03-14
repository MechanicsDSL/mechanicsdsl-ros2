# Architecture

## Overview

mechanicsdsl-ros2 follows a clean separation between the physics layer (MechanicsDSL-generated C++) and the ROS2 communication layer.

```
┌─────────────────────────────────────────────────────────┐
│                    mechanicsdsl-ros2                     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              ROS2 Node Layer                     │   │
│  │  pendulum_node.cpp / double_pendulum_node.cpp    │   │
│  │  ┌──────────────┐  ┌──────────────────────────┐ │   │
│  │  │  Publishers   │  │     Subscribers          │ │   │
│  │  │  /state       │  │  /reset  /set_params     │ │   │
│  │  │  /energy      │  │                          │ │   │
│  │  └──────────────┘  └──────────────────────────┘ │   │
│  └───────────────────────────────────────────────── ┘   │
│                         │                               │
│  ┌──────────────────────▼──────────────────────────┐   │
│  │         MechanicsDSL Physics Layer               │   │
│  │   pendulum_dynamics.hpp (generated header)       │   │
│  │   ┌──────────────┐  ┌──────────────────────┐    │   │
│  │   │  EOM          │  │  Hamiltonian          │   │   │
│  │   │  (Euler-Lag.) │  │  (Noether conserved)  │   │   │
│  │   └──────────────┘  └──────────────────────┘    │   │
│  │   ┌──────────────────────────────────────────┐   │   │
│  │   │           RK4 Integrator                 │   │   │
│  │   └──────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Message Types

| Message | Fields | Publisher |
|---------|--------|-----------|
| `PendulumState` | theta, omega, energy, energy_drift, sim_time | pendulum_node |
| `SystemState` | q[], q_dot[], lambda[], energy, conserved_quantities | double_pendulum_node |

## Adding a New System

1. Write the DSL specification: `system.msl`
2. Generate the ROS2 package: `mechanicsdsl generate system.msl --target ros2`
3. The generator produces:
   - `<system>_node.cpp` with Hamilton's equations
   - `<System>State.msg`
   - `<system>.launch.py`
   - `<system>_params.yaml`
4. Add the new executable to `CMakeLists.txt`
5. Build: `colcon build --packages-select mechanicsdsl_pendulum`

## Conservation Monitoring

Every generated node includes Noether-based conservation monitoring. When `|ΔE/E₀|` exceeds `drift_tol`, a `RCLCPP_WARN_THROTTLE` is emitted at 1 Hz. This is configurable via the ROS2 parameter server at runtime.
