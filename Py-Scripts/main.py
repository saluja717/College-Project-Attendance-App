import face_recognition
import cv2
import numpy as np
import os
import pandas as pd
import time
from mongo import store_db
import sys

import urllib.request
import time


if sys.argv[3] == "empty":
    num_cameras = 0
    video_capture_list = []
    for i in range(10):
        cap = cv2.VideoCapture(i)
        if not cap.isOpened():
            break
        else:
            num_cameras += 1
            video_capture_list.append(cap)
    print(f"Detected {num_cameras} cameras")
else:
    url = "http://" + sys.argv[3] + "/shot.jpg"

known_face_encodings = []
known_face_roll_no = []
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True
attendance_record = set([])
roll_record = {}

prev_frame_time = 0
new_frame_time = 0
name_col = []
roll_no_col = []
time_col = []
classid_col = []

df = pd.read_excel("students" + os.sep + "students_db.xlsx")

for key, row in df.iterrows():
    roll_no = row["roll_no"]
    name = row["name"]
    image_path = row["image"]
    classid = row["classid"]
    roll_record[roll_no] = name
    try:
        student_image = face_recognition.load_image_file("../public/assets/uploads" + os.sep + image_path)
        student_face_encoding = face_recognition.face_encodings(student_image)[0]
        known_face_encodings.append(student_face_encoding)
        known_face_roll_no.append(roll_no)
    except:
        print("../public/assets/uploads" + os.sep + image_path + " Student has not uploaded an image")
        continue


k = 0
while True:
    try:
        frames = []
        if sys.argv[3] == "empty":
            for video_capture in video_capture_list:
                ret, frame = video_capture.read()
                frames.append(frame)
        else:
            imgResp = urllib.request.urlopen(url)
            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            frames.append(cv2.imdecode(imgNp, -1))

        merged_frame = np.concatenate(frames, axis=1)
        merged_frame = cv2.flip(merged_frame, 2)

        rgb_small_frame =  cv2.cvtColor(merged_frame, cv2.COLOR_BGR2RGB)

        font = cv2.FONT_HERSHEY_SIMPLEX
        new_frame_time = time.time()

        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time
        fps = int(fps)
        fps = str(fps)
        if process_this_frame:
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
                name = "Unknown"
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    roll_no = known_face_roll_no[best_match_index]
                    name = roll_record[roll_no]
                    if roll_no not in attendance_record:
                        attendance_record.add(roll_no)
                        print(name, roll_no)
                        name_col.append(name)
                        roll_no_col.append(roll_no)
                        curr_time = time.localtime()
                        curr_clock = time.strftime("%H:%M:%S", curr_time)
                        time_col.append(curr_clock)

                face_names.append(name)

        process_this_frame = not process_this_frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            cv2.rectangle(merged_frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(merged_frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(merged_frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        cv2.imshow("Video", merged_frame)

    except Exception as e:
        print("Something is miss interpreted :", e)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

classid_col.append(classid)
data = {"Name": name_col, "RollNo": roll_no_col, "Time": time_col, "Class": classid_col}
print(data)

curr_time = time.localtime()
curr_clock = time.strftime("%c", curr_time)
# print(curr_clock)
file_name = ""
space = 0
for i in range(0, len(curr_clock)):
    s = curr_clock[i]
    if s == " " and curr_clock[i + 1] == " ":
        continue
    else:
        file_name += s

log_file_name = file_name

store_db(log_file_name, sys.argv[1], data)


if sys.argv[3] == "empty":
    video_capture.release()
cv2.destroyAllWindows()
