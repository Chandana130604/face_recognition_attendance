import cv2

def start_camera():

    video = cv2.VideoCapture(0)

    while True:

        ret, frame = video.read()

        if not ret:
            break

        cv2.imshow("Camera", frame)

        key = cv2.waitKey(1)

        if key == 27:   # ESC key
            break

    video.release()
    cv2.destroyAllWindows()