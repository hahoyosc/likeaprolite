# Import necessary libraries.
from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
from cv2 import cv2
from threading import Thread
import time
from datetime import datetime
import os
from argparse import ArgumentParser
import sys

# Developed dependencies.
from video_processing import video_process as vp
from video_processing import image_process as ip

# Video stream widget class.
from video_stream import video_stream_widget as vs

# Initialize the Flask app.
app = Flask(__name__)

# Global variables.
selected_team = 1
show_web = True
initial_time = time.time()
# Datetime object containing current date and time.
now = datetime.now()
cameras = 0
video_stream_widget_list = []

# Statistics variables.
time_list = []
team_a = {
    'name': 'Barcelona A',
    'goal': 0,
    'possession': 0,
    'corner': 0,
    'fault': 0,
    'penalty': 0
}
team_b = {
    'name': 'Real Madrid B',
    'goal': 0,
    'possession': 0,
    'corner': 0,
    'fault': 0,
    'penalty': 0
}
start_possession = datetime.now()
team_a_possession = datetime.now()
team_b_possession = datetime.now()
pivot_possession = datetime.now()

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
@app.route('/change_team')
def team_1():
    global selected_team, pivot_possession, team_a_possession, team_b_possession

    if selected_team == 1:
        print("Team 2 selected.")
        selected_team = 2
        pivot_possession = datetime.now() - pivot_possession
        team_a_possession = pivot_possession + team_a_possession
        pivot_possession = datetime.now()

    else:
        print("Team 1 selected.")
        selected_team = 1
        pivot_possession = datetime.now() - pivot_possession
        team_a_possession = pivot_possession + team_a_possession
        pivot_possession = datetime.now()

    return "nothing"


@app.route('/start_match')
def team_2():
    global start_possession
    start_possession = datetime.now()
    print("Starting possession counter.")

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
    for camera in range(cameras):
        video_stream_widget_list[camera].record = False
        video_stream_widget_list[camera].show_frame()
        print("Camera " + str(camera) + " closed.")

    return "nothing"


@app.route('/export')
def export():
    print("Exporting operations.")

    # Get non corrupted files.
    video_path_list = []
    for file in os.listdir("./output/"):
        if os.path.getsize("./output/" + file):
            file_path = "./output/" + file
            video_path_list.append(file_path)
            print(file_path)
    print(time_list)

    # Ball possession update.
    final_possession = datetime.now() - start_possession
    percentage_a_possession = team_a_possession / final_possession * 100
    percentage_b_possession = team_b_possession / final_possession * 100
    team_a['possession'] = percentage_a_possession
    team_b['possession'] = percentage_b_possession

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
        return Response(video_stream_widget_list[0].show_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


    @app.route('/video_feed2')
    def video_feed2():
        return Response(video_stream_widget_list[1].show_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Start the Flask server.
if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument('-c', '--cameras', type=int, default=2, required=False, help="Number of cameras",)
    args = parser.parse_args()
    cameras = args.cameras

    for camera in range(cameras):
        # Path of the camera record.
        path = "./output/cam" + str(camera) + "-" + now.strftime("%d_%m_%Y-%H_%M_%S") + ".avi"
        video_stream_widget_list.append(vs.VideoStreamWidget(camera, "Camera " + str(camera), path))

    # Initialize the webserver thread.
    web_server = Thread(target=app.run(debug=True))
    web_server.daemon = True
    web_server.start()
