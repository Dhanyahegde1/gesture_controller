import cv2
import mediapipe as mp

class HandDetector:
    def __init__(self, detection_confidence=0.7, tracking_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,       # video mode (faster tracking)
            max_num_hands=1,               # one hand only
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )

        # Fingertip landmark IDs (from the diagram)
        self.tip_ids = [4, 8, 12, 16, 20]

    def find_hands(self, frame):
        """
        Process a frame, draw landmarks, and return the frame.
        Always draws the hand skeleton when a hand is detected.
        """
        # MediaPipe requires RGB, OpenCV gives BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(rgb_frame)

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]  # first hand only

            # Draw the skeleton + landmark dots on the frame
            self.mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw_styles.get_default_hand_landmarks_style(),
                self.mp_draw_styles.get_default_hand_connections_style()
            )

        return frame

    def get_landmarks(self, frame):
        """
        Returns a list of 21 landmark positions as (id, x, y) tuples.
        x and y are pixel coordinates based on the frame size.
        Returns empty list if no hand is detected.
        """
        landmark_list = []
        hand_label = "Right"  # default

        if self.results.multi_hand_landmarks:
            hand_landmarks = self.results.multi_hand_landmarks[0]
            h, w, _ = frame.shape

            for idx, lm in enumerate(hand_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmark_list.append((idx, cx, cy))

            # detect left or right
            if self.results.multi_handedness:
                hand_label = self.results.multi_handedness[0].classification[0].label

        return landmark_list, hand_label  # ← now a tuple


# ── isolated test ──────────────────────────────────────────────
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    detector = HandDetector()

    print("Testing HandDetector — press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = detector.find_hands(frame)
        landmarks, hand_label = detector.get_landmarks(frame)

        if landmarks:
            # Print fingertip positions (IDs 4,8,12,16,20)
            tips = [lm for lm in landmarks if lm[0] in detector.tip_ids]
            print(f"Fingertips: {tips}", end="\r")

        cv2.imshow("Hand Detector Test", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()