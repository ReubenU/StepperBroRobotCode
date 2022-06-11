from PS4_MotorControl import *
from math import *
import threading
import pickle
import serial
import time
import sys

# Timeout is the delay needed to pace the Python loop
# to the Arduino loop.
timeout = 80/1000 
arduino = serial.Serial(port='/dev/ttyUSB0', baudrate=115200, timeout=timeout)

# Timing variables...
deltaTime = 1

# Idling timer
idle_clock = 0.0
max_idle_time = 1.0
is_idling = False

# Robot Settings Panel
speed_percent = 25 # Please enter speed percentage(0 - 100%)
vertical_raise = True
vertical_value = 1000 # 2000 tilt up, 1000 lowered.
vertical_raise_rate = 500

# Values for displaying...
leftMotorPercent = 0
rightMotorPercent = 0


# Interpolation/Smoothing variables.
leftMotorLerp = 1500
rightMotorLerp = 1500

lerpSpeed = 4


# Compile the PS4 stick controls to drive and stepper
# data format...
def MotorSpeeds()->str:
    global speed_percent
    global leftMotorPercent
    global rightMotorPercent
    global deltaTime
    global vertical_value
    global vertical_raise_rate
    global leftMotorLerp
    global rightMotorLerp
    global lerpSpeed
    
    cont = controller

    y_sign = copysign(1, cont.L3.y)

    inverter = 1 * (y_sign > 0) + (y_sign < 0) * -1

    # Drivetrain calculations to apply joystick direction
    # to each wheel.
    leftMotor = -clamp(inverter*cont.L3.x + cont.L3.y, -1, 1)
    rightMotor = -clamp(inverter*-cont.L3.x + cont.L3.y, -1, 1)

    leftMotorPercent = leftMotor
    rightMotorPercent = rightMotor

    # Speed calculations...
    speed_range = 2000-1000
    adjusted_speed = (speed_range - (speed_range*(speed_percent/100)) )/2

    # Motor speed control
    leftMotor = int( round( mapInputToRange(leftMotor, -1, 1, 2000-adjusted_speed, 1000+adjusted_speed) ) )
    rightMotor = int( round( mapInputToRange(rightMotor, -1, 1, 1000+adjusted_speed, 2000-adjusted_speed) ) )

    # Interpolation for smoothing input so that Stepper Bro isn't spastic
    leftMotorLerp = int(round(lerp(leftMotorLerp, leftMotor, deltaTime * lerpSpeed)))
    rightMotorLerp = int(round(lerp(rightMotorLerp, rightMotor, deltaTime * lerpSpeed)))

    # Gripper control
    gripper = int(round(cont.Gripper))

    # Data to send to arduino...
    data = "<{:d},{:d},{:d},{:d},{:d},{:d}>".format(cont.R3.x, cont.R3.y, leftMotorLerp, rightMotorLerp, gripper, vertical_value)

    return data


# Automation Section
rolling_time = 3.4
rolling_elapsed = 0
rolling_speed_percent = 20

roll_left = 1500
roll_right = 1500

roll_lerp = 4

def RollOut():
    global deltaTime
    global roll_lerp
    global roll_left
    global roll_right
    global rolling_time
    global rolling_elapsed
    global rolling_speed_percent

    global vertical_value
    global vertical_raise

    # Speed calculations...
    if (rolling_elapsed < rolling_time and controller.rollOut):
        controller.L3.y = 1
        controller.isActive = True

        rolling_elapsed += deltaTime
    
        if (rolling_elapsed > rolling_time - .2):
            vertical_value = 2000
            vertical_raise = True

            controller.isActive = True
    
    if (rolling_elapsed >= rolling_time and controller.rollOut):
        controller.L3.y = 0
    
    if (controller.rollOut == False):
        rolling_elapsed = 0
    


# Pause Controlling Section
time_elapsed = 0.0
y_jog_time = 10.0
x_jog_time = 3.0
isPausing = False

def PauseControl():
    global vertical_value
    global vertical_raise
    global time_elapsed
    global y_jog_time
    global x_jog_time
    global isPausing


    if (time_elapsed < y_jog_time and controller.Quit):
        write2Arduino('<0,-1,1500,1500,90,{:d}>'.format(vertical_value))
        isPausing = True
        controller.isActive = True
        time_elapsed += deltaTime
    elif (time_elapsed > y_jog_time-6.5 and controller.Quit):
        controller.isActive = True
        vertical_value = 1000
        vertical_raise = False
        write2Arduino('<0,0,1500,1500,90,{:d}>'.format(vertical_value))
    elif (time_elapsed >= y_jog_time):

        if (controller.Quit == False):
            time_elapsed = 0.0
            isPausing = False
            vertical_value = 2000
            vertical_raise = True
            write2Arduino('<0,0,1500,1500,90,{:d}>'.format(vertical_value))
    
    if (controller.Exit and time_elapsed >= y_jog_time-1):
        controller.stop = True


# Send data to Arduino via Serial
def write2Arduino(data):

    if (arduino.in_waiting > 0):
        arduino.readline() # make the Serial clear the buffer...
        arduino.write(pickle.dumps(data)) # ...then write afterwards
    else:
         arduino.write(pickle.dumps(data)) # Write if there is no more data...

# Function to call when you want to spam the robot neutral values.
# Only use this in emergency situations.
def spamNeutralData():
    for _ in range(8):
        write2Arduino('<0,0,1500,1500,90,1000>')


# Get the PS4 inputs and run controller's listen function.
def getInputs():
    controller.listen(timeout=2, on_connect=None, on_disconnect=disconnect)#, on_sequence=quit_sequence())


# Disconnect function that spams a neutral data packet
# after controller.listen quits.
def disconnect():
    spamNeutralData()


# Idling function determines whether or not
# the controller hasn't been used after a certain
# amount of time.
def isIdle(deltaTime) -> bool:
    global idle_clock
    global max_idle_time

    if (controller.isActive == False and idle_clock < max_idle_time):
        idle_clock += deltaTime
    
    if (controller.isActive):
        idle_clock = 0.0
    
    if (idle_clock >= max_idle_time):
        return True
    
    return False


# DISPLAY FOR STEPPER BRO
x1 = '              ||    \n'
x2 = '          ====||====\n'
x3 = '          || [__] ||\n'
x4 = '  STEPPER BRO\'S DISPLAY PANEL\n\n'
print(x1+x2+x3+x4)
def DisplayScreen():
    global leftMotorPercent
    global rightMotorPercent
    global vertical_raise
    global deltaTime
    global isPausing
    global vertical_value

    global rolling_elapsed


    status = 'Idle' if (is_idling) else 'Active'
    status = 'Paused' if (isPausing) else 'Active'

    vert_mode = 'Erect' if (vertical_raise) else 'Flaccid'

    print(
        'Motors: {:.2%} | {:.2%} Gripper: {:d} Status: {} Vertical Mode: {} Vertical Value = {:d} Ticks Per Sec: {:.2f}'.format(
        -leftMotorPercent,
        -rightMotorPercent,
        int(round(controller.Gripper)),
        status,
        vert_mode,
        vertical_value,
        rolling_elapsed,
        round(1/deltaTime, 2)
        ),
        end='\r'
    )

    sys.stdout.flush()


# Testing main function to see data packet 
# (you have to write the Serial data writer function first...)
def main():
    global vertical_value
    global deltaTime
    global isPausing
    global idle_clock
    global timeout
    global is_idling

    while True:
        startTime = time.perf_counter() # Start performance timer

        # Function to pause robot and controller.
        PauseControl()

        # Rollout function.
        RollOut()

        # Only send data when controller is not paused/quitted
        # and we are actively using the controller.
        if (controller.Quit == False and is_idling == False):

            write2Arduino(MotorSpeeds())
        
        if (controller.stop):
            break

        time.sleep(timeout)

        deltaTime = time.perf_counter() - startTime # Get delta time from performance timer.
        is_idling = isIdle(deltaTime)

        DisplayScreen()
    
    # Give the terminal back a newline gracefully after DisplayPanel is finished.
    print('')



# Multithreading because controller.listen will override main.
# Main is the data sending thread, while getInputs is the
# input listening thread.
input_thread = threading.Thread(target=getInputs)
data_thread = threading.Thread(target=main)

input_thread.start()
data_thread.start()

input_thread.join()
data_thread.join()
