#!/usr/bin/env python3
# 


import numpy as np
from midiutil import MIDIFile
from PIL import Image
import matplotlib.image as mpimg
import random
import gdal
import os
from pyproj import Proj, transform
import osr
import operator

import subprocess


def arpeggio(x):
    dic = {0:0, 
           1:4,
           2:7,
           3:12,
           4:16, 
           5:12,
           6:7,
           7:4,
           8:0,
           9:4,
           10:7,
           11:12,
           12:16,
           13:12,
           14:7,
           15:4}
    return dic[x]

# Generates a thematic song in MIDI from input raster data. Four themes are available with more to come: A calming water song (WATER), a celtic-inspired country grassland style (GRASSLAND), soothing harp (FOREST), and an intimidating mountain war march (MOUNTAIN). Further fine-tuning can be done within the method. 
def generate_song(image, theme="WATER", output="/tmp/default.mid"):
    rhythms_lst = {"WATER":[    [1, 1, 1, 0.5, 0.5],
                                [2, 2],
                                [0.5, 0.5, 0.5, 1.5, 0.5, 0.25, 0.25],
                                [1, 1, 1, 1]],
                   "MOUNTAIN":[ [0.25, 0.25, 0.25, 0.25, 0.5, 0.5, 1, 0.5, 0.5],
                                [1, 1, 1, 0.5, 0.5],
                                [1, -2.5, 0.5],
                                [0.25, 0.25, 0.25, 1.25, -0.5, 0.5, 0.25, 0.25, 0.25, 0.25]],
                   "GRASSLAND":[[1, 0.5, 1, 0.5, 1, 0.5, 1.5],
                                [1.5, 1.5, 0.5, 0.5, 0.5, 1.5],
                                [6]],
                   "FOREST":[   [0.5, -0.5, 0.5, -0.5, 0.25, 0.75],
                                [-0.5, 0.5, -0.5, 0.25, 0.25, 0.25, 0.25, 0.5, -0.5, 0.5]]
                                }
    accompaniment_lst = {"WATER":[[3, 1],
                                  [1, 1, 1, 1],
                                  [1.5, 0.5, 0.5, 1],
                                  [2, 2]],
                     "MOUNTAIN":[ [0.5, 0.5, -1.5, 0.5, 0.5 -0.5],
                                  [0.5, 0.5, 1, 0.5,0.5, 1],
                                  [-1, 0.25,0.25,0.25,0.25, -0.5, 0.5],
                                  [1.5, 0.5, 0.25,0.25,0.25,0.25,0.25,0.25,0.25,0.25]],
                     "GRASSLAND":[[3, 3],
                                  [6], 
                                  [2, 1, 2, 1]],
                     "FOREST":[   [0.25] * 16, 
                                  [0.25] * 16]
                                  }
    # Defines how many scale degrees will be used in each theme
    degrees_lst = {"WATER":5, 
                   "MOUNTAIN":6, 
                   "GRASSLAND":4,
                   "FOREST":3}
    # Set the tempo of each theme
    tempo={"WATER":130, 
           "MOUNTAIN":100, 
           "GRASSLAND":130,
           "FOREST":60}

    rhythms = rhythms_lst[theme]
    accompaniment = accompaniment_lst[theme]
    # Initialize MIDI object 
    MyMIDI = MIDIFile(1)
    track = 0
    time = 0 
    MyMIDI.addTrackName(track, time, "SONGSAT")
    MyMIDI.addTempo(track, time, tempo[theme])

    # Read in raster data
    landsat_clip_path = image
    img = mpimg.imread(landsat_clip_path).flatten()

    # Eliminate any possible nodata values included to avoid widely repeated notes
    pentatonic = list(filter(lambda x: x != 255, img)) 

    # Normalize raster data to the number of degrees of the scale
    pentatonic = list(map(lambda x: (x % degrees_lst[theme]) + 1, pentatonic))
    
    # Shorten the data to be a reasonable song length
    melody = pentatonic[::int(len(pentatonic) / 650)]
    
    # Initialize the scale used for the thematic tune
    scales = {"WATER":{1:0, 2:2, 3:4, 4:7, 5:9},
              "MOUNTAIN":{1:0, 2:2, 3:3, 4:4, 5:5, 6:8},
              "GRASSLAND":{1:0, 2:4, 3:7, 4:9},
              "FOREST":{1:0, 2:2, 3:4}}
    scale = scales[theme]

    x = 0
    # The base octave that this song begins at. Set to an octave above middle C (60) with modifier.
    octaves = {"WATER":60 + 12,
               "MOUNTAIN":60 - 12,
               "GRASSLAND":60 + 6,
               "FOREST":60}
    octave = octaves[theme] + random.randint(-6, 6)
    
    # Keep track of when midi events happen 
    time_upper = 0
    time_lower = 0

    # Loop through the melody notes and apply rhythms
    while x < len(melody):
        try:
            rhythm_indice = random.randint(0, len(rhythms) - 1)
            r = rhythms[rhythm_indice]
            b = accompaniment[rhythm_indice]
            starting_note = scale[melody[x]]
            last_note = scale[melody[x]] + octave
            for i in range(0, len(r)):
                note = scale[melody[x]] + octave 
                #Ugly jump - keep melody smooth.
                if abs(note - last_note) > 8:
                    if note > last_note:
                        note -= 12
                        octave -= 12
                    else:
                        note += 12
                        octave += 12
                if note > 255:
                    note -= 12
                    octave -= 12
                
                duration = r[i]
                last_note = note 

                if duration > 0:
                    MyMIDI.addNote(track, 0, note + 12, time_upper, duration, 100)
                    # Mountain sounds great with octave doubling.
                    if theme == "MOUNTAIN":
                        MyMIDI.addNote(track, 0, note, time_upper, duration, 100)
                else:
                    # Rests are denoted with negative beats.
                    duration *= -1
                time_upper += duration

                x+=1
            for i in range(0, len(b)):
                if theme != "MOUNTAIN":
                    lnote = int(starting_note + octave - 12 - ((i % 2) * 12))
                else:
                    lnote = int(starting_note + octave - 12)
                if lnote < 0:
                    lnote += 12
                if lnote > 255:
                    lnote -= 12
                #print(lnote)
                if b[i] > 0:
                    if theme != "FOREST":
                        MyMIDI.addNote(track, 1, 
                                       lnote,
                                       time_lower, b[i], 100)
                    else:
                        MyMIDI.addNote(track, 1, 
                                       lnote + arpeggio(i),
                                       time_lower, b[i], 100)
                else:
                    b[i] *= -1
                time_lower += b[i]
            
        except Exception as e:
            print(e)
    # Add nice chord to end of water theme
    if theme == "WATER":
        MyMIDI.addNote(track, 0, 60, time_upper, 4, 100)
        MyMIDI.addNote(track, 0, 67, time_upper, 4, 100)
        MyMIDI.addNote(track, 0, 72, time_upper, 4, 100)
        MyMIDI.addNote(track, 0, 84, time_upper, 4, 100)
    # Write out midi file to specified output. 
    binfile = open(output, 'wb')
    MyMIDI.writeFile(binfile)
    binfile.close()

