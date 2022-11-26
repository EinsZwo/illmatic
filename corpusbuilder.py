'''
Created on Nov 22, 2022

@author: matth
'''


from illmatic.parser import getLyricsByArtist,getLyricsByArtistDEBUG
from illmatic import song
from illmatic import dataloader
from illmatic import util
import xml.etree.ElementTree as ET
from illmatic.dataloader import loadArtist




def cleanArtistName(artistName):
    return artistName.replace("&", "and")

def buildArtistXML(jsonArtist):
    
    artistRoot = ET.Element(util.ARTIST_HEAD)
    for song in jsonArtist['songs']:
        artistName = song['artist']
        artistName = cleanArtistName(artistName)
        songRoot = ET.SubElement(artistRoot, util.SONG_ROOT, {util.SONG_NAME: song['title'], \
                                                              util.RAW_SONG_LYRICS: song['lyrics']})
        
        
        releaseDate = dataloader.getReleaseDate(song)
        if(releaseDate is not None):
            songRoot.set(util.RELEASE_DATE, str(releaseDate))
        
        if(len(song['lyrics'].strip())==0): #skip instrumentals, or things that aren't transcribed on genius.com
            continue
        
        artists, lyrics = getLyricsByArtist(song['lyrics'], song['artist'])
        
        for performer, lyricBatch in zip(artists,lyrics):
            verse = ET.SubElement(songRoot, util.VERSE_ROOT, {util.PERFORMER_NAME: performer})
            for line in lyricBatch:
                ET.SubElement(verse, util.LINE_ELEMENT, {util.LINE: line})
        
            
        ## TODO: Album is something you'd have to fetch via Genius
    
        
    artistRoot.set(util.ARTIST_HEAD, {util.ARTIST_NAME: artistName})
    
    return artistRoot
    

def buildCorpus():
    print("Building ILLMATIC corpus...")
    print()
    print()
    print("Loading artist JSON...")
    artists = dataloader.loadAllArtists()
    print("Done.")
    print()
    print()
    print("Building XML for each artist...")
    print()
    print()
    root = ET.Element(util.CORPUS_ROOT)
    
    for artist in artists:
        string = f"Building tree for {artist['name'].encode('utf-8')}..."
        print(string)
        root.append(buildArtistXML(artist))
        
    tree = ET.ElementTree(root)
    ET.indent(tree, "    ")
    print(f"Writing to outfile: {util.OUTFILE}...")
    tree.write(util.OUTFILE)
    print("Done.")
       


#buildCorpus()

def checkCorpusErrors():

    artists = dataloader.loadAllArtists()
    
    artistNames = ["The Roots","The Sequence", "Three 6 Mafia", "Too Short"]
    artists = [loadArtist(artName + ".json") for artName in artistNames]
    for artist in artists:
        print(f"Building tree for {artist['name']}...".encode("utf-8"))
        for song in artist['songs']:
            
            if(len(song['lyrics'].strip())==0): #skip instrumentals, or things that aren't transcribed on genius.com
                continue
            
            getLyricsByArtistDEBUG(song['lyrics'], song['artist'], song['title'])
            
buildCorpus()

