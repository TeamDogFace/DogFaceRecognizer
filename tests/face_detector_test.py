import sys
sys.path.append('../')

import face_detector as fd

if __name__ == "__main__":
  model = fd.FaceDetector("../cascades/cascade28-2-28-14.xml")
  model.detect('../test_images/dog4-1.jpg')
