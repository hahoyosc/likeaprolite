# -*- coding: utf-8 -*-
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips, ImageClip
import moviepy.video.fx.all as vfx
from datetime import datetime

def create_highlights(htimestrs, videopath1, videopath2, outpath, statspath,
                      size=(1920, 1080), intropath='intro.mp4', outropath='outro.mp4',
                      audiopath='audio.mp3', verbose=False):
    """.py:function:: wresize(im,w)
    generar y guardar el video de jugadas destacadas de un partido a partir 
    de las grabaciones de dos cámaras guardadas previamente en disco
    :param list htimestrs: lista de str con los tiempos de finalización de las jugadas tipo %H:%M:%S
    :param str videopath1: ruta del video de grabación de la cámara 1
    :param str videopath2: ruta del video de grabación de la cámara 2
    :param str outpath: ruta del video de salida
    :param str statspath: ruta de la imagen de resumen estadístico del partido
    :param tuple size: (opcional) tula con tamaño del video en pixeles (ancho,largo)
    :param str intropath: (opcional) ruta con el video de entrada
    :param str outropath: (opcional) ruta con el video de salida
    :param str audiopath: (opcional) ruta con el audio base
    :param Boolean verbose: (opcional) flag para mostrar o no el progreso
    """
    num_clips = len(htimestrs)
    lag_time = 10
    add_time = 10
    sus_time = 10
    
    intro = VideoFileClip(intropath)
    intro = intro.fx(vfx.resize, newsize=size)
    outro= VideoFileClip(intropath)
    outro = outro.fx(vfx.resize, newsize=size)
    
    video1 = VideoFileClip(videopath1)
    video1 = video1.fx(vfx.resize, newsize=size)
    video2 = VideoFileClip(videopath2)
    video2 = video2.fx(vfx.resize, newsize=size)
    audio = AudioFileClip(audiopath)
    
    stats = ImageClip(statspath).set_duration(15)
    stats = stats.fx(vfx.resize, newsize=size)
    
    htimes = []
    for i in range(num_clips):
        timestr = htimestrs[i]
        htime = datetime.strptime(timestr,'%H:%M:%S')
        htime = htime.second + htime.minute*60 + htime.hour*3600
        htimes.append(htime)
    
    clips = []
    final_clip = intro
    for i in range(num_clips):
        htime1 = htimes[i]
        hclip1 = video1.subclip(htime1-sus_time, htime1)
        hclip2 = video1.subclip(htime1+lag_time, htime1+lag_time+add_time)
        final_clip = concatenate_videoclips([final_clip, hclip1, hclip2])
        clips.append(hclip1)
        clips.append(hclip2)
    
    final_clip = concatenate_videoclips([final_clip,outro])
    final_clip = concatenate_videoclips([final_clip,stats])
    final_clip = concatenate_videoclips([final_clip,outro])
    
    audio = audio.subclip(0,final_clip.duration)
    videofinal =  final_clip.set_audio(audio)
    
    videofinal.write_videofile(outpath, verbose=verbose)
