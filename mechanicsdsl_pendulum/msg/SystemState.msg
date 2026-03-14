# SystemState.msg
# ---------------
# Generic state message for MechanicsDSL multi-DOF systems.
# Used by generated nodes with more than one generalised coordinate.
#
# Author: MechanicsDSL (github.com/MechanicsDSL)

std_msgs/Header header

# Generalised coordinates q_i [mixed units per system]
float64[] q

# Generalised velocities dq_i/dt
float64[] q_dot

# Generalised accelerations d²q_i/dt²
float64[] q_ddot

# Constraint forces (Lagrange multipliers) — one per active constraint
float64[] lambda

# Total mechanical energy [J]
float64 energy

# Relative energy drift |ΔE/E0|
float64 energy_drift

# Names of conserved quantities identified by Noether analysis
string[] conserved_quantities

# Simulation time [s]
float64 sim_time
