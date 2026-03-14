"""
test_pendulum_integration.py
----------------------------
ROS2 integration test for the MechanicsDSL pendulum node.
Launches the node and verifies published state matches expected physics.

Run with:
    colcon test --packages-select mechanicsdsl_pendulum
    # or directly:
    pytest test/test_pendulum_integration.py -v
"""

import time
import pytest
import math

try:
    import rclpy
    from rclpy.node import Node
    from mechanicsdsl_pendulum.msg import PendulumState
    ROS2_AVAILABLE = True
except ImportError:
    ROS2_AVAILABLE = False


@pytest.mark.skipif(not ROS2_AVAILABLE, reason="ROS2 not available")
class TestPendulumNodeIntegration:

    @classmethod
    def setup_class(cls):
        rclpy.init()
        cls.node = rclpy.create_node("test_pendulum_integration")
        cls.received = []
        cls.sub = cls.node.create_subscription(
            PendulumState,
            "/mechanicsdsl/pendulum/state",
            lambda msg: cls.received.append(msg),
            10
        )

    @classmethod
    def teardown_class(cls):
        cls.node.destroy_node()
        rclpy.shutdown()

    def spin_for(self, seconds: float):
        deadline = time.time() + seconds
        while time.time() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.01)

    def test_node_publishes_state(self):
        """Node should publish state messages within 1 second of launch."""
        self.spin_for(1.0)
        assert len(self.received) > 0, "No state messages received within 1 s"

    def test_publication_rate_near_250hz(self):
        """Publication rate should be close to 250 Hz (dt=0.004 s)."""
        self.received.clear()
        self.spin_for(1.0)
        rate = len(self.received)
        assert 200 <= rate <= 300, f"Publication rate {rate} Hz far from 250 Hz"

    def test_energy_conserved(self):
        """Energy drift should stay below 1e-3 after 5 seconds."""
        self.received.clear()
        self.spin_for(5.0)
        if not self.received:
            pytest.skip("No messages received")
        max_drift = max(msg.energy_drift for msg in self.received)
        assert max_drift < 1e-3, f"Max energy drift {max_drift:.2e} exceeds 1e-3"

    def test_theta_stays_bounded(self):
        """Angle should stay within [-2π, 2π] for default initial condition."""
        if not self.received:
            pytest.skip("No messages received")
        max_theta = max(abs(msg.theta) for msg in self.received)
        assert max_theta < 2 * math.pi, f"theta {max_theta:.3f} rad out of bounds"
