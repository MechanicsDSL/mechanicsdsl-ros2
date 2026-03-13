cmake_minimum_required(VERSION 3.16)
project(mechanicsdsl_pendulum VERSION 0.1.0)

# C++17 required
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic -O2)
endif()

# ---------------------------------------------------------------------------
# Dependencies
# ---------------------------------------------------------------------------
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# ---------------------------------------------------------------------------
# Custom message: PendulumState
# Fields: header, theta (rad), omega (rad/s), energy (J), energy_drift
# ---------------------------------------------------------------------------
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/PendulumState.msg"
  DEPENDENCIES std_msgs
)

# ---------------------------------------------------------------------------
# MechanicsDSL-generated pendulum dynamics node
# ---------------------------------------------------------------------------
add_executable(pendulum_node src/pendulum_node.cpp)

ament_target_dependencies(pendulum_node
  rclcpp
  std_msgs
  geometry_msgs
  sensor_msgs
)

rosidl_get_typesupport_target(cpp_typesupport_target
  ${PROJECT_NAME} rosidl_typesupport_cpp)
target_link_libraries(pendulum_node "${cpp_typesupport_target}" m)

install(TARGETS pendulum_node
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  find_package(ament_cmake_gtest REQUIRED)
  ament_lint_auto_find_test_dependencies()

  ament_add_gtest(test_pendulum_eom test/test_pendulum_eom.cpp)
  target_link_libraries(test_pendulum_eom m)
endif()

ament_package()
