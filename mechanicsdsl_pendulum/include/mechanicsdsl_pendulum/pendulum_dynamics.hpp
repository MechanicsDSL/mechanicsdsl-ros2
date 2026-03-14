/**
 * pendulum_dynamics.hpp
 * ---------------------
 * MechanicsDSL-generated header: equations of motion and Hamiltonian
 * for the simple pendulum, suitable for inclusion in ROS2 nodes
 * and other C++ targets.
 *
 * DSL specification:
 *   \system{pendulum}
 *   \lagrangian{0.5*m*l^2*\dot{theta}^2 - m*g*l*(1-cos(theta))}
 *   \target{cpp_header}
 *
 * Author: MechanicsDSL (github.com/MechanicsDSL)
 * License: MIT
 */

#pragma once

#include <cmath>
#include <array>

namespace mechanicsdsl {
namespace classical {

/// Physical parameters for the simple pendulum.
struct PendulumParams {
    double m   = 1.0;    ///< Mass [kg]
    double l   = 0.25;   ///< Rod length [m]
    double g   = 9.81;   ///< Gravitational acceleration [m/s^2]
};

/// State vector: [theta (rad), omega (rad/s)]
using PendulumState = std::array<double, 2>;

/**
 * @brief MechanicsDSL-generated equation of motion.
 *
 * Derived from Euler-Lagrange applied to:
 *   L = 0.5*m*l^2*omega^2 - m*g*l*(1-cos(theta))
 *
 * Result: d(omega)/dt = -(g/l)*sin(theta)
 *
 * @param theta  Angle from vertical [rad]
 * @param p      Physical parameters
 * @return       Angular acceleration [rad/s^2]
 */
[[nodiscard]] inline double pendulum_domega(double theta,
                                             const PendulumParams& p) noexcept {
    return -(p.g / p.l) * std::sin(theta);
}

/**
 * @brief MechanicsDSL-generated Hamiltonian (Noether conserved energy).
 *
 * H = 0.5*m*l^2*omega^2 + m*g*l*(1-cos(theta))
 * Conserved by time-translation symmetry (Noether's theorem).
 *
 * @param state  [theta, omega]
 * @param p      Physical parameters
 * @return       Total mechanical energy [J]
 */
[[nodiscard]] inline double pendulum_hamiltonian(const PendulumState& state,
                                                  const PendulumParams& p) noexcept {
    const double T = 0.5 * p.m * p.l * p.l * state[1] * state[1];
    const double V = p.m * p.g * p.l * (1.0 - std::cos(state[0]));
    return T + V;
}

/**
 * @brief Runge-Kutta 4 integration step for the pendulum.
 *
 * @param state  Current [theta, omega] — updated in place
 * @param dt     Timestep [s]
 * @param p      Physical parameters
 */
inline void pendulum_rk4_step(PendulumState& state, double dt,
                               const PendulumParams& p) noexcept {
    const double k1_th = state[1];
    const double k1_om = pendulum_domega(state[0], p);

    const double k2_th = state[1] + 0.5*dt*k1_om;
    const double k2_om = pendulum_domega(state[0] + 0.5*dt*k1_th, p);

    const double k3_th = state[1] + 0.5*dt*k2_om;
    const double k3_om = pendulum_domega(state[0] + 0.5*dt*k2_th, p);

    const double k4_th = state[1] + dt*k3_om;
    const double k4_om = pendulum_domega(state[0] + dt*k3_th, p);

    state[0] += (dt / 6.0) * (k1_th + 2*k2_th + 2*k3_th + k4_th);
    state[1] += (dt / 6.0) * (k1_om + 2*k2_om + 2*k3_om + k4_om);
}

} // namespace classical
} // namespace mechanicsdsl
