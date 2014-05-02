import face_detector as fd
import face_recognizer as fr
import mysql.connector
import sqlite3 # We won't need this for production
import cv2 # For debugging
import sys
import os

def load_config():
  config = {}
  # We need this for the base path of search request images
  # We could change this since we know where the script will
  #  be located in respect in respect to the web app
  execfile("paths.conf", config)
  return config

def load_cascades():
  cascade20 = fd.FaceDetector('./cascades/cascade20-2-26-14.xml')
  cascade28 = fd.FaceDetector('./cascades/cascade28-2-28-14.xml')
  cascade10 = fd.FaceDetector('./cascades/cascade10-3-16.xml')
  return [cascade20, cascade28, cascade10]

def detectFace(path, cascades):
  for cascade in cascades:
    img = cascade.detect(path)
    if img is not None:
      return img
  return None

def find_dog(dog_id, dogs):
  for dog in dogs:
    if dog[0] == dog_id:
      # print dog[3]
      return dog
  return None

if __name__ == "__main__":
  # Load our paths form the config
  paths = load_config()
  # print paths["base_image_path"]
  # print paths["sqlite3_path"]

  # Load in all our cascades
  cascades = load_cascades()
  # print cascades

  # Create our FaceRecognizer model
  recognizer = fr.FaceRecognizer()
  images, labels = [], []

  # Create MySQL connections and cursors
  dog_conn = mysql.connector.connect(user='root', password='1dontknow', host='127.0.0.1', database='dog_face')
  webapp_conn = mysql.connector.connect(user='root', password='1dontknow', host='127.0.0.1', database='here_doggie')
  dog_cursor = dog_conn.cursor()
  webapp_cursor = webapp_conn.cursor()

  # Query search request with ID
  search_id = sys.argv[1]
  webapp_cursor.execute("select date_lost, photo_file_name, num_results from searches where id=%s", (search_id,))
  request = webapp_cursor.fetchone()

  # Search criteria
  date_lost = request[0]
  photo_file_name = str(request[1])
  num_results = request[2]

  # Image to be recognized details
  # base_path = paths["base_image_path"]
  base_path = "/Users/Tyler/Documents/School/SeniorDesign/WebAppPrototypes/HereDoggie/public/system/samples/" # For testing
  photo_full_path = os.path.join(base_path, search_id, 'normal', photo_file_name)
  # print date_lost
  # print photo_file_name
  # print photo_full_path
  # print num_results

  try:
    # Detect dog face
    img = detectFace(photo_full_path, cascades)
    cv2.imwrite("detected.png", img) # For Debugging
    # If no face is detected raise an exception
    if img is None:
      raise Exception("Problems detecting face. Please use another image.")

    #Query all possible dog images from Dog DB
    dog_cursor.execute("select dogs.dogID, photos.filename, photos.path, dogs.listingURL, dogs.description from dogs join photos on dogs.dogID = photos.dogID")
    possible_dogs = dog_cursor.fetchall()
    db_photo_base_path = str(possible_dogs[0][2])
    # print len(possible_dogs)

    # Fill images and labels with possible dogs
    for possible_dog in possible_dogs:
      # print str(possible_dog[1])
      # print str(possible_dog[2])
      images.append(str(possible_dog[1]))
      labels.append(possible_dog[0])

    # Loop until we run out of dogs or we get design number of results
    for n in range(min(len(possible_dogs), num_results)):
      # Train the recognizer
      recognizer.train(db_photo_base_path, images, labels)
      print "Recognizer trained with", len(images), "images."

      # Run Recognition on the image
      # print os.path.dirname(photo_full_path)
      photo_path = os.path.dirname(photo_full_path)
      predicted_dog_id = recognizer.recognize(photo_path, photo_file_name)

      print "ID of predicted dog:", predicted_dog_id

      # Create Prediction records
      matched_dog = find_dog(predicted_dog_id, possible_dogs)
      # print search_id
      # print matched_dog[3]
      # print matched_dog[4]
      # print matched_dog[1]
      webapp_cursor.execute("insert into predictions (dog_id, search_id, url, description, photo_file_name) values (%s,%s,%s,%s,%s)", (predicted_dog_id, search_id, matched_dog[3], matched_dog[4], matched_dog[1]))
      webapp_conn.commit()
      print "Created Prediction record"

      # Take out the predicted image and label
      index = labels.index(predicted_dog_id)
      del images[index]
      del labels[index]

    # Update Search record status with "finished"
    webapp_cursor.execute("update searches set status=%s where id=%s", ("finished", search_id))
    webapp_conn.commit()

  except Exception as exc:
    print "Error:", exc
    print "Could not recognize image!!"
    # Update record with status of "failed"
    webapp_cursor.execute("update searches set status=%s where id=%s", ('failed', search_id))
    # webapp_conn.commit()

  # Close connections
  dog_conn.close()
  webapp_conn.close()
