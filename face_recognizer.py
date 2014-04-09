import cv2
import numpy as np
import os

class FaceRecognizer:

  def __init__(self):
    self.model = cv2.createLBPHFaceRecognizer()

  def train(self, base_path, images=[], labels=[]):
    self.images = images
    self.labels = labels  # this will be Dog DB IDs
    X = []

    for img_name in images:
      # Read in image from path as grayscale
      img = cv2.imread(os.path.join(base_path, img_name), cv2.IMREAD_GRAYSCALE)
      # Resize images
      # We need all images the same size for recognition
      img = cv2.resize(img, (64,64))
      X.append(np.asarray(img, dtype=np.uint8))

    # We need our labels to be 32-bit integers
    self.labels = np.asarray(self.labels, dtype=np.int32)

    # Train the model
    self.model.train(np.asarray(X), np.asarray(self.labels))


  def recognize(self, base_path, img_name):
    # Read in the image to be recognized
    img = cv2.imread(os.path.join(base_path, img_name), cv2.IMREAD_GRAYSCALE)

    # The prediction returns the label and confidence
    [id, confidence] = self.model.predict(np.asarray(img, dtype=np.uint8))

    # For debugging and accuracy checking purposes
    print "Dog ID:", id, "with confidence:", confidence,"%"

    return id
