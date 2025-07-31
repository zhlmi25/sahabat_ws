from setuptools import find_packages, setup

package_name = 'shbat_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/urdf', [
            'urdf/lidar.urdf.xacro',
            'urdf/sahabat_robot.urdf.xacro',
            'urdf/sahabat_control.urdf.xacro',
        ]),

        # ('share/' + package_name + '/map', [
        #     'map/sahabat_map.yaml',
        #     'map/sahabat_map.pgm',
        # ]),
        
        ('share/' + package_name + '/launch', [
            'launch/sahabat_launch.py',
            'launch/sahabat_slam.launch.py',
        ]),
        ('share/' + package_name + '/config', [
            'config/mapper_params_online_async.yaml',
        ]),
 
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sahabat',
    maintainer_email='sahabat@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'rpm2odom = shbat_pkg.rpm2odom:main',
            'kalman_filter = shbat_pkg.kalman_filter:main',
        ],
    },
)