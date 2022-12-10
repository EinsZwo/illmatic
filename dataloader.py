'''
Created on Jun 9, 2022

@author: Eins Zwo
'''



import os
import json
from datetime import datetime
from collections import Counter
from matplotlib import pyplot as plt
from illmatic import util
import xml.etree.ElementTree as ET




def getFiles(artistNames = [],dataFolder=util.DATA_FOLDER):
    artist_files = []
    for filename in os.listdir(dataFolder):
        
        fileInfo = os.path.splitext(filename)
        
        if(fileInfo[1] != ".json"):
            continue
        
        if(artistNames and fileInfo[0] not in artistNames):
            continue
        """
        rel_dir = os.path.relpath(dir_, DATA_FOLDER)
        rel_file = os.path.join(rel_dir, filename)
        """
        artist_files.append(filename)
            
    return artist_files
        


def getDiscographyInfo(artistNames = []):
    artists = []
    songTitles =  []
    songLyrics = []
    
    script_dir = os.path.dirname(os.path.abspath(__file__))

    fileNames = getFiles(artistNames)
    for fileName in fileNames:
        rel_path = util.DATA_FOLDER + "/" + fileName
        abs_file_path = os.path.join(script_dir, rel_path)
        file = open(abs_file_path, "r", encoding='utf-8')
        loaded = json.load(file)
        
        for song in loaded['songs']:
            artists.append(song['artist'])
            songTitles.append(song['title'])
            songLyrics.append(song['lyrics'])
            
        file.close()
        
    return artists, songTitles, songLyrics


def getJsonArtists(artistNames = []):
    
    artists = []
    script_dir = os.path.dirname(os.path.abspath(__file__))

    fileNames = getFiles(artistNames)
    for fileName in fileNames:
        rel_path = util.DATA_FOLDER + "/" + fileName
        abs_file_path = os.path.join(script_dir, rel_path)
        file = open(abs_file_path, "r", encoding='utf-8')
        artists.append(json.load(file))
        
    return artists
        


    
def loadFile(filename,fileFolder=util.DATA_FOLDER):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rel_path = fileFolder + "/" + filename
    abs_file_path = os.path.join(script_dir, rel_path)
    
    file = open(abs_file_path)
    artist = json.load(file)
    return artist



def getReleaseDate(jsonSong):
    if 'release_date' in jsonSong and jsonSong['release_date'] is None:
            return None
        
    elif 'release_date_components' in jsonSong:
        components = eval(str(jsonSong['release_date_components']))
        if components is not None and 'year' in components:
            return components['year']
        else:
            return None
    
    date = datetime.strptime(jsonSong['release_date'], util.DATE_FORMAT)
    return date.year


def loadAllArtists():
    files = getFiles()
    allArtists = [loadFile(filename,util.DATA_FOLDER) for filename in files]
    return allArtists


def loadAlbums():
    files = getFiles([],util.ALBUM_FOLDER)
    allAlbums = [loadFile(filename, util.ALBUM_FOLDER) for filename in files]
    return allAlbums

def loadCorpusXMLTree(infile=util.OUTFILE):
    return ET.parse(infile)
        

    

