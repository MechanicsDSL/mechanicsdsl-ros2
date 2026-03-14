# Adding New Systems to mechanicsdsl-ros2

## Overview

Any physical system definable in MechanicsDSL DSL notation can be compiled to a ROS2 package. This guide covers the full workflow.

---

## Step 1: Write the DSL Specification

```
\system{spring_mass}
\parameter{m}{1.0}{kg}
\parameter{k}{10.0}{N/m}
\lagrangian{0.5*m*\dot{x}^2 - 0.5*k*x^2}
\initial{x: 0.5, x_dot: 0.0}
\target{ros2}
```

---

## Step 2: Generate the ROS2 Package

```bash
pip install mechanicsdsl-core

mechanicsdsl generate spring_mass.msl --target ros2 \
    --package-name mechanicsdsl_spring_mass \
    --out ~/ros2_ws/src/
```

Generated files:
```
mechanicsdsl_spring_mass/
├── package.xml
├── CMakeLists.txt
├── msg/SpringMassState.msg
├── src/spring_mass_node.cpp
├── launch/spring_mass.launch.py
└── config/spring_mass_params.yaml
```

---

## Step 3: Build

```bash
cd ~/ros2_ws
colcon build --packages-select mechanicsdsl_spring_mass
source install/setup.bash
```

---

## Step 4: Run

```bash
ros2 launch mechanicsdsl_spring_mass spring_mass.launch.py
ros2 topic echo /spring_mass/state
```

---

## Manual Implementation Template

Every generated node follows this structure:

```cpp
// 1. MechanicsDSL-generated EOM (Euler-Lagrange)
static double eom_ddq(double q, double dq, /* params */) {
    return /* generated expression */;
}

// 2. MechanicsDSL-generated Hamiltonian
static double hamiltonian(double q, double dq, /* params */) {
    return /* T + V */;
}

// 3. RK4 step
static void rk4_step(double& q, double& dq, double dt, /* params */) { /* ... */ }

// 4. Timer callback: integrate → monitor → publish
void timer_callback() {
    rk4_step(q_, dq_, dt_, /* params */);
    t_ += dt_;
    const double E = hamiltonian(q_, dq_, /* params */);
    const double drift = std::abs((E - E0_) / E0_);
    if (drift > drift_tol_)
        RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 1000,
            "Energy drift %.2e", drift);
    auto msg = SystemState();
    msg.q     = {q_};
    msg.q_dot = {dq_};
    msg.energy = E;
    pub_->publish(msg);
}
```

---

## Supported DSL Features in ROS2 Target

| Feature | Support |
|---------|---------|
| Holonomic constraints | ✅ Baumgarte stabilization |
| Conservation laws | ✅ Noether monitor + WARN |
| Multiple DOF | ✅ SystemState message |
| Parameter server | ✅ All `\parameter` values |
| Live parameter update | ✅ Via Vector3 topic |
| Custom message types | ✅ Generated per system |
