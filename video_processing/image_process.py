# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

def dtostr(d):
    """.py:function:: dtostr(d)
    convertir datos de un dict() a str
    :param dict d: diccionario de entrada
    :return dict: diccionario con datos tipo str
    """
    keys_values = d.items()
    res = {str(key): str(value) for key, value in keys_values}
    return res

def wresize(im, objw):
    """.py:function:: wresize(im,w)
    cambiar el tamaño de una imagen considerando solamente el ancho
    :param PIL.Image im: imagen de entrada
    :param int objw: ancho objetivo de la imagen de salida
    :return PIL.Image: Imagen con diferente tamaño
    """
    w,h = im.size
    r = objw/w
    imrs = im.resize((int(w*r),int(h*r)))
    return imrs

def repos(im, pos):
    """.py:function:: repos(pos)
    cambiar la poscisión para pegar una imagen de center-bottom a left-top
    :param PIL.Image im: imagen de entrada
    :param tuple pos: tupla con posición x,y en pixeles centrada en center-bottom
    :return repos: Imagen con diferente tamaño
    """
    w,h = im.size
    x,y = pos
    
    xn = x - w*0.5
    yn = y - h
    
    repos = (int(xn),int(yn))
    return repos
  
def create_report(team1, team2, pathout, root='', size=(1920, 1080)):
    """.py:function:: create_report(team1,team2,pathout,root="")
    crear y guardar la imagen de reporte de resultados y estadísiticos de partido
    :param dict team1: diccionario con los resultados del equipo 1 con 6 keys {'name','goal','pos','cor','foul','penal'}
    :param dict team2: diccionario con los resultados del equipo 2 con 6 keys {'name','goal','pos','cor','foul','penal'}
    :param str pathout: ruta para guaradar la imagen reultado
    :param str root: (opcional) carpeta donde se encuantran los archivos base, carpeta base del programa por defecto
    :param tuple size: (opcional) tula con tamaño de la imagen en pixeles (ancho,largo)
    """ 
    team1 = dtostr(team1)
    team2 = dtostr(team2)
    
    textsize = 40
    textcolor = (201, 199, 201)
    pos1 = [(300,900),(710,210),(710,385),(710,550),(710,700),(710,860)]
    pos2 = [(1640,900),(1215,210),(1215,385),(1215,550),(1215,700),(1215,860)]
    size = (1920,1080)
    poslogo1 = (300,800)
    poslogo2 = (1640,800)
    logow = 500
    
    font = ImageFont.truetype(root+"arialbd.ttf",textsize)
    
    statspath = root + 'base1.png'
    logo1path = root + 'logo1.png'
    logo2path = root + 'logo2.png'
    
    imagen = Image.open(statspath)
    imagen = imagen.resize(size)
    
    logo1 = Image.open(logo1path)
    logo2 = Image.open(logo2path)
    logo1 = wresize(logo1,logow)
    logo2 = wresize(logo2,logow)
    poslogo1 = repos(logo1,poslogo1)
    poslogo2 = repos(logo2,poslogo2)
    
    imagen.paste(logo1,poslogo1,logo1.convert('RGBA'))
    imagen.paste(logo2,poslogo2,logo2.convert('RGBA'))
    
    edit = ImageDraw.Draw(imagen)
    edit.text(pos1[0], team1['name'], textcolor, font=font,anchor = 'mm')
    edit.text(pos2[0], team2['name'], textcolor, font=font,anchor = 'mm')
    edit.text(pos1[1], team1['goal'], textcolor, font=font,anchor = 'mm')
    edit.text(pos2[1], team2['goal'], textcolor, font=font,anchor = 'mm')
    edit.text(pos1[2], team1['posession'], textcolor, font=font,anchor = 'mm')
    edit.text(pos2[2], team2['posession'], textcolor, font=font,anchor = 'mm')
    edit.text(pos1[3], team1['corner'], textcolor, font=font,anchor = 'mm')
    edit.text(pos2[3], team2['corner'], textcolor, font=font,anchor = 'mm')
    edit.text(pos1[4], team1['fault'], textcolor, font=font,anchor = 'mm')
    edit.text(pos2[4], team2['fault'], textcolor, font=font,anchor = 'mm')
    edit.text(pos1[5], team1['penalty'], textcolor, font=font,anchor = 'mm')
    edit.text(pos2[5], team2['penalty'], textcolor, font=font,anchor = 'mm')
    
    imagen.save(pathout)
    imagen.close()
