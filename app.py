# Import necessary libraries.
from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from cv2 import cv2
from threading import Thread
import time
from datetime import datetime
import os
import sys

# Developed dependencies.
from video_processing import video_process as vp
from video_processing import image_process as ip

# Video stream widget class.
from video_stream import video_stream_widget as vs

# Initialize the Flask app.
app = Flask(__name__)

# URL for the cameras.
camlink1 = "rtsp://192.168.0.2:554/h264?username=admin&password=123456"
camlink2 = "rtsp://192.168.0.3:554/h264?username=admin&password=123456"

# Global variables.
selected_team = 1
show_web = True
initial_time = time.time()
# Datetime object containing current date and time.
now = datetime.now()

# Statistics variables.
time_list = []
team_a = {
    'name': 'Barcelona A',
    'goal': 0,
    'posession': 0,
    'corner': 0,
    'fault': 0,
    'penalty': 0
}
team_b = {
    'name': 'Real Madrid B',
    'goal': 0,
    'posession': 0,
    'corner': 0,
    'fault': 0,
    'penalty': 0
}

# Media paths.
# Paths of the camera records.
path1 = "./output/cam1-" + now.strftime("%d_%m_%Y-%H_%M_%S") + ".avi"
path2 = "./output/cam2-" + now.strftime("%d_%m_%Y-%H_%M_%S") + ".avi"
# Path of the statistics.
report_path = "./output/stats-" + now.strftime("%d_%m_%Y-%H_%M_%S") + ".png"
# Path of the highlights video.
highlights_path = "./output/highlights-" + now.strftime("%d_%m_%Y-%H_%M_%S") + ".mp4"


# Global methods.
def manage_statistics(team_number, statistic):
    if team_number == 1:
        team_a[statistic] += 1
    else:
        team_b[statistic] += 1


# Define app route for default page of the web-app.
@app.route('/')
def index():
    return render_template('index.html')


# Rendering the HTML page which has the button.
@app.route('/json')
def json():
    return render_template('json.html')


# Background process happening without any refreshing.
@app.route('/team_1')
def team_1():
    global selected_team
    selected_team = 1
    print("Team " + str(selected_team) + " selected.")
    return "nothing"


@app.route('/team_2')
def team_2():
    global selected_team
    selected_team = 2
    print("Team " + str(selected_team) + " selected.")
    return "nothing"


@app.route('/goal')
def goal():
    event_time = time.strftime('%H:%M:%S', time.gmtime(int(time.time() - initial_time)))
    time_list.append(event_time)
    print("There was a goal for the team " + str(selected_team) + " at " + event_time + ".")
    manage_statistics(selected_team, 'goal')
    return "nothing"


@app.route('/shoot')
def shoot():
    event_time = time.strftime('%H:%M:%S', time.gmtime(int(time.time() - initial_time)))
    time_list.append(event_time)
    print("There was a shoot for the team " + str(selected_team) + " at " + event_time + ".")
    return "nothing"


@app.route('/outstanding_play')
def outstanding_play():
    event_time = time.strftime('%H:%M:%S', time.gmtime(int(time.time() - initial_time)))
    time_list.append(event_time)
    print("There was an outstanding play for the team " + str(selected_team) + " at " + event_time + ".")
    return "nothing"


@app.route('/corner')
def corner():
    event_time = time.strftime('%H:%M:%S', time.gmtime(int(time.time() - initial_time)))
    time_list.append(event_time)
    print("There was a corner for the team " + str(selected_team) + " at " + event_time + ".")
    manage_statistics(selected_team, 'corner')
    return "nothing"


@app.route('/fault')
def fault():
    event_time = time.strftime('%H:%M:%S', time.gmtime(int(time.time() - initial_time)))
    time_list.append(event_time)
    print("There was a fault for the team " + str(selected_team) + " at " + event_time + ".")
    manage_statistics(selected_team, 'fault')
    return "nothing"


@app.route('/penalty')
def penalty():
    event_time = time.strftime('%H:%M:%S', time.gmtime(int(time.time() - initial_time)))
    time_list.append(event_time)
    print("There was a penalty for the team " + str(selected_team) + " at " + event_time + ".")
    manage_statistics(selected_team, 'penalty')
    return "nothing"


@app.route('/pause')
def pause():
    show_web = False
    event_time = time.strftime('%H:%M:%S', time.gmtime(int(time.time() - initial_time)))
    print("Pausing the recording at " + event_time + ".")
    video_stream_widget.record = False
    video_stream_widget.show_frame()
    print("Camera 1 closed.")
    video_stream_widget2.record = False
    video_stream_widget2.show_frame()
    print("Camera 2 closed.")
    return "nothing"


@app.route('/export')
def export():
    print("Exporting operations.")

    # Get non corrupted files.
    video_path_list = []
    for file in os.listdir("./output/"):
        if os.path.getsize("./output/" + file):
            video_path_list.append("./output/" + file)
    print(video_path_list[0])
    print(video_path_list[1])
    print(time_list)

    # Create reports.
    ip.create_report(
        team1=team_a,
        team2=team_b,
        pathout=report_path,
        root='./dependencies/'
    )

    # Create highlights video.
    vp.create_highlights(
        htimestrs=time_list,
        videopath1=video_path_list[0],
        videopath2=video_path_list[1],
        outpath=highlights_path,
        statspath=report_path,
        intropath='./dependencies/intro.mp4',
        outropath='./dependencies/outro.mp4',
        audiopath='./dependencies/audio.mp3'
    )

    return "nothing"


# Define app route for the video feeds.
if show_web:
    @app.route('/video_feed1')
    def video_feed1():
        return Response(video_stream_widget.show_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


    @app.route('/video_feed2')
    def video_feed2():
        return Response(video_stream_widget2.show_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Start the Flask server.
if __name__ == "__main__":

    for source in range(4):
        cap = cv2.VideoCapture(source)
        if cap is None or not cap.isOpened():
            print('Warning: unable to open video source: ', source)

    # Initialize the video stream widget threads.
    video_stream_widget = vs.VideoStreamWidget(camlink1, "Camera 1", path1)
    video_stream_widget2 = vs.VideoStreamWidget(camlink2, "Camera 2", path2)

    # Initialize the webserver thread.
    web_server = Thread(target=app.run(debug=True))
    web_server.daemon = True
    web_server.start()
