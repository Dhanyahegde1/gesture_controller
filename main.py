import cv2
import time
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from action_handler import ActionHandler

def main():
    # Start webcam capture
    cap = cv2.VideoCapture(0)

    """Initialize modules"""
     # detects hand & landmarks
    detector   = HandDetector()
     # identifies gesture         
    recognizer = GestureRecognizer()   
     # performs system action 
    handler    = ActionHandler()        

    # Variables for displaying gesture label
    display_label = ""       # text to show on screen
    display_until = 0        # time until label is visible
    DISPLAY_DURATION = 1.5   # seconds to show label

    print("Gesture Control Running — press Q to quit")

    while True:
        # Read frame from webcam
        ret, frame = cap.read()
        if not ret:
            break

        # Step 1 — detect hand and draw landmarks
        frame = detector.find_hands(frame)

        # Step 2 — get 21 hand landmark points
        landmarks, hand_label = detector.get_landmarks(frame)

        # Step 3 — recognize gesture using landmarks
        gesture = recognizer.recognize(landmarks, hand_label)

        # Step 4 — perform action based on gesture
        handler.handle(gesture)

        # If gesture detected, update display label
        if gesture is not None:
            label = gesture[0] if isinstance(gesture, tuple) else gesture
            display_label = f"{hand_label}: {label}"
            display_until = time.time() + DISPLAY_DURATION  # reset timer

        # Show label until time expires
        if time.time() < display_until:
            cv2.putText(frame, display_label, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Display output window
        cv2.imshow("Gesture Control", frame)

        # Exit when 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release camera and close window
    cap.release()
    cv2.destroyAllWindows()

# Run main function
if __name__ == "__main__":
    main()