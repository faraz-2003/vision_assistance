
import time
import cv2
from libs.logger import Logger
from PIL import Image
import numpy as np

class ImageCV2:
    
    def __init__(self) -> None:
        # Set up logging
        self.logger = Logger.get_logger('gemini_vision.log')
        
    def open_webcam(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use CAP_DSHOW as a different backend
        if not cap.isOpened():
            self.logger.warning("Cannot open webcam with CAP_DSHOW, trying default backend.")
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                self.logger.error("Cannot open webcam")
                return None
        return cap


    def capture_image(self, cap):
        ret, frame = cap.read()
        self.logger.info(f"Capturing image from webcam")
        
        if not ret:
            self.logger.error("Cannot capture image")
            return None

        self.logger.info(f"Converting image PIL.Image")
        # Convert the numpy.ndarray to a PIL.Image.Image
        image = Image.fromarray(frame)
        
        self.logger.info(f"Converting image success")
        return image
    
    def save_image(self, image, filename):
        self.logger.info(f"Saving image to: {filename}")
        
        # Convert the PIL.Image.Image back to a numpy.ndarray
        frame = np.array(image)
        
        # Save the image
        cv2.imwrite(filename, frame)
        
    
    def capture_image_from_webcam(self, image_name):
        self.logger.info("Capturing image from webcam")

        cap = self.open_webcam()

        if cap is None:
            self.logger.error("Cannot open webcam")
            return None

        # Capture frame
        ret, frame = cap.read()

        # Check if frame is None
        if frame is None or not ret:
            self.logger.error("Cannot capture image")
            # Release the webcam capture object in case of an error
            cap.release()
            return None

        # Convert the numpy.ndarray to a PIL.Image.Image
        image = Image.fromarray(frame)

        # Save the image
        self.save_image(image, image_name)
        self.logger.info(f"Saved image to: {image_name}")

        # Release the webcam capture object
        cap.release()

        return image


    def release_webcam(self):
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
            self.logger.info("Webcam released")

    def show_webcam_feed(self):
        # Open the webcam (0 is the default webcam)
        cap = cv2.VideoCapture(0)

        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()

            # Display the resulting frame
            cv2.imshow('Webcam Feed', frame)

            # Break the loop on 'q' key press
            if cv2.waitKey(1)& 0xFF == ord('q'):
                break

        # When everything is done, release the capture and destroy the window
        cap.release()
        cv2.destroyAllWindows()
        
    def stop_webcam_feed(self,interval):
        time.sleep(interval)

