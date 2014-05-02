import face_detector as fd
import face_recognizer as fr
import mysql.connector
import sqlite3
import sys
import os


def detectFace(path, cascades):
  for cascade in cascades:
    img = cascade.detect(path)
    if img is not None:
      return img
  return None


if __name__ == "__main__":
  config = {}
  execfile("paths.conf", config)

  base_path = config["base_image_path"]

  # Maybe load all cascades in a certain directory
  # So we can run detection with multiple cascades
  cascade20 = fd.FaceDetector('./cascades/cascade20-2-26-14.xml')
  cascade28 = fd.FaceDetector('./cascades/cascade28-2-28-14.xml')
  cascade10 = fd.FaceDetector('./cascades/cascade10-3-16.xml')
  cascades = [cascade20, cascade28, cascade10]
  # detector = fd.FaceDetector('./cascades/cascade20-2-26-14.xml')

  recognizer = fr.FaceRecognizer()
  images, labels = [], []

  # Create MySQL and SQLite3 connections and cursors
  dog_conn = mysql.connector.connect(user='root', password='1dontknow', host='127.0.0.1', database='dog_face')
  webapp_conn = sqlite3.connect(config["sqlite3_path"])
  dog_cursor = dog_conn.cursor()
  webapp_cursor = webapp_conn.cursor()

  # Query record with ID
  webapp_cursor.execute("select id, date_lost, photo_file_name, num_results from searches where id=?", (sys.argv[1],))
  request = webapp_cursor.fetchone()

  search_id = str(request[0])
  date_lost = request[1]
  photo_file_name = str(request[2])
  num_results = request[3]
  photo_full_path = os.path.join(base_path, search_id, 'normal', photo_file_name)

  try:
    # for cascade in cascades:
    #   img = detector.detect(os.path.join(base_path, str(request[0]), 'normal', str(request[2])))
    #   if img is not None:
    #     break

    # Detect dog face
    img = detectFace(photo_full_path, cascades)
    # If no face is detected raise an error
    if img is None:
      raise Exception("Problems detecting face. Please use another image.")
    # img = detector.detect(os.path.join(base_path, str(request[0]), 'normal', str(request[2])))

    # Query all possible dog images from Dog DB
    dog_cursor.execute("select dogs.dogID, photos.filename, photos.path, dogs.listingURL from dogs join photos on dogs.dogID = photos.dogID")
    possible_dogs = dog_cursor.fetchall()
    
    # Add all possible dogs and dogIDs to our train images and labels lists
    for possible_dog in possible_dogs:
      images.append(str(possible_dog[1]))
      labels.append(possible_dog[0])


    # Time for Recognition kids
    for n in range(num_results):
      # Train the recognizer
      recognizer.train(str(possible_dogs[0][2]), images, labels)
      print "Recognizer trained with", len(images), "images."

      # Run recognition on the image
      path = os.path.join(base_path, str(request[0]), 'normal')
      request_id = recognizer.recognize(path, str(request[2]))

      print "ID of predicted dog:", result_id

      # Create Prediction record
      webapp_cursor.execute("insert into predictions (dog_id, search_id, url) values (?,?,?)", (result_id, request[0]))









    # Train the recognizer
    recognizer.train(str(possible_dogs[0][2]), images, labels)
    print "Recognizer trained with", len(images), "images."

    # Run recognition on image
    path = os.path.join(base_path, str(request[0]), 'normal')
    result_id = recognizer.recognize(path, str(request[2]))

    print "ID of predicted dog:", result_id

    # Update Search record status with "finished"
    webapp_cursor.execute("update searches set status=? where id=?", ("finished", request[0]))
    # webapp_conn.commit()

    # Create Prediction records
    webapp_cursor.execute("insert into predictions (dog_id, search_id, url) values (?,?,?)", (result_id, request[0], "http://google.com"))
    webapp_conn.commit()
    print "Prediction records created"

  except Exception as exc:
    print "Error:", exc
    print "Could not recognize image!!"
    # Update record with status of "failed"
    webapp_cursor.execute("update searches set status=? where id=?", ('failed', request[0]))
    # webapp_conn.commit()

  # Close connections
  dog_conn.close()
  webapp_conn.close()
