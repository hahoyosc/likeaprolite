# Import necessary libraries.
from flask import Flask, render_template, Response
import cv2
import imutils
import threading
import time

# Initialize the Flask app.
app = Flask(__name__)

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
outputFrame1 = None
outputFrame2 = None
lock1 = threading.Lock()
lock2 = threading.Lock()

# Capture Video using OpenCV.
cam1 = cv2.VideoCapture('rtsp://192.168.0.2:554/h264?username=admin&password=123456')
#cam2 = cv2.VideoCapture('rtsp://192.168.0.3:554/h264?username=admin&password=123456')
#cam2 = cv2.VideoCapture(0)
time.sleep(2.0)

def rescale_frame(frame, percent=25):
    width = int(frame.shape[1] * percent / 100)
    height = int(frame.shape[0] * percent / 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)

def stream1(frameCount):
    global outputFrame1, lock1
    if cam1.isOpened():
        while True:
            ret_val, frame = cam1.read()
            if frame.shape:
                frame = rescale_frame(frame, 50)
                with lock1:
                    outputFrame1 = frame.copy()
            else:
                continue 
    else:
        print('Camera 1 open failed.')

def stream2(frameCount):
    global outputFrame2, lock2
    if cam2.isOpened():
        while True:
            ret_val, frame = cam2.read()
            if frame.shape:
                frame = rescale_frame(frame, 50)
                with lock2:
                    outputFrame2 = frame.copy()
            else:
                continue 
    else:
        print('Camera 2 open failed.')

# Adding window and generating frames from the camera.
def generate1():
     # grab global references to the output frame and lock variables
    global outputFrame1, lock1
    
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock1:
            # check if the output frame is available, otherwise skip the iteration of the loop
            if outputFrame1 is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame1)
 
            # ensure the frame was successfully encoded
            if not flag:
                continue

        # Concat frame one by one and show result.
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

def generate2():
     # grab global references to the output frame and lock variables
    global outputFrame2, lock2
    
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock2:
            # check if the output frame is available, otherwise skip the iteration of the loop
            if outputFrame2 is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame2)
 
            # ensure the frame was successfully encoded
            if not flag:
                continue

        # Concat frame one by one and show result.
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

# Define app route for default page of the web-app.
@app.route('/')
def index():
    return render_template('index.html')

# Define app route for the video feed.
@app.route('/video_feed1')
def video_feed1():
    return Response(generate1(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Define app route for the video feed.
'''@app.route('/video_feed2')
def video_feed2():
    return Response(generate2(), mimetype='multipart/x-mixed-replace; boundary=frame')'''

# Start the Flask server.
if __name__ == "__main__":
    
    t1 = threading.Thread(target=stream1, args=(32,))
    #t2 = threading.Thread(target=stream2, args=(32,))
    
    t1.daemon = True
    #t2.daemon = True

    t1.start()
    #t2.start()

    app.run(debug=True)

# release the video stream pointer
cam1.release()
cv2.destroyAllWindows()