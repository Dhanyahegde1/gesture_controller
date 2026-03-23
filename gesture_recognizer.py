import math

class GestureRecognizer:
    def __init__(self):
        # Fingertip and knuckle IDs (from MediaPipe landmark map)
        self.tip_ids   = [4, 8, 12, 16, 20]   # fingertips
        self.base_ids  = [2, 5,  9, 13, 17]   # knuckle bases

        # Swipe tracking
        self.prev_x        = None
        self.swipe_threshold = 40   # pixels moved to count as a swipe

    # ── helpers ───────────────────────────────────────────────

    def _distance(self, p1, p2):
        """Euclidean distance between two (id, x, y) landmarks."""
        return math.hypot(p1[1] - p2[1], p1[2] - p2[2])

    def _fingers_up(self, landmarks):
        """
        Returns a list of 5 booleans [thumb, index, middle, ring, pinky].
        True = finger is extended/up.
        """
        fingers = []

        # Thumb: compare x-axis (horizontal) instead of y-axis
        # Tip (4) should be to the LEFT of base (2) for right hand
        if landmarks[4][1] < landmarks[2][1]:
            fingers.append(True)
        else:
            fingers.append(False)

        # Four fingers: tip y should be ABOVE (smaller y) than knuckle y
        for tip, base in zip(self.tip_ids[1:], self.base_ids[1:]):
            if landmarks[tip][2] < landmarks[base][2]:
                fingers.append(True)
            else:
                fingers.append(False)

        return fingers  # e.g. [False, True, True, False, False]

    # ── gesture recognition ───────────────────────────────────

    def recognize(self, landmarks):
        """
        Main method — call this every frame with the 21 landmarks.
        Returns a gesture string or None.
        """
        if len(landmarks) < 21:
            self.prev_x = None
            return None

        fingers = self._fingers_up(landmarks)

        # ── 1. FIST → Mute ───────────────────────────────────
        # All fingers closed
        if fingers == [False, False, False, False, False]:
            return "MUTE"

        # ── 2. TWO FINGERS UP → Play / Pause ─────────────────
        # Index + middle up, others down
        if fingers == [False, True, True, False, False]:
            return "PLAY_PAUSE"

        # ── 3. THUMB–INDEX DISTANCE → Volume Control ─────────
        # Only thumb and index extended (pinch gesture)
        if fingers == [True, True, False, False, False]:
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            distance  = self._distance(thumb_tip, index_tip)
            # Return distance so action_handler can map it to volume level
            return ("VOLUME_CONTROL", distance)

        # ── 4. SWIPE RIGHT → Next Track ──────────────────────
        # ── 5. SWIPE LEFT  → Previous Track ──────────────────
        # All fingers up = open palm → track swipe movement
        if fingers == [True, True, True, True, True]:
            wrist_x = landmarks[0][1]   # x coordinate of wrist

            if self.prev_x is not None:
                delta = wrist_x - self.prev_x

                if delta > self.swipe_threshold:
                    self.prev_x = wrist_x
                    return "NEXT_TRACK"

                elif delta < -self.swipe_threshold:
                    self.prev_x = wrist_x
                    return "PREV_TRACK"

            self.prev_x = wrist_x
            return None

        # No recognised gesture
        self.prev_x = None
        return None


# ── isolated test ──────────────────────────────────────────────
if __name__ == "__main__":
    import cv2
    from hand_detector import HandDetector

    cap      = cv2.VideoCapture(0)
    detector = HandDetector()
    recognizer = GestureRecognizer()

    print("Testing GestureRecognizer — press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame     = detector.find_hands(frame)
        landmarks = detector.get_landmarks(frame)
        gesture   = recognizer.recognize(landmarks)

        if gesture:
            label = gesture[0] if isinstance(gesture, tuple) else gesture
            cv2.putText(frame, label, (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            print(f"Gesture: {gesture}        ", end="\r")

        cv2.imshow("Gesture Recognizer Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()