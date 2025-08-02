import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import requests

CAN_EFF_FLAG = 0x80000000
RPM_FLAG = 0x300
LEFT_ID = 15
RIGHT_ID = 33

class BaseController(Node):
    def __init__(self):
        super().__init__('base_controller')
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10
        )
        self.wheel_base = 0.33  # meters
        self.wheel_radius = 0.1524  # meters

    def cmd_vel_callback(self, msg: Twist):
        v = msg.linear.x
        w = msg.angular.z

        # Differential drive kinematics
        v_left = v - (w * self.wheel_base / 2)
        v_right = v + (w * self.wheel_base / 2)

        # Convert to RPM
        rpm_left = int((v_left / (2 * 3.1416 * self.wheel_radius)) * 60)
        rpm_right = int((v_right / (2 * 3.1416 * self.wheel_radius)) * 60)

        self.get_logger().info(f'Setting left RPM: {rpm_left}, right RPM: {rpm_right}')

        # Send left RPM
        can_id_left = LEFT_ID | RPM_FLAG | CAN_EFF_FLAG
        data_left = list(rpm_left.to_bytes(4, byteorder='big', signed=True))
        payload_left = {"can_id": can_id_left, "data": data_left}
        requests.post("http://localhost:8000", json=payload_left)

        # Send right RPM
        can_id_right = RIGHT_ID | RPM_FLAG | CAN_EFF_FLAG
        data_right = list(rpm_right.to_bytes(4, byteorder='big', signed=True))
        payload_right = {"can_id": can_id_right, "data": data_right}
        requests.post("http://localhost:8000", json=payload_right)

def main(args=None):
    rclpy.init(args=args)
    node = BaseController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()