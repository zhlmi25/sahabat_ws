from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([
                FindPackageShare('nav2_bringup'),
                '/launch/navigation_launch.py'
            ]),
            launch_arguments={
                'use_sim_time': 'False',
                'autostart': 'False',
                'map': '/path/to/your-map.yaml'
            }.items()
        )
    ])
