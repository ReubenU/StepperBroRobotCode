from pyPS4Controller.controller import Controller

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# PS4 controller object
class MyController(Controller):

    def __init__(self, **kwargs):
        Controller.__init__(self, **kwargs)

        self.L3 = Vector(0, 0)
        self.R3 = Vector(0, 0)

        self.L3_x_deadzone = 0.2
        self.L3_y_deadzone = 0.25
        self.R3_deadzone = 0.1
        self.gripper_deadzone = 0.3

        self.Gripper = 90.0
        self.Quit=False
        self.Exit = False

        self.isActive = False

        self.rollOut = False

    #### This entire block handles the left joystick L3
    
    # L3 Y axis
    def on_L3_up(self, value):
        self.L3.y = mapInputToRange(value, 0, -32767, 0.0, 1.0)
        self.L3.y = self.L3.y * (self.L3.y > self.L3_y_deadzone)
        self.isActive = True
    
    def on_L3_down(self, value):
        self.L3.y = mapInputToRange(value, 0, 32767, 0.0, -1.0)
        self.L3.y = self.L3.y * (self.L3.y < -self.L3_y_deadzone)
        self.isActive = True

    # L3 X axis
    def on_L3_right(self, value):
        self.L3.x = mapInputToRange(value, 0, 32767, 0.0, 1.0)
        self.L3.x = self.L3.x * (self.L3.x > self.L3_x_deadzone)
        self.isActive = True

    def on_L3_left(self, value):
        self.L3.x = mapInputToRange(value, 0, -32767, 0.0, -1.0)
        self.L3.x = self.L3.x * (self.L3.x < -self.L3_x_deadzone)
        self.isActive = True
    
    # Reset L3 axes to the neutral value of 1500
    def on_L3_x_at_rest(self):
        self.L3.x = 0
        self.isActive = False
    
    def on_L3_y_at_rest(self):
        self.L3.y = 0
        self.isActive = False


    #### This entire block handles the right joystick R3

    # R3 Y axis
    def on_R3_up(self, value):
        self.R3.y = 1
        self.R3.y = self.R3.y * (abs(value)/32767 > self.R3_deadzone)
        self.isActive = True
    
    def on_R3_down(self, value):
        self.R3.y = -1
        self.R3.y = self.R3.y * (abs(value)/32767 > self.R3_deadzone)
        self.isActive = True

    # R3 X axis
    def on_R3_right(self, value):
        self.R3.x = 1
        self.R3.x = self.R3.x * (abs(value)/32767 > self.R3_deadzone)
        self.isActive = True

    def on_R3_left(self, value):
        self.R3.x = -1
        self.R3.x = self.R3.x * (abs(value)/32767 > self.R3_deadzone)
        self.isActive = True
    
    # Reset R3 axes to the neutral value of 0
    def on_R3_x_at_rest(self):
        self.R3.x = 0
        self.isActive = False
    
    def on_R3_y_at_rest(self):
        self.R3.y = 0
        self.isActive = False

    # Trigger Handling for Gripper
    def on_L2_press(self, value):
        value = value * (abs(value)/32767 > self.gripper_deadzone)
        self.Gripper = mapInputToRange(value, 32767, -32767, 0, 90)
        self.isActive = True

    def on_L2_release(self):
        self.Gripper = 90
        self.isActive = False

    def on_R2_press(self, value):
        value = value * (abs(value)/32767 > self.gripper_deadzone)
        self.Gripper = mapInputToRange(value, -32767, 32767, 90, 180)
        self.isActive = True

    def on_R2_release(self):
        self.Gripper = 90
        self.isActive = False

    # Quit button
    def on_playstation_button_press(self):
        self.Quit = not self.Quit

    def on_playstation_button_release(self):
        pass
    

    # Vertical Control
    def on_up_arrow_press(self):
        self.rollOut = True
        self.isActive = True
    
    def on_up_down_arrow_release(self):
        self.isActive = False
    
    def on_down_arrow_press(self):
        self.rollOut = False
        self.isActive = True

    def on_x_press(self):
        self.Quit = True
        self.Exit = True

# Use this controller instance instead.
controller = MyController(interface="/dev/input/js0", connecting_using_ds4drv=False)

# Clamp value between a minimum and
# a maximum.
def clamp(value, minValue, maxValue)->float:
    return min(maxValue, max(minValue, value))

# Make an input value that ranges from "fromMin" to "fromMax"
# map directly to a new range that goes from "toMin" to "toMax".
def mapInputToRange(inputVal, fromMin, fromMax, toMin, toMax)->float:
    return (inputVal-fromMin)/(fromMax-fromMin)*(toMax-toMin)+toMin

# Linear Interpolation function where a is the start value,
# b is the goal, and t is the interpolation step.
def lerp(a, b, t):
    return a + (b-a)*t
