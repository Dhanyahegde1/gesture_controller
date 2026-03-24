import math

class GestureRecognizer:
    def __init__(self):
        # Fingertip landmark indices
        self.tip_ids  = [4, 8, 12, 16, 20]
        
        # Base joint landmark indices
        self.base_ids = [2, 5,  9, 13, 17]

        # Swipe tracking variables
        self.swipe_start_x   = None  
        # minimum pixels to detect swipe 
        self.swipe_threshold = 60     

    def _distance(self, p1, p2):
        # Calculate Euclidean distance between two points
        return math.hypot(p1[1] - p2[1], p1[2] - p2[2])

    def _fingers_up(self, landmarks, hand_label="Right"):  
        fingers = []

        # Thumb logic (depends on left/right hand)
        if hand_label == "Right":
            fingers.append(landmarks[4][1] < landmarks[2][1])
        else:
            fingers.append(landmarks[4][1] > landmarks[2][1])

        # Other fingers (tip above base → finger is up)
        for tip, base in zip(self.tip_ids[1:], self.base_ids[1:]):
            fingers.append(landmarks[tip][2] < landmarks[base][2])

        return fingers 

    def recognize(self, landmarks, hand_label="Right"):
        # If no proper hand detected
        if len(landmarks) < 21:
            self.prev_x = None
            return None

        # Get finger states (True = up, False = down)
        fingers = self._fingers_up(landmarks, hand_label)

        # All fingers down → Mute
        if fingers == [False, False, False, False, False]:
            return "MUTE"

        # Index + middle up → Play/Pause
        if fingers == [False, True, True, False, False]:
            return "PLAY_PAUSE"

        # Thumb + index up → Volume control
        if fingers == [True, True, False, False, False]:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance  = self._distance(thumb_tip, index_tip)  
            return ("VOLUME_CONTROL", distance)
        
        # Open palm (4 fingers up) → Swipe detection
        if fingers[1] and fingers[2] and fingers[3] and fingers[4]:
            # wrist x-position
            wrist_x = landmarks[0][1]  

            # Store initial swipe position
            if self.swipe_start_x is None:
                self.swipe_start_x = wrist_x
                return None

            # Calculate total horizontal movement
            total_delta = wrist_x - self.swipe_start_x

            # Swipe right → Next track
            if total_delta > self.swipe_threshold:
                self.swipe_start_x = None  # reset after action
                return "NEXT_TRACK"

            # Swipe left → Previous track
            elif total_delta < -self.swipe_threshold:
                self.swipe_start_x = None  # reset after action
                return "PREV_TRACK"

            return None

        # Reset swipe tracking if palm is not open
        self.swipe_start_x = None
        return None


# isolated test 
if __name__ == "__main__":
    import cv2
    from hand_detector import HandDetector

    # Start webcam
    cap = cv2.VideoCapture(0)
    
    # Initialize modules
    detector   = HandDetector()
    recognizer = GestureRecognizer()

    print("Testing GestureRecognizer — press Q to quit")

    while True:
        # Capture frame
        ret, frame = cap.read()
        if not ret:
            break

        # Detect hand and landmarks
        frame = detector.find_hands(frame)
        landmarks, hand_label = detector.get_landmarks(frame)   

        # Recognize gesture
        gesture = recognizer.recognize(landmarks, hand_label)

        # Display detected gesture
        if gesture:
            label = gesture[0] if isinstance(gesture, tuple) else gesture
            display = f"{hand_label}: {label}"                  
            cv2.putText(frame, display, (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            print(f"Gesture: {gesture}        ", end="\r")

        # Show window
        cv2.imshow("Gesture Recognizer Test", frame)

        # Exit on 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Cleanup
    cap.release()
    cv2.destroyAllWindows()