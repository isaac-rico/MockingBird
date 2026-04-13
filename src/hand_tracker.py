# ==============================================================================
# imports

# ======================================
# standard imports
import time, cv2, math, socket
import numpy as np

# ======================================
# third-party imports
import mediapipe as mp
from mediapipe.framework.formats import landmark_pb2



# ==============================================================================
# classes

# ======================================
# raspberry pi communication class
class RPiComm:
    def __init__(self):
        self.host = "raspberrypi.local"
        # self.host = "raspberrypi"
        self.port = 8080
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    

    def __del__(self):
        self.send_message("close")
        self.disconnect()


    def connect(self):
        self.client.connect((self.host, self.port))


    def disconnect(self):
        self.client.close()
    

    def send_message(self, message):
        self.client.sendall(message.encode("utf-8"))

    def send_data(self, data):
        message = ""
        for i in range(len(data)):
            if i != (len(data) - 1):
                message += "%.2f, " % (data[i])
            else:
                message += "%.2f" % (data[i])
        self.client.sendall(message.encode("utf-8"))
    

    def receive_data(self):
        response = self.client.recv(1024).decode()
        return response
    

    def transact(self, data):
        self.send_data(data)
        return self.receive_data()
    



# ======================================
# camera capture class
class CameraCapture:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
    
    
    def fetch_frame(self):
        ret, frame = self.camera.read()
        frame = cv2.flip(frame, 1)
        return frame
    

    def close():
        pass



# ======================================
# hand landmark detection class
class Landmarker:
    def __init__(self):
        self.result = mp.tasks.vision.HandLandmarkerResult
        self.landmarker = mp.tasks.vision.HandLandmarker
        self.create_landmarker()
   
    # callback function
    def update_result(self, result, output_image: mp.Image, timestamp_ms: int):
        self.result = result

    def create_landmarker(self):
        # HandLandmarkerOptions (details here: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker/python#live-stream)
        options = mp.tasks.vision.HandLandmarkerOptions( 
            base_options = mp.tasks.BaseOptions(model_asset_path = "hand_landmarker.task"), # path to model
            running_mode = mp.tasks.vision.RunningMode.LIVE_STREAM, # running on a live stream
            num_hands = 2, # track both hands
            min_hand_detection_confidence = 0.3, # lower than value to get predictions more often
            min_hand_presence_confidence = 0.3, # lower than value to get predictions more often
            min_tracking_confidence = 0.3, # lower than value to get predictions more often
            result_callback = self.update_result)
      
      
        # initialize landmarker
        self.landmarker = self.landmarker.create_from_options(options)
   

    def detect_async(self, frame):
        # convert np frame to mp image
        mp_image = mp.Image(image_format = mp.ImageFormat.SRGB, data = frame)
        # detect landmarks
        self.landmarker.detect_async(image = mp_image, timestamp_ms = int(time.time() * 1000))


    def close(self):
        # close landmarker
        self.landmarker.close()



# ======================================
# hand tracker class
class HandTracker:
    def __init__(self):
        self.capture_device = CameraCapture()
        self.hand_landmarker = Landmarker()
        self.tick_rate = 30

        self.hand_landmark_matrix = [
            [1, 2, 3, 4],
            [5, 6, 7, 8],
            [9, 10, 11, 12],
            [13, 14, 15, 16],
            [17, 18, 19, 20]
        ]
    

    def close(self):
        self.capture_device.close()
        self.hand_landmarker.close()


    def set_tick_rate(self, rate):
        self.tick_rate = rate
    

    def get_tick_rate(self):
        return self.tick_rate

    def draw_landmarks_on_image(self, rgb_image):
        """Courtesy of https://github.com/googlesamples/mediapipe/blob/main/examples/hand_landmarker/python/hand_landmarker.ipynb"""
        try:
            if self.hand_landmarker.result.hand_landmarks == []:
                return rgb_image
            else:
                hand_landmarks_list = self.hand_landmarker.result.hand_landmarks
                handedness_list = self.hand_landmarker.result.handedness
                annotated_image = np.copy(rgb_image)

                # Loop through the detected hands to visualize.
                for idx in range(len(hand_landmarks_list)):
                    hand_landmarks = hand_landmarks_list[idx]
                    
                    # Draw the hand landmarks.
                    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                    hand_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks])
                    mp.solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    hand_landmarks_proto,
                    mp.solutions.hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_styles.get_default_hand_landmarks_style(),
                    mp.solutions.drawing_styles.get_default_hand_connections_style())

                return annotated_image
        except:
            return rgb_image
        

    def calculate_finger_angle(self, hand_landmarks, finger):
        if finger < 0 or finger > 4:
            return -1
        
        loc1 = self.hand_landmark_matrix[finger][0]
        loc2 = self.hand_landmark_matrix[finger][1]
        loc3 = self.hand_landmark_matrix[finger][3]

        c = np.array([hand_landmarks[loc3].x, hand_landmarks[loc3].y, hand_landmarks[loc3].z])
        b = np.array([hand_landmarks[loc2].x, hand_landmarks[loc2].y, hand_landmarks[loc2].z])
        a = np.array([hand_landmarks[loc1].x, hand_landmarks[loc1].y, hand_landmarks[loc1].z])

        v1 = [b[0] - a[0], b[1] - a[1], b[2] - a[2]]
        v2 = [c[0] - b[0], c[1] - b[1], c[2] - b[2]]

        dot_product = sum(v1[i] * v2[i] for i in range(3))
        magnitude_v1 = math.sqrt(sum(v1[i] ** 2 for i in range(3)))
        magnitude_v2 = math.sqrt(sum(v2[i] ** 2 for i in range(3)))

        # Angle in radians
        angle_rad = math.acos(dot_product / (magnitude_v1 * magnitude_v2))

        # Convert to degrees
        angle_deg = math.degrees(angle_rad)

        return angle_deg
    

    def get_finger_angles(self):
        try:
            if self.hand_landmarker.result.hand_landmarks == []:
                return [-1, -1, -1, -1, -1]
            
            finger_angles = [0, 0, 0, 0, 0]
            hand_landmarks_list = self.hand_landmarker.result.hand_landmarks

            for i in range(len(hand_landmarks_list)):
                for finger in range(5):
                    angle = self.calculate_finger_angle(hand_landmarks_list[i], finger)
                    finger_angles[finger] = angle
            
            return finger_angles
        
        except:
            return [-1, -1, -1, -1, -1]
    
    

    def display_finger_angles(self, finger_angles):
        for finger in range(5):
            print(f"Finger {finger + 1}: {finger_angles[finger]} degrees")


    def tick(self):
        # get frame
        frame = self.capture_device.fetch_frame()
        
        # determine hand landmarks
        self.hand_landmarker.detect_async(frame)

        # draw landmarks on frame
        frame = self.draw_landmarks_on_image(frame)

        # display finger angles in console
        # self.display_finger_angles(self.get_finger_angles())

        # update cv2 window
        cv2.imshow("HandTracker v0.2", frame)
        cv2.waitKey(1)
    

    def run(self, rpi_comm = None):
        while True:
            self.tick()
            if rpi_comm:
                angles = self.get_finger_angles()
                if angles[0] != -1:
                    response = rpi_comm.transact(angles)
                    print(response)
            
            time.sleep((1.0 / self.tick_rate))



# ==============================================================================
# main function
def main():
    hand_tracker = HandTracker()
    rpi_comm = RPiComm()
    rpi_comm.connect()
    hand_tracker.run(rpi_comm)



if __name__ == "__main__":
    main()