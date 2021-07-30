# -*- coding: utf-8 -*-
from video_processing import video_process as vp
from video_processing import image_process as ip
import time

print("Start processing")
start_time = time.time()

#parámetros para crear resumen estadísitico
team1 = {'name': 'Barcelona A', 'goal': 2, 'posession': 60, 'corner': 5, 'fault': 10, 'penalty': 1}
team2 = {'name': 'Real Madrid B', 'goal': 0, 'posession': 40, 'corner': 1, 'fault': 15,'penalty': 0}
statspath = "./dependencies/stats-13_07_2021-13_49_37.png"

# parámetros para crear video
htimestrs = ['00:00:29', '00:00:43', '00:00:58', '00:01:13', '00:01:30', '00:01:45']
videopath1 = "./output/cam1-13_07_2021-15_51_23.avi"
videopath2 = "./output/cam2-13_07_2021-15_51_23.avi"
outpath = "./output/highlights.mp4"
intropath = "./dependencies/intro.mp4"
outropath = "./dependencies/outro.mp4"
audiopath = "./dependencies/audio.mp3"

# se guarda el resumen
ip.create_report(team1, team2, statspath, root='./dependencies/')

#se guarda el video
vp.create_highlights(htimestrs, videopath1, videopath2, outpath, statspath=statspath, intropath=intropath, outropath=outropath, audiopath=audiopath)

print("Done in %s seconds" % round(time.time() - start_time,2))