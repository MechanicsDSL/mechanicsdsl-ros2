"""
double_pendulum.launch.py
-------------------------
Launch file for the MechanicsDSL double pendulum node.

Usage:
    ros2 launch mechanicsdsl_pendulum double_pendulum.launch.py
    ros2 launch mechanicsdsl_pendulum double_pendulum.launch.py theta1_0:=0.3 theta2_0:=0.2
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    args = [
        DeclareLaunchArgument('m_kg',     default_value='1.0',   description='Mass [kg]'),
        DeclareLaunchArgument('l_m',      default_value='1.0',   description='Rod length [m]'),
        DeclareLaunchArgument('g_mps2',   default_value='9.81',  description='Gravity [m/s^2]'),
        DeclareLaunchArgument('theta1_0', default_value='0.8',   description='Initial theta1 [rad]'),
        DeclareLaunchArgument('theta2_0', default_value='0.4',   description='Initial theta2 [rad]'),
        DeclareLaunchArgument('dt_s',     default_value='0.005', description='Timestep [s]'),
        DeclareLaunchArgument('drift_tol',default_value='1e-3',  description='Energy drift tolerance'),
    ]

    node = Node(
        package='mechanicsdsl_pendulum',
        executable='double_pendulum_node',
        name='double_pendulum',
        output='screen',
        parameters=[{
            'm_kg':     LaunchConfiguration('m_kg'),
            'l_m':      LaunchConfiguration('l_m'),
            'g_mps2':   LaunchConfiguration('g_mps2'),
            'theta1_0': LaunchConfiguration('theta1_0'),
            'theta2_0': LaunchConfiguration('theta2_0'),
            'dt_s':     LaunchConfiguration('dt_s'),
            'drift_tol':LaunchConfiguration('drift_tol'),
        }],
    )

    return LaunchDescription([
        *args,
        LogInfo(msg=['Launching MechanicsDSL double pendulum. '
                     'θ₁₀=', LaunchConfiguration('theta1_0'),
                     ' θ₂₀=', LaunchConfiguration('theta2_0')]),
        node,
    ])
