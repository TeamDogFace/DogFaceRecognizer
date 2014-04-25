import sys
sys.path.append('../')

import face_recognizer as fr
from os import listdir

model = fr.FaceRecognizer()
base_path = '.'
to_be_recognized = 'dog4-5-detected.jpg'

def train(images, labels):
  model.train(base_path, images, labels)

def recognize():
  return model.recognize(base_path, to_be_recognized)

if __name__ == "__main__":  
  # Lulz at these initials
  images = ['dog4-1-detected.jpg']
  labels = [0]
  c = 10

  for file in listdir('./dog_faces'):
    if file.startswith("n"):
      images.append('./dog_faces/' + file)
      labels.append(c)
      c += 1


  for x in range(0,13):
    train(images, labels)
    prediction = recognize()
    # print labels
    print 'Image', to_be_recognized, 'is most closely related to', prediction, "\n\n"
    index = labels.index(prediction)
    del images[index]
    del labels[index]

  print labels