from flask import Flask, render_template, Response, request
import requests
import numpy as np
import cv2

from ultralytics import YOLO
import random

# Initialize the Flask app
app = Flask(__name__)

# cam_ip = ["192.168.1.3:6677"]
current_cam = 0
# url_video = "http://"+cam_ip[current_cam]+"/videofeed?username=&password="

# opening the file in read mode
my_file = open("G:/Object_Detection-main/utils/coco.txt", "r")

# reading the file
data = my_file.read()


# replacing end splitting the text | when newline ('\n') is seen.
class_list = data.split("\n")
my_file.close()


# Generate random colors for class list
detection_colors = []

for i in range(len(class_list)):

    r = random.randint(0, 255)

    g = random.randint(0, 255)

    b = random.randint(0, 255)

    detection_colors.append((b, g, r))


# load a pretrained YOLOv8n model
model = YOLO("weights/yolov8n.pt", "v8")


# Vals to resize video frames | small frame optimise the run
frame_wid = 640
frame_hyt = 480

def gen_frames():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print("Cannot open camera")

        exit()

    while True:

        # Capture frame-by-frame
        success, frame = cap.read()

        # if frame is read correctly ret is True

        if not success:

            print("Can't receive frame (stream end?). Exiting ...")

            break

        #  resize the frame | small frame optimise the run

        frame = cv2.resize(frame, (frame_wid, frame_hyt))

        # Predict on image

        detect_params = model.predict(source=[frame], conf=0.45, save=False)

        # Convert tensor array to numpy

        DP = detect_params[0].numpy()

        if len(DP) != 0:

            for i in range(len(detect_params[0])):
                print(i)

                boxes = detect_params[0].boxes

                box = boxes[i]  # returns one box

                clsID = box.cls.numpy()[0]

                conf = box.conf.numpy()[0]

                bb = box.xyxy.numpy()[0]

                cv2.rectangle(

                    frame,

                    (int(bb[0]), int(bb[1])),

                    (int(bb[2]), int(bb[3])),

                    detection_colors[int(clsID)],

                    3,
                )

                # Display class name and confidence

                font = cv2.FONT_HERSHEY_COMPLEX

                cv2.putText(

                    frame,

                    class_list[int(clsID)]

                    + " "

                    + str(round(conf, 3))

                    + "%",

                    (int(bb[0]), int(bb[1]) - 10),

                    font,

                    1,

                    (255, 255, 255),

                    2,
                )
        success, buffer = cv2.imencode('.jpg', frame)

        frame = buffer.tobytes()

        yield (b'--frame\r\n'

               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/video_feed')
def video_feed():

    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/button_con', methods=['POST'])
def button_con():

    btn_name = request.form['button_name']

    global current_cam

    if (btn_name == 'con_rot'):

        requests.post("http://"+cam_ip[current_cam]+"/rotatecamera")

    elif (btn_name == 'con_fl'):

        requests.post("http://"+cam_ip[current_cam]+"/flashlight_on_off")

    elif (btn_name == 'con_cam'):

        requests.post("http://"+cam_ip[current_cam]+"/camera_switch")

    print(btn_name)

    return '', 204


@app.route('/button_view', methods=['POST'])
def button_view():

    btn_name = request.form['button_name']
    print(btn_name)

    if (btn_name == 'cam_v1'):

        updateSelectedIPCam(1)

        return render_template('index.html')

    elif (btn_name == 'cam_v2'):

        updateSelectedIPCam(2)

        return render_template('index.html')

    elif (btn_name == 'cam_v3'):

        updateSelectedIPCam(3)

        return render_template('index.html')

    elif (btn_name == 'cam_v4'):

        updateSelectedIPCam(4)

        return render_template('index.html')

    else:

        return '', 404


def updateSelectedIPCam(sel_cam: int):

    global current_cam,url_video
    current_cam = sel_cam - 1
    print("Current Camera view is ", sel_cam)
    url_video = "http://"+cam_ip[current_cam]+"/videofeed?username=&password="


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
