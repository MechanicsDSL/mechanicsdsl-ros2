#!/bin/bash
# monitor.sh
# ----------
# Convenience script to monitor MechanicsDSL ROS2 topics.
# Shows state, energy, and publication rate in a compact summary.
#
# Usage:
#   ./scripts/monitor.sh                  # monitor pendulum
#   ./scripts/monitor.sh double_pendulum  # monitor double pendulum
#   ./scripts/monitor.sh --hz             # show topic rates only

set -e

SYSTEM="${1:-pendulum}"
SHOW_HZ="${1:---hz}"

source_ros() {
    for f in /opt/ros/jazzy/setup.bash /opt/ros/iron/setup.bash /opt/ros/humble/setup.bash; do
        [[ -f "$f" ]] && { source "$f"; return; }
    done
    echo "Error: ROS2 not found"; exit 1
}

source_ros

if [[ "$SHOW_HZ" == "--hz" ]]; then
    echo "=== Publication rates ==="
    ros2 topic hz /mechanicsdsl/pendulum/state &
    ros2 topic hz /double_pendulum/state &
    wait
    exit 0
fi

echo "=== MechanicsDSL ROS2 Monitor: $SYSTEM ==="
echo ""
echo "Topics:"
ros2 topic list | grep -i "$SYSTEM" || echo "  (none found — is the node running?)"
echo ""
echo "Latest state (Ctrl+C to stop):"
if [[ "$SYSTEM" == "double_pendulum" ]]; then
    ros2 topic echo /double_pendulum/state --once
else
    ros2 topic echo /mechanicsdsl/pendulum/state --once
fi
