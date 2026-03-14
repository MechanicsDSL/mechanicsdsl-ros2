FROM ros:jazzy-ros-base

LABEL maintainer="nomapa223@gmail.com"
LABEL description="MechanicsDSL ROS2 development environment (ROS2 Jazzy)"

# Install build tools and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    ros-jazzy-rclcpp \
    ros-jazzy-std-msgs \
    ros-jazzy-geometry-msgs \
    ros-jazzy-sensor-msgs \
    && rm -rf /var/lib/apt/lists/*

# Install MechanicsDSL
RUN pip3 install mechanicsdsl-core --break-system-packages

# Set up workspace
WORKDIR /ros2_ws
COPY . /ros2_ws/src/mechanicsdsl_pendulum/

RUN /bin/bash -c "source /opt/ros/jazzy/setup.bash && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    colcon build --symlink-install"

RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
RUN echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

CMD ["/bin/bash"]
