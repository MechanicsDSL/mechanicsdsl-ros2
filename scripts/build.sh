#!/bin/bash
# build.sh
# --------
# Builds the mechanicsdsl_pendulum ROS2 package and optionally runs
# the pendulum node demo.
#
# Usage:
#   ./scripts/build.sh           # Build only
#   ./scripts/build.sh --run     # Build and run pendulum node
#   ./scripts/build.sh --docker  # Build inside Docker

set -e
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

if [[ "$1" == "--docker" ]]; then
    echo "Building in Docker..."
    docker build -t mechanicsdsl-ros2:jazzy "$REPO_ROOT/docker/"
    docker run --rm -it mechanicsdsl-ros2:jazzy bash -c \
        "source /opt/ros/jazzy/setup.bash && source /ros2_ws/install/setup.bash && \
         ros2 launch mechanicsdsl_pendulum pendulum.launch.py"
    exit 0
fi

# Source ROS2
if [ -f /opt/ros/jazzy/setup.bash ]; then
    source /opt/ros/jazzy/setup.bash
elif [ -f /opt/ros/iron/setup.bash ]; then
    source /opt/ros/iron/setup.bash
elif [ -f /opt/ros/humble/setup.bash ]; then
    source /opt/ros/humble/setup.bash
else
    echo "Error: No ROS2 installation found."
    exit 1
fi

# Build
WS="$REPO_ROOT/../.."
cd "$WS"
colcon build --packages-select mechanicsdsl_pendulum --symlink-install
source install/setup.bash

echo "Build complete."

if [[ "$1" == "--run" ]]; then
    echo "Launching pendulum node..."
    ros2 launch mechanicsdsl_pendulum pendulum.launch.py
fi
