'''
Created on Nov 21, 2022

@author: EinsZwo
'''

from illmatic.song import Song

class Artist:
    
    def __init__(self, jsonArtist):
        self.name = jsonArtist['artist'] #TODO does this work?
        
        
        #TODO add some other reportable features for the artist?
        self.songs = [Song(jsonSong) for jsonSong in jsonArtist['songs']]