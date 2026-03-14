# Contributing to mechanicsdsl-ros2

## Contribution Types

### New System Nodes

Generate a new node from a DSL specification and submit it:

```bash
mechanicsdsl generate my_system.msl --target ros2 --package-name mechanicsdsl_my_system
```

Include in your PR:
- The originating `.msl` specification
- A `launch/` file
- A `config/` params YAML
- At least one GTest unit test
- An updated `CMakeLists.txt` entry

### Hardware Validation

If you've run a generated node on real robot hardware, a validation report (even informal) is very valuable. Open an issue with the `hardware-validation` label describing:
- Robot platform and ROS2 distro
- Which node(s) were tested
- Integration rate achieved
- Any issues encountered

### Launch File Improvements

Multi-node launch files composing several MechanicsDSL systems together are welcome — for example, a cart-pendulum with separate pendulum and cart nodes.

## Testing

```bash
colcon build --packages-select mechanicsdsl_pendulum
colcon test --packages-select mechanicsdsl_pendulum
colcon test-result --verbose
```

All GTests must pass. New nodes must include at least:
- Energy conservation test (10+ seconds)
- Equilibrium stability test
- Small-angle period validation (if applicable)

## Style

- Follow ROS2 C++ style guide
- All generated code must include the originating DSL specification as a header comment
- Parameter names must match the DSL `\parameter` block names exactly
