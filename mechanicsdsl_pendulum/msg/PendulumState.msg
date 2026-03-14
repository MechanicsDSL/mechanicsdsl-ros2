# PendulumState.msg
# ------------------
# State message for MechanicsDSL-generated pendulum dynamics node.
# Published at the configured integration rate (default 250 Hz).
#
# Author: MechanicsDSL (github.com/MechanicsDSL)

# Header with timestamp and frame ID
std_msgs/Header header

# Generalised coordinate: angle from vertical [rad]
float64 theta

# Generalised velocity: angular rate [rad/s]
float64 omega

# Hamiltonian (total mechanical energy) [J]
# Conserved by Noether's theorem (time-translation symmetry).
float64 energy

# Relative energy drift |ΔE/E0| [-]
# MechanicsDSL Noether monitor. Exceeding threshold triggers WARN.
float64 energy_drift

# Simulation time [s] (may differ from header.stamp if real-time offset)
float64 sim_time
