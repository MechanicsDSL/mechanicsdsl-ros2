#!/usr/bin/env bash
# ci_colcon.sh - generate ROS2 packages with mechanicsdsl-ros2, build them with
# colcon, run their tests, and smoke-test the running nodes.
#
# Runs inside an official ROS2 image (ros:humble, ros:jazzy):
#   docker run --rm -v "$PWD":/src -w /src ros:humble bash scripts/ci_colcon.sh
#
# Exits non-zero on the first failure.
set -euo pipefail

: "${ROS_DISTRO:?run this inside a ROS2 environment (ROS_DISTRO unset)}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WS="${WS:-/tmp/mdsl_ws}"
SYSTEMS="${SYSTEMS:-pendulum double_pendulum}"
export MECHANICSDSL_NO_BANNER=1

echo "::group::apt dependencies"
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  python3-venv python3-colcon-common-extensions \
  "ros-${ROS_DISTRO}-ament-cmake-gtest" "ros-${ROS_DISTRO}-std-srvs" \
  "ros-${ROS_DISTRO}-sensor-msgs" "ros-${ROS_DISTRO}-launch-ros" >/dev/null
echo "::endgroup::"

# The generator lives in its own venv: pip must not touch the distro's Python
# packages (on Ubuntu 24.04 / jazzy it cannot uninstall Debian's numpy). The
# generated nodes themselves run on the system Python with ROS's rclpy.
echo "::group::install mechanicsdsl-ros2"
GEN_VENV=/tmp/mdsl_gen_venv
python3 -m venv "$GEN_VENV"
"$GEN_VENV/bin/python" -m pip install -q --upgrade pip
"$GEN_VENV/bin/python" -m pip install -q "$REPO"
GEN="$GEN_VENV/bin/mechanicsdsl-ros2"
echo "::endgroup::"

rm -rf "$WS" && mkdir -p "$WS/src"
for s in $SYSTEMS; do
  "$GEN" scaffold "$s" --lang cpp -o "$WS/src"
  "$GEN" scaffold "$s" --lang python -o "$WS/src"
done

# ROS setup scripts reference unset variables; relax -u while sourcing.
set +u
source "/opt/ros/${ROS_DISTRO}/setup.bash"
set -u

cd "$WS"
echo "::group::colcon build"
colcon build --event-handlers console_direct+ --cmake-args -DCMAKE_BUILD_TYPE=Release
echo "::endgroup::"

echo "::group::colcon test"
colcon test --event-handlers console_direct+ --ctest-args --output-on-failure
colcon test-result --verbose
echo "::endgroup::"

set +u
source "$WS/install/setup.bash"
set -u

smoke() {  # smoke <package> <executable> <system> <param>
  local pkg="$1" exe="$2" sys="$3" param="$4" pid
  echo "::group::smoke $pkg"
  ros2 run "$pkg" "$exe" >"/tmp/$pkg.log" 2>&1 &
  pid=$!
  trap 'kill $pid 2>/dev/null || true' RETURN
  # Wait for DDS discovery: echoing before the publisher is seen fails with
  # "Could not determine the type for the passed topic".
  local waited=0
  until ros2 topic list 2>/dev/null | grep -qx "/$sys/joint_states"; do
    sleep 1; waited=$((waited + 1))
    if [ "$waited" -ge 30 ]; then
      echo "topic /$sys/joint_states never appeared"; cat "/tmp/$pkg.log"; return 1
    fi
  done
  timeout 30 ros2 topic echo --once "/$sys/joint_states" | head -20
  timeout 30 ros2 service call "/$sys/reset" std_srvs/srv/Trigger | tail -2
  timeout 30 ros2 param set "/${sys}_node" "$param" 3.7
  [ "$(timeout 30 ros2 param get "/${sys}_node" "$param")" = "Double value is: 3.7" ]
  kill "$pid"; wait "$pid" 2>/dev/null || true
  echo "node log:"; cat "/tmp/$pkg.log"
  echo "::endgroup::"
}

for s in $SYSTEMS; do
  name="$("$GEN_VENV/bin/python" -c "import mechanicsdsl_ros2 as m; print(m.compile_spec('$s').name)" 2>/dev/null | tail -1)"
  smoke "mechanicsdsl_${name}" "${name}_node" "$name" g
  smoke "mechanicsdsl_${name}_py" "${name}_node" "$name" g
done
echo "colcon build, tests and node smoke tests passed for: $SYSTEMS"
