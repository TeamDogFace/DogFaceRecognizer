import sys
sys.path.append('../')

import face_recognizer as fr

if __name__ == "__main__":
  model = fr.FaceRecognizer()
  base_path = '.'
  images = ['dog1-detected.jpg', 'dog4-2-detected.jpg', 'dog5-detected.jpg']
  to_be_recognized = 'dog4-5-detected.jpg'

  model.train(base_path, images)

  prediction = model.recognize(base_path, to_be_recognized)

  print 'Image', to_be_recognized, 'is most closely related to', prediction
