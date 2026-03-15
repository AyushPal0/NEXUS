import cv2

def take_photo():
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()

    if ret:
        cv2.imwrite("photo.png", frame)

    cam.release()