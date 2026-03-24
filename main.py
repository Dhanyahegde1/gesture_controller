import cv2
import time
from hand_detector import HandDetector
from gesture_recognizer import GestureRecognizer
from action_handler import ActionHandler

def main():
    cap        = cv2.VideoCapture(0)
    detector   = HandDetector()         
    recognizer = GestureRecognizer()     
    handler    = ActionHandler()        

    # --- Display persistence ---
    display_label    = ""
    display_until    = 0          # timestamp until which to keep showing label
    DISPLAY_DURATION = 1.5        # seconds to keep label on screen after gesture

    print("Gesture Control Running — press Q to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Step 1 — detect hand, draw skeleton, get annotated frame
        frame     = detector.find_hands(frame)

        # Step 2 — extract the 21 landmark coordinates
        landmarks, hand_label = detector.get_landmarks(frame)   

        # Step 3 — recognise gesture from landmarks
        gesture = recognizer.recognize(landmarks, hand_label) 
        
        # Step 4 — YOUR code: fire the system action
        handler.handle(gesture)

        # Update display label when a new gesture is detected
        if gesture is not None:
            label = gesture[0] if isinstance(gesture, tuple) else gesture
            display_label = f"{hand_label}: {label}"
            display_until = time.time() + DISPLAY_DURATION   # reset timer
           
        # Keep showing label until timer expires
        if time.time() < display_until:
            cv2.putText(frame, display_label, (10, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Gesture Control", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()