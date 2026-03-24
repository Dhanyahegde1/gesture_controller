import math

class GestureRecognizer:
    def __init__(self):
        self.tip_ids  = [4, 8, 12, 16, 20]
        self.base_ids = [2, 5,  9, 13, 17]

        # Swipe tracking — accumulation approach
        self.swipe_start_x   = None   # where the swipe began
        self.swipe_threshold = 60     # total pixels across full swipe

    def _distance(self, p1, p2):
        return math.hypot(p1[1] - p2[1], p1[2] - p2[2])

    def _fingers_up(self, landmarks, hand_label="Right"):  
        fingers = []

        if hand_label == "Right":
            fingers.append(landmarks[4][1] < landmarks[2][1])
        else:
            fingers.append(landmarks[4][1] > landmarks[2][1])

        for tip, base in zip(self.tip_ids[1:], self.base_ids[1:]):
            fingers.append(landmarks[tip][2] < landmarks[base][2])

        return fingers

    def recognize(self, landmarks, hand_label="Right"):
        if len(landmarks) < 21:
            self.prev_x = None
            return None

        fingers = self._fingers_up(landmarks, hand_label)

        if fingers == [False, False, False, False, False]:
            return "MUTE"

        if fingers == [False, True, True, False, False]:
            return "PLAY_PAUSE"

        if fingers == [True, True, False, False, False]:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance  = self._distance(thumb_tip, index_tip)
            return ("VOLUME_CONTROL", distance)
        
        if fingers[1] and fingers[2] and fingers[3] and fingers[4]:
            wrist_x = landmarks[0][1]

            # Record where swipe started
            if self.swipe_start_x is None:
                self.swipe_start_x = wrist_x
                return None

            # Measure total distance from swipe start
            total_delta = wrist_x - self.swipe_start_x
            #print(f"wrist_x: {wrist_x} | start: {self.swipe_start_x} | total: {total_delta}")

            if total_delta > self.swipe_threshold:
                self.swipe_start_x = None   # reset after firing
                return "NEXT_TRACK"

            elif total_delta < -self.swipe_threshold:
                self.swipe_start_x = None   # reset after firing
                return "PREV_TRACK"

            return None

         # When open palm is NOT detected, reset swipe start
        self.swipe_start_x = None
        return None

    


# ── isolated test ──────────────────────────────────────────────
if __name__ == "__main__":
    import cv2
    from hand_detector import HandDetector

    cap        = cv2.VideoCapture(0)
    detector   = HandDetector()
    recognizer = GestureRecognizer()

    print("Testing GestureRecognizer — press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame               = detector.find_hands(frame)
        landmarks, hand_label = detector.get_landmarks(frame)   
        gesture             = recognizer.recognize(landmarks, hand_label)

        if gesture:
            label = gesture[0] if isinstance(gesture, tuple) else gesture
            display = f"{hand_label}: {label}"                  
            cv2.putText(frame, display, (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            print(f"Gesture: {gesture}        ", end="\r")

        cv2.imshow("Gesture Recognizer Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()