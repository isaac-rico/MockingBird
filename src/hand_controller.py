# ==============================================================================
# imports

# ======================================
# standard imports
import socket, time, enum

# ======================================
# third-party imports
from adafruit_servokit import ServoKit



# ==============================================================================
# classes

# ======================================
# finger enum class
class Finger(enum.Enum):
    THUMB = 0
    INDEX = 1
    MIDDLE = 2
    RING = 3
    PINKY = 4


# ======================================
# host communication class
class HostComm:
    def __init__(self):
        self.host = "0.0.0.0"
        self.port = 8080
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    def __del__(self):
        self.close()


    def open(self):
        self.server.bind((self.host, self.port))
        

    def close(self):
        self.conn.close()
        self.server.close()
    

    def wait_for_connections(self):
        self.server.listen(1)
        self.conn, self.addr = self.server.accept()
    

    def send_message(self, message):
        self.conn.sendall(message.encode("utf-8"))


    def receive_data(self):
        data = self.conn.recv(1024)
        return data.decode()
    


# ======================================
# servo control class
class ServoControl:
    """Class to control servos.
    All servos are assumed to be connected to the Adafruit 16-Channel Servo Driver,
    in the order thumb to pinky (0-4)."""
    def __init__(self):
        self.kit = ServoKit(channels = 16)
        self.servo_seq_delay = 0.05

        self.min_servo_angle = 0
        self.max_servo_angle = 270


    def set_servo_angle(self, number, angle):
        """Set angle of a single servo.
        """
        if angle < self.min_servo_angle:
            raise ServoControlException("Angle (%d degrees) too low, must be at least %d degrees" % (angle, self.min_servo_angle))
        elif angle > self.max_servo_angle:
            raise ServoControlException("Angle (%d degrees) too high, must be at most %d degrees" % (angle, self.max_servo_angle))
        else:
            self.kit.servo[number].angle = angle

    
    def set_servo_angles(self, servos, angles):
        """Assumes hand has 5 servos, thumb to pinky.
        """
        for i in range(len(servos)):
            self.set_servo_angle(servos[i], angles[i])



# ======================================
# hand controller class
class HandController:
    def __init__(self):
        self.servo_control = ServoControl()
        self.hand_tickrate = 10
        self.hand_position_timestamp = 0
        self.hand_position = [0, 0, 0, 0, 0]
        self.finger_mask = [1, 1, 1, 1, 1]

        self.min_finger_angles = [0, 0, 0, 0, 0]
        self.max_finger_angles = [90, 130
        , 140, 130, 140]

        self.finger_angle_multiplier = [1.0, 1.3, 1.0, 1.2, 1.1]

        self.finger_seq_delay = 0.05
    

    def enable_finger(self, finger):
        self.finger_mask[finger] = 1


    def disable_finger(self, finger):
        self.finger_mask[finger] = 0
    
    
    def set_finger_angle(self, finger, angle):
        """Set angle of a single finger.
        """
        angle *= self.finger_angle_multiplier[finger]

        if angle < self.min_finger_angles[finger]:
            angle = self.min_finger_angles[finger]
        elif angle > self.max_finger_angles[finger]:
            angle = self.max_finger_angles[finger]
        
        self.servo_control.set_servo_angle(finger, angle)



    def set_hand(self, angles):
        """Set hand to a specific position.
        Does not update the hand position if the function is called faster than `self.hand_tickrate`.
        
        Args:
            angles (list): List of 5 integers, each representing the angle of a servo in degrees.
        """
        if time.time() - self.hand_position_timestamp < (1.0 / self.hand_tickrate):
            return
        
        self.hand_position_timestamp = time.time()
        for i in range(len(self.finger_mask)):
            if (self.finger_mask[i]):
                self.set_finger_angle(i, angles[i])
                time.sleep(self.finger_seq_delay)


    def open_hand(self):
        self.set_hand([0, 0, 0, 0, 0])
    

    def close_hand(self):
        self.set_hand(self.max_finger_angles)
    

    def middle_finger(self):
        angles = [self.min_finger_angles[0], self.max_finger_angles[1], self.min_finger_angles[2], self.max_finger_angles[3], self.max_finger_angles[4]]
        self.set_hand(angles)


    def rock_out(self):
        angles = [self.max_finger_angles[0], self.min_finger_angles[1], self.max_finger_angles[2], self.max_finger_angles[3], self.min_finger_angles[4]]
        self.set_hand(angles)


    def shaka(self):
        angles = [self.min_finger_angles[0], self.max_finger_angles[1], self.max_finger_angles[2], self.max_finger_angles[3], self.min_finger_angles[4]]
        self.set_hand(angles)
    

    def peace(self):
        angles = [self.max_finger_angles[0], self.min_finger_angles[1], self.min_finger_angles[2], self.max_finger_angles[3], self.max_finger_angles[4]]
        self.set_hand(angles)


    def thumbs_up(self):
        angles = [self.min_finger_angles[0], self.max_finger_angles[1], self.max_finger_angles[2], self.max_finger_angles[3], self.max_finger_angles[4]]
        self.set_hand(angles)


    
# ==============================================================================
# execeptions
class ServoControlException(Exception):
    pass



# ==============================================================================
# main function
def main():
    host_comm = HostComm()
    host_comm.open()

    print("Waiting for connection at %s on port %d" % (host_comm.host, host_comm.port))
    host_comm.wait_for_connections()
    print("Connected!")

    hand_controller = HandController()
    hand_controller.open_hand()

    hand_controller.finger_seq_delay = 0.00
    hand_controller.hand_tickrate = 30

    # temporary
    # hand_controller.disable_finger(Finger.THUMB.value)
    # hand_controller.disable_finger(Finger.INDEX.value)
    # hand_controller.disable_finger(Finger.MIDDLE.value)
    # hand_controller.disable_finger(Finger.RING.value)
    # hand_controller.disable_finger(Finger.PINKY.value)

    while True:
        data = host_comm.receive_data()
        host_comm.send_message("received")
        print(data)
        if data == "close":
            break
        angles = [float(x) for x in data.split(", ")]
        print(angles)
        hand_controller.set_hand(angles)
    
    hand_controller.open_hand()



def finger_test():
    hand_controller = HandController()
    hand_controller.open_hand()
    
    time.sleep(2)
    hand_controller.close_hand()
    time.sleep(2)
    hand_controller.shaka()
    time.sleep(2)
    hand_controller.rock_out()
    time.sleep(2)
    hand_controller.peace()
    time.sleep(2)
    hand_controller.thumbs_up()
    time.sleep(2)
    hand_controller.open_hand()
    return

    hand_controller.finger_seq_delay = 0.00

    # hand_controller.disable_finger(Finger.THUMB.value)
    # hand_controller.disable_finger(Finger.INDEX.value)
    # hand_controller.disable_finger(Finger.MIDDLE.value)
    # hand_controller.disable_finger(Finger.RING.value)
    # hand_controller.disable_finger(Finger.PINKY.value)

    angles = [0, 15, 30, 45, 60, 75, 90, 105, 120]
    # angles = [0, 15, 30, 45, 60, 75, 90]

    for i in range(len(angles)):
        print("Setting all finger angles to %d" % (angles[i]))
        hand_controller.set_hand([angles[i]] * 5)
        time.sleep(0.1)
    
    hand_controller.open_hand()





if __name__ == "__main__":
    finger_test()
    # main()