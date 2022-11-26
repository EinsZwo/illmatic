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





def getFiles(artistNames = []):
    artist_files = []
    for dir_, _, files in os.walk(util.DATA_FOLDER):
 
        for filename in files:
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
        


    
def loadArtist(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    rel_path = util.DATA_FOLDER + "/" + filename
    abs_file_path = os.path.join(script_dir, rel_path)
    
    file = open(abs_file_path)
    artist = json.load(file)
    return artist

def getReleaseDate(jsonSong):
    
    if jsonSong['release_date'] is None:
            return None
    
    date = datetime.strptime(jsonSong['release_date'], util.DATE_FORMAT)
    return date.year


def loadAllArtists():
    files = getFiles()
    allArtists = [loadArtist(filename) for filename in files]
    return allArtists


def loadCorpusXMLTree():
    return ET.parse(util.OUTFILE)
        
    

files = getFiles()
years = []
for file in files:
    artist = loadArtist(file)
    for song in artist['songs']:
        if song['release_date'] is None:
            continue
        
        date = datetime.strptime(song['release_date'], util.DATE_FORMAT)
        years.append(date.year)
        
years_distro = Counter(years)
rounded = {}
ignore_list = []
for key in years_distro.keys():
    if(key < 1950):
        ignore_list.append(key)
    else:
        rounded_year = int(round(key/5.0)*5.0)
        if(key in rounded):
            rounded[rounded_year] += years_distro[key]
        else:
            rounded[rounded_year] = years_distro[key]
    

for key in ignore_list:
    del years_distro[key]
    
plt.bar(years_distro.keys(), years_distro.values())

plt.show()

print(len(years))

plt.bar(rounded.keys(), rounded.values())

plt.show()

