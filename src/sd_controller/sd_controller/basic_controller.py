import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from xbox360controller import Xbox360Controller


class JoystickCMDPublisher(Node):

    def __init__(self, controller):
        super().__init__('minimal_publisher')

        self.controller = controller
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)
        timer_period = 0.5  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.max_dX = 5  # linear velocity along the x axis
        self.max_thetaZ = 1  # angular velocity along the z axis

        self.forward = 1
        self.backward = -1

    def convert_controller_data(self):
        joyL_x = self.controller.axis_l.x
        joyL_y = self.controller.axis_l.y
        trigR = self.controller.trigger_r.value

        if abs(joyL_x) < 0.1:
            joyL_x = 0

        if abs(joyL_y) < 0.1:
            # default to forward for very small values of joystick in the Y direction
            dX_direction = self.forward
            joyL_x = joyL_x * (-1)
        elif joyL_y < 0:
            dX_direction = self.forward
            joyL_x = joyL_x * (-1)
        else:
            dX_direction = self.backward

        dX = dX_direction * trigR * self.max_dX
        thetaZ = joyL_x * self.max_thetaZ

        return (dX, thetaZ)

    def timer_callback(self):
        cmd_vel = Twist()

        (dX, thetaZ) = self.convert_controller_data()

        cmd_vel.linear.x = float(dX)
        cmd_vel.linear.y = 0.0
        cmd_vel.linear.z = 0.0
        cmd_vel.angular.x = 0.0
        cmd_vel.angular.y = 0.0
        cmd_vel.angular.z = float(thetaZ)

        self.publisher_.publish(cmd_vel)


def main(args=None):

    try:
        with Xbox360Controller(0, axis_threshold=0.1) as controller:

            rclpy.init(args=args)

            joystick_command_publisher = JoystickCMDPublisher(controller)

            rclpy.spin(joystick_command_publisher)

            # Destroy the node explicitly
            # (optional - otherwise it will be done automatically
            # when the garbage collector destroys the node object)
            joystick_command_publisher.destroy_node()
            rclpy.shutdown()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
