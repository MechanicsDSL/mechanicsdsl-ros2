/**
 * test_pendulum_eom.cpp
 * ---------------------
 * GTest unit tests for MechanicsDSL-generated pendulum equations of motion.
 * Validates physics correctness independently of ROS2.
 *
 * Run with: colcon test --packages-select mechanicsdsl_pendulum
 */

#include <gtest/gtest.h>
#include <cmath>
#include "mechanicsdsl_pendulum/pendulum_dynamics.hpp"

using namespace mechanicsdsl::classical;

static constexpr double PI = M_PI;
static constexpr double TOL = 1e-6;


// ---------------------------------------------------------------------------
// EOM correctness
// ---------------------------------------------------------------------------
TEST(PendulumEOM, EquilibriumAtZero) {
    PendulumParams p;
    EXPECT_NEAR(pendulum_domega(0.0, p), 0.0, 1e-15);
}

TEST(PendulumEOM, EquilibriumAtPi) {
    // Unstable equilibrium: sin(π)=0
    PendulumParams p;
    EXPECT_NEAR(pendulum_domega(PI, p), 0.0, 1e-14);
}

TEST(PendulumEOM, MaxForceAtQuarterPeriod) {
    // At theta=pi/2: domega = -(g/l)*1
    PendulumParams p{1.0, 1.0, 9.81};
    EXPECT_NEAR(pendulum_domega(PI/2.0, p), -9.81, 1e-12);
}

TEST(PendulumEOM, SmallAngleLinearApproximation) {
    // For small theta: sin(theta) ≈ theta, so domega ≈ -(g/l)*theta
    PendulumParams p{1.0, 0.25, 9.81};
    const double theta = 0.001;
    const double linear = -(p.g/p.l)*theta;
    const double nonlinear = pendulum_domega(theta, p);
    EXPECT_NEAR(nonlinear, linear, 1e-8);
}


// ---------------------------------------------------------------------------
// Energy conservation (Noether)
// ---------------------------------------------------------------------------
TEST(PendulumHamiltonian, EnergyConservationRK4) {
    PendulumParams p{1.0, 0.25, 9.81};
    PendulumState s{0.3, 0.0};
    const double E0 = pendulum_hamiltonian(s, p);

    const double dt = 0.001;
    const int steps = 10000;  // 10 seconds

    for (int i = 0; i < steps; ++i) {
        pendulum_rk4_step(s, dt, p);
    }

    const double E_final = pendulum_hamiltonian(s, p);
    const double drift = std::abs((E_final - E0) / E0);
    EXPECT_LT(drift, 1e-5) << "Energy drift exceeded tolerance: " << drift;
}

TEST(PendulumHamiltonian, ZeroEnergyAtEquilibrium) {
    PendulumParams p;
    PendulumState s{0.0, 0.0};
    EXPECT_NEAR(pendulum_hamiltonian(s, p), 0.0, 1e-15);
}

TEST(PendulumHamiltonian, EnergyPositiveDefiniteAboveEquilibrium) {
    PendulumParams p;
    PendulumState s{0.5, 0.1};
    EXPECT_GT(pendulum_hamiltonian(s, p), 0.0);
}


// ---------------------------------------------------------------------------
// RK4 integrator
// ---------------------------------------------------------------------------
TEST(PendulumRK4, SmallAnglePeriod) {
    // Period should match T = 2π√(l/g) for small angles
    PendulumParams p{1.0, 0.25, 9.81};
    const double T_analytical = 2.0 * PI * std::sqrt(p.l / p.g);
    const double dt = 0.0001;
    const int max_steps = static_cast<int>(3 * T_analytical / dt) + 1;

    PendulumState s{0.01, 0.0};  // small angle
    double prev_theta = s[0];
    std::vector<double> crossings;

    for (int i = 0; i < max_steps && crossings.size() < 4; ++i) {
        pendulum_rk4_step(s, dt, p);
        if (prev_theta > 0 && s[0] <= 0) {
            crossings.push_back(i * dt);
        }
        prev_theta = s[0];
    }

    ASSERT_GE(crossings.size(), 4u) << "Not enough zero crossings found";
    const double T_numerical = 2.0 * (crossings[2] - crossings[0]);
    EXPECT_NEAR(T_numerical, T_analytical, 0.001)
        << "Numerical period " << T_numerical
        << " differs from analytical " << T_analytical;
}


int main(int argc, char** argv) {
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