def GetExtent(gt,cols,rows):
    ''' Return list of corner coordinates from a geotransform

        @type gt:   C{tuple/list}
        @param gt: geotransform
        @type cols:   C{int}
        @param cols: number of columns in the dataset
        @type rows:   C{int}
        @param rows: number of rows in the dataset
        @rtype:    C{[float,...,float]}
        @return:   coordinates of each corner
    '''
    ext=[]
    xarr=[0,cols]
    yarr=[0,rows]

    for px in xarr:
        for py in yarr:
            x=gt[0]+(px*gt[1])+(py*gt[2])
            y=gt[3]+(px*gt[4])+(py*gt[5])
            ext.append([x,y])
            
        yarr.reverse()
    return ext

def getCorners(image_path):
    ds=gdal.Open(image_path)
    proj = osr.SpatialReference(wkt=ds.GetProjection())
    projection_str = "epsg:"+ str(proj.GetAttrValue('AUTHORITY',1))
    inProj = Proj(init=projection_str)
    outProj = Proj(init='epsg:4326')
    gt=ds.GetGeoTransform()
    cols = ds.RasterXSize
    rows = ds.RasterYSize
    ext=GetExtent(gt,cols,rows)
    ul_lon = ext[0][0]
    ul_lat = ext[0][1]
    lr_lon = ext[2][0]
    lr_lat = ext[2][1]

    ul = inProj(ul_lon, ul_lat, inverse=True)
    lr = inProj(lr_lon, lr_lat, inverse=True)

    return [[ul[0], ul[1]], [lr[0], lr[1]]]


def getCentroid(image_path):
    ext = getCorners(image_path)
    
    ul = ext[0]
    lr = ext[1]   

    md_lat = (ul[0] + lr[0]) / 2.0 + 1
    md_lon = (ul[1] + lr[1]) / 2.0 + 1
    print(md_lon)
    # r = inProj(md_lon, md_lat, inverse=True)
    #print(r)

    print("{}, {}".format(md_lat, md_lon))

    #md_lat_wgs, md_lon_wgs = transform(inProj, outProj, md_lat, md_lon)
    return [md_lon, md_lat]

def getClassificationValue(loc):
    s =  [os.getcwd() + "/getClass/getclass", \
          str(loc[0]) , \
          str(loc[1])]
    p = subprocess.check_output(s)
    p = p.decode('UTF-8').replace("\n", "").replace("Value:", "").strip()
    return p

def getClassification(image_path, samples=0):
    # Samples defines the number of random samples placed in the image to generate  

    image_location = getCentroid(image_path)
    if samples > 0:
        p_dict = {}
        corners = getCorners(image_path)
        ul = corners[0]
        lr = corners[1]
        random_coords = [[float(random.uniform(ul[0], lr[0])),
                          float(random.uniform(ul[1], lr[1]))] for _ in range(samples)]
        random_coords.append(image_location)
        
        for c in random_coords:
            p = getClassificationValue(list(c))
            if p not in p_dict.keys():
                p_dict[p] = 1
            else:
                p_dict[p] += 1
        #print(p_dict)
        return max(p_dict.items(), key=operator.itemgetter(1))[0]
                

        
    else:
        p = getClassificationValue(image_location)
    return p

def songSAT(image_path, output_midi="/tmp/OUT.mid"):
    
    p = getClassification(image_path)
    if p == "MOUNTAIN":
        theme = "MOUNTAIN"
    elif p == "0":
        theme = "WATER"
    elif p == "1":
        theme = "FOREST"
    elif p == "6" or p == "12" or p == "14" or p == "15":
        theme = "GRASSLAND"
    else:
        theme = "FAILED"

    if theme == "FAILED":
        print("Sorry! This land cover is not yet supported by SongSAT! Check back again at a later time, or bug one of the developers on the project to implement it!")
    else:
        generate_song(image_path, theme,output_midi)


#songSAT("/home/alex/Documents/spaceapp/landsat/img.TIF")
print(getClassification("/home/alex/Documents/spaceapp/landsat/img.TIF", 300))