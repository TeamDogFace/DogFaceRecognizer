import cv2
import cv2.cv as cv
import numpy as np
import os

class FaceDetector:

  def __init__(self, cascade_path):
    self.cascade = cv2.CascadeClassifier(cascade_path)
    if self.cascade.empty():
      raise Exception("Cascade not loaded! Please check the path.")

  def detect(self, image_path):
    filename = os.path.basename(os.path.splitext(image_path)[0])
    extension = os.path.splitext(image_path)[1]
    # Decide whether these need to be attributes
    self.image = cv2.imread(image_path)
    gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    # Detect using our cascade
    rect = self.cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(15,15), flags=cv.CV_HAAR_SCALE_IMAGE)

    # We can't do recognition on multiple faces
    # Ok well we could but I'm lazy right now, 1 face is easier
    if len(rect) > 1:
      raise Exception("Detected multiple faces. Proper recognition cannot be conducted.")

    if len(rect) == 0:
      raise Exception("Could not detect any faces. Try using another image.")

    rect[:,2:] += rect[:,:2]

    vis = self.image.copy()

    # For debugging purposes
    for x1, y1, x2, y2 in rect:
      cv2.imwrite(filename + '-detected' + extension, vis[y1:y2,x1:x2])

    return vis[y1:y2,x1:x2]
