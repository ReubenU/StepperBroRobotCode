import numpy
import math

# The drive function code for the tri-omnibot
def set_robot_speeds(x_speed:float, y_speed:float, rot_speed:float):
    input_matrix = numpy.matrix(
        [
            [math.cos(math.radians(240)), math.cos(math.radians(120)), math.cos(math.radians(0))],
            [math.sin(math.radians(240)), math.sin(math.radians(120)), math.sin(math.radians(0))],
            [1, 1, 1]
        ]
    )

    inp_inverse = numpy.linalg.inv(input_matrix)
    
    a, b, c, d, e, f, g, h, i = [inp_inverse.item(x) for x in range(3*3)]

    motor_1 = a * x_speed + b * y_speed + c * rot_speed
    motor_2 = d * x_speed + e * y_speed + f * rot_speed
    motor_3 = g * x_speed + h * y_speed + i * rot_speed

    return [motor_1, motor_2, motor_3]

print(set_robot_speeds(70, 0, 0))