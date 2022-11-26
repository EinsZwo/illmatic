'''
Created on Nov 21, 2022

@author: matth
'''

from datetime import datetime
from illmatic.parser import getLyricsByArtist
DATE_FORMAT = '%Y-%m-%d' #todo this is messy



class Song:
    
    def __init__(self, jsonSong):
        self.artistName = jsonSong['artist']
        self.rawLyrics = jsonSong['lyrics']
        
        date = datetime.strptime(jsonSong['release_date'], DATE_FORMAT)
        self.releaseYear = date.year
        
        self.lyricsByArtist = getLyricsByArtist(self.rawLyrics, self.artistName)
        
