import sys
sys.path.append('../')

import face_recognizer as fr
from os import listdir

if __name__ == "__main__":
  model = fr.FaceRecognizer()
  base_path = '.'
  # Lulz at these initials
  images = ['dog1-detected.jpg', 'dog4-2-detected.jpg', 'dog5-detected.jpg']
  labels = [1,4,5]
  c = 10

  #try:
      for file in listdir('./dog_face'):
          if file.startswith("n"):
              images.append('./dog_face', file)
              labels.append(c)
              c += 1
  #except:
   #   print "OpenCV Error"
    #  print file


#  try:
#    for file in listdir('./dog_faces'):
#      if(file.startswith("n")):
#        images.append('./dog_faces', file)
#        labels.append(c)
#        c += 1
#  except:
#    print "OpenCV Error"
#    print file

  print len(images)

  to_be_recognized = 'dog4-5-detected.jpg'

  model.train(base_path, images, labels)

  prediction = model.recognize(base_path, to_be_recognized)

  print 'Image', to_be_recognized, 'is most closely related to', prediction
