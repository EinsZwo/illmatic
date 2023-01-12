'''
Helper class for 
@author: EinsZwo
'''

from illmatic.song import Song

class Artist:
    
    def __init__(self, jsonArtist):
        self.name = jsonArtist['artist']
        
        
        self.songs = [Song(jsonSong) for jsonSong in jsonArtist['songs']]