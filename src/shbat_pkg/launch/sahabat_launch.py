import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
import xacro
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():

    # Specify the name of the package and path to xacro file within the package
    pkg_name = 'shbat_pkg'
    file_subpath = 'urdf/sahabat_robot.urdf.xacro'

    # Use xacro to process the file
    xacro_file = os.path.join(get_package_share_directory(pkg_name), file_subpath)
    robot_description_raw = xacro.process_file(xacro_file).toxml()

    # Configure the robot_state_publisher node
    node_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw},
                    {'use_sim_time': True}],
    )

    # Configure the RViz node
    node_rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
    )

    node_joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_description_raw}]
    )

    node_oradar_scan = Node(
        package='oradar_radar',
        executable='oradar_scan_node',
        name='oradar_scan_node',
        output='screen',
        parameters=[
        {'device_model': 'MS200'},
        {'frame_id': 'base_link'},
        {'scan_topic': 'scan'},
        {'port_name': '/dev/ttyUSB0'},
        {'baudrate': 230400},
        {'angle_min': 0.0},
        {'angle_max': 360.0},
        {'range_min': 0.05},
        {'range_max': 20.0},
        {'clockwise': False},
        {'motor_speed': 10}
        ]  # Change as needed
    )

    node_imu = Node(
        package='wheeltec_n100_imu',
        executable='imu_node',
        name='imu_node',
        output='screen',
        parameters=[{'serial_port': '/dev/ttyUSB0'}]  # Change '/dev/ttyUSB0' to your actual serial port if needed
    )

    # Run the nodes
    return LaunchDescription([
        node_robot_state_publisher,
        node_joint_state_publisher,
        # node_rviz 
    ])