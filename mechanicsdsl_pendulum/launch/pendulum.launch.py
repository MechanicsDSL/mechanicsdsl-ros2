"""
pendulum.launch.py
------------------
Launch file for the MechanicsDSL simple pendulum node.

Usage:
    ros2 launch mechanicsdsl_pendulum pendulum.launch.py
    ros2 launch mechanicsdsl_pendulum pendulum.launch.py l_m:=0.5 theta0_rad:=0.5
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration, TextSubstitution
from launch_ros.actions import Node


def generate_launch_description():
    # Declare launch arguments matching ROS2 parameter server keys
    args = [
        DeclareLaunchArgument('m_kg',       default_value='1.0',   description='Pendulum mass [kg]'),
        DeclareLaunchArgument('l_m',        default_value='0.25',  description='Rod length [m]'),
        DeclareLaunchArgument('g_mps2',     default_value='9.81',  description='Gravitational acceleration [m/s^2]'),
        DeclareLaunchArgument('theta0_rad', default_value='0.30',  description='Initial angle [rad]'),
        DeclareLaunchArgument('dt_s',       default_value='0.004', description='Integration timestep [s]'),
        DeclareLaunchArgument('drift_tol',  default_value='1e-4',  description='Energy drift warning threshold'),
    ]

    pendulum_node = Node(
        package='mechanicsdsl_pendulum',
        executable='pendulum_node',
        name='pendulum',
        output='screen',
        parameters=[{
            'm_kg':       LaunchConfiguration('m_kg'),
            'l_m':        LaunchConfiguration('l_m'),
            'g_mps2':     LaunchConfiguration('g_mps2'),
            'theta0_rad': LaunchConfiguration('theta0_rad'),
            'dt_s':       LaunchConfiguration('dt_s'),
            'drift_tol':  LaunchConfiguration('drift_tol'),
        }],
        remappings=[
            ('/pendulum/state',  '/mechanicsdsl/pendulum/state'),
            ('/pendulum/energy', '/mechanicsdsl/pendulum/energy'),
        ],
    )

    return LaunchDescription([
        *args,
        LogInfo(msg=['Launching MechanicsDSL pendulum node. l=',
                     LaunchConfiguration('l_m'), ' m, θ₀=',
                     LaunchConfiguration('theta0_rad'), ' rad']),
        pendulum_node,
    ])
