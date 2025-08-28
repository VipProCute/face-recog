import cv2
import threading
import time

class ThreadedCamera:
    def __init__(self, cam_index=0):
        self.cap = cv2.VideoCapture(cam_index)
        self.frame = None
        self.running = False
        self.thread = None

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.update, daemon=True)
            self.thread.start()

    def update(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame
            time.sleep(0.01)  # Slight delay for CPU relief

    def get_frame(self):
        return self.frame

    def stop(self):
        self.running = False
        if self.cap.isOpened():
            self.cap.release()