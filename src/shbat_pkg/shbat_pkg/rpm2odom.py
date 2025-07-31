import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import Int32MultiArray
import math


class RpmToOdom(Node):
    def __init__(self):
        super().__init__('rpm_to_odom')

        # Robot parameters
        self.wheel_radius = 0.05  # meters
        self.wheel_base = 0.3     # meters
        self.rpm_to_rps = 2 * math.pi / 60  # RPM to rad/s

        # Pose
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.last_time = self.get_clock().now()

        # ROS interfaces
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.rpm_sub = self.create_subscription(
            Int32MultiArray,  # [left_rpm, right_rpm]
            '/wheel_rpm',
            self.rpm_callback,
            10
        )

    def rpm_callback(self, msg):
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time

        left_rpm = msg.data[0]
        right_rpm = msg.data[1]

        left_rps = left_rpm * self.rpm_to_rps
        right_rps = right_rpm * self.rpm_to_rps

        v_left = left_rps * self.wheel_radius
        v_right = right_rps * self.wheel_radius

        linear_vel = (v_right + v_left) / 2.0
        angular_vel = (v_right - v_left) / self.wheel_base

        # Dead-reckoning integration
        delta_x = linear_vel * math.cos(self.theta) * dt
        delta_y = linear_vel * math.sin(self.theta) * dt
        delta_theta = angular_vel * dt

        self.x += delta_x
        self.y += delta_y
        self.theta += delta_theta

        # Create Odometry message
        odom = Odometry()
        odom.header.stamp = current_time.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        odom.pose.pose.orientation.w = math.cos(self.theta / 2.0)
        odom.twist.twist.linear.x = linear_vel
        odom.twist.twist.angular.z = angular_vel

        self.odom_pub.publish(odom)


def main(args=None):
    rclpy.init(args=args)
    node = RpmToOdom()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
