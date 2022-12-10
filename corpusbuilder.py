'''
Created on Nov 22, 2022

@author: matth
'''


from illmatic.parser import getLyricsByArtist,removeSongStructure,possibleGeniusLabels,\
    removeGeniusLabels
from illmatic import song, artist
from illmatic import dataloader
from illmatic import util
import xml.etree.ElementTree as ET
from illmatic.dataloader import loadFile
from collections import Counter
import re

def cleanArtistName(artistName):
    return artistName.replace("&", "and")


# TODO this is really stupid
def setArtistName(artistRoot,artistName):
    """
    artistRoot.set(util.ARTIST_HEAD, {util.ARTIST_NAME: artistName})
    """
    artistRoot.set(util.ARTIST_NAME, artistName)


def buildSongXML(song,artistRoot,releaseDate=""):    

    if(len(song['lyrics'].strip())==0): #skip instrumentals, or things that aren't transcribed on genius.com
        return
    
    songRoot = ET.SubElement(artistRoot, util.SONG_ROOT, {util.SONG_NAME: song['title'], \
                                                          util.RAW_SONG_LYRICS: song['lyrics']})

    if not releaseDate:
        releaseDate = dataloader.getReleaseDate(song)
    
    if(releaseDate is not None):
        songRoot.set(util.RELEASE_DATE, str(releaseDate))
    
    artists, lyrics = getLyricsByArtist(song['lyrics'], song['artist'])
    
    for performer, lyricBatch in zip(artists,lyrics):
        verse = ET.SubElement(songRoot, util.VERSE_ROOT, {util.PERFORMER_NAME: performer})
        for annotatedLine,rawLine in lyricBatch:
            ET.SubElement(verse, util.LINE_ELEMENT, {util.ANNOTATED_LINE: annotatedLine, util.RAW_LINE : rawLine})
    

def buildArtistXML(jsonArtist):
    
    artistRoot = ET.Element(util.ARTIST_HEAD)
    for song in jsonArtist['songs']:
        artistName = song['artist']
        artistName = cleanArtistName(artistName)
        buildSongXML(song, artistRoot)

            
    setArtistName(artistRoot,artistName)    
    
    
    return artistRoot
    

def saveCorpusXML(root,filename=util.OUTFILE,verbose=False):
    tree = ET.ElementTree(root)
    ET.indent(tree, "    ")
    if(verbose):
        print(f"Writing to outfile: {filename}...")
    tree.write(filename)
    if(verbose):
        print("Done.")


        

       

# TODO Move and make less bad
def getArtistName(artistHead):
    return artistHead.attrib[util.ARTIST_NAME]
    
            
def getArtist(corpusXML, artistName):
    
    """
    Fetch the existing artist XML node, or create a new one if necessary
    """
    for artist in corpusXML.iter(util.ARTIST_HEAD):
        if getArtistName(artist) == artistName:
            print(f"Found existing artist {artistName}")
            return artist
        
    
    # otherwise, make an element for the artist and return it
    artistRoot = ET.Element(util.ARTIST_HEAD)
    setArtistName(artistRoot,artistName)
    corpusXML.append(artistRoot)
    return artistRoot


def getExistingSongNames(artistRoot):
    songs = [song for song in artistRoot.iter(util.SONG_ROOT)]
    songNames = [song.attrib[util.SONG_NAME] for song in songs]
    return songNames
    
            
def addSupplementalAlbums(writeFile=util.OUTFILE):
    albums = dataloader.loadAlbums()
    corpusRoot = dataloader.loadCorpusXMLTree().getroot()
    for album in albums:
        try:
            artist = album['artist']['name']
            releaseDate = dataloader.getReleaseDate(album)
            print(f"Adding {album['full_title'].encode('utf-8')}...")
            artist = cleanArtistName(artist)
            artistRoot = getArtist(corpusRoot, artist)
            existingSongs = getExistingSongNames(artistRoot)
            for track in album['tracks']:
                song = track['song']
                if song['instrumental'] == True:
                    continue
                
                title = song['title']
                if (title in existingSongs):
                    continue
                else:
                    buildSongXML(song,artistRoot,releaseDate)
        except:
            with open("corpus_status.txt", "a+", encoding="utf-8") as outfile:
                outfile.write("FAILED {artist} - {album['name']}")
    
    saveCorpusXML(corpusRoot, filename=writeFile,verbose=True)
                
def getArtistCounts(corpusRoot=None):
    
    if corpusRoot is None:
        corpusRoot = dataloader.loadCorpusXMLTree().getroot()

    artists = []
    
    for artist in corpusRoot.iter(util.ARTIST_HEAD):
        artists.append(getArtistName(artist))
    
    for song in corpusRoot.iter(util.SONG_ROOT):
        song_artists = []
        for verse in song.iter(util.VERSE_ROOT):
            performers = verse.attrib[util.PERFORMER_NAME].split("_")
            song_artists.extend(performers)
        
        artists.extend(set(song_artists))
    
    artists_count = Counter(artists)
    
    artists = list(reversed(artists_count.most_common()))
    
    with open("artist_names_num_songs.txt", "w+", encoding='utf-8') as outfile:
        for artist in artists:
            outfile.write(f"{artist[0]} : {artists_count[artist[0]]}\n")
    
    return artists_count

    
            
def cleanArtistNamesForErrors():
    corpusRoot = dataloader.loadCorpusXMLTree().getroot()
    
    
    for artist in corpusRoot.iter(util.ARTIST_HEAD):
        song_artist = artist.attrib[util.ARTIST_NAME]
        
        for song in artist.iter(util.SONG_ROOT):
            
            for verse in song.iter(util.VERSE_ROOT):
                new = []
                performers = verse.attrib[util.PERFORMER_NAME].split("_")
                for performer in performers:
                    performer = removeSongStructure(performer).strip()
                    
                    if (performer != "" and performer.lower() not in possibleGeniusLabels()):
                        new.append(performer)
            
                if(len(new) < 1): #fill in gaps we may have created
                    new.append(song_artist)
            
                verse.set(util.PERFORMER_NAME, "_".join(new))
            
    saveCorpusXML(corpusRoot, util.OUTFILE, verbose=True)


def replaceInfrequentPerformers():
    corpusRoot = dataloader.loadCorpusXMLTree().getroot()
    artistCounts = getArtistCounts(corpusRoot)
    
    for artist in corpusRoot.iter(util.ARTIST_HEAD):
        song_artist = artist.attrib[util.ARTIST_NAME]
        
        for song in artist.iter(util.SONG_ROOT):
            
            for verse in song.iter(util.VERSE_ROOT):
                new_performers = []
                performers = verse.attrib[util.PERFORMER_NAME].split("_")
                
                for performer in performers:
                    if (artistCounts[performer]>1):
                        new_performers.append(performer)
                        
                    else:
                        new_performers.append(util.UNKNOWN_PERFORMER)
                        
                new_performers = list(set(new_performers))
                if(len(new_performers)==1 and new_performers[0] == util.UNKNOWN_PERFORMER) or len(new_performers)<1:
                    new_performers = [song_artist]
            
                verse.set(util.PERFORMER_NAME, "_".join(new_performers))
                
    saveCorpusXML(corpusRoot, util.OUTFILE, verbose=True)
    

def checkDuplicateSongs(artistNode):
    songTitles = [song.attrib[util.SONG_NAME] for song in artistNode.iter(util.SONG_ROOT)]
    
    songLower = [title.lower().strip() for title in songTitles]
    
    toRemove = []
    
    for title in songTitles:
        tempTitle=title.lower()
        if "remix" in tempTitle or "reprise" in tempTitle:
            
            regexes = ['[(]?reprise[)]?','[(]?remix[)]?']
            
            for regex in regexes:
                tempTitle = re.sub(regex, "", tempTitle)
                
            tempTitle=tempTitle.strip()
            
            if tempTitle in songLower:
                toRemove.append(title)
                print(title)
                
    
    
    for song in artistNode.findall(util.SONG_ROOT):
        if song.attrib[util.SONG_NAME] in toRemove:
            artistNode.remove(song)
            
                


def cleanUpDuplicateSongs():
    corpusRoot = dataloader.loadCorpusXMLTree().getroot()
    for artist in corpusRoot.iter(util.ARTIST_HEAD):
        checkDuplicateSongs(artist)
        
    saveCorpusXML(corpusRoot, util.OUTFILE, verbose=True)


def stripName(name):
    name = name.lower()
    regex = "[^a-z ]" # strip out punctuation, non-spaces
    name = re.sub(regex, "", name)
    
    if name.startswith("the "):
        name = name[4:]
        
    
    return name
    
    
    
def normalizeArtistNames(corpusRoot=None):
    
    if corpusRoot is None:
        corpusRoot = dataloader.loadCorpusXMLTree().getroot()
        
    goldStandardNames = [artist.attrib[util.ARTIST_NAME] for artist in corpusRoot.iter(util.ARTIST_HEAD)]
    
    goldStandardNormalized = [stripName(name) for name in goldStandardNames]
    
    goldStandardNormalized = dict(zip(goldStandardNormalized,goldStandardNames))

    
    
    for verse in corpusRoot.iter(util.VERSE_ROOT):
        new_performers = []
        performers = verse.attrib[util.PERFORMER_NAME].split("_")
        
        for performer in performers:
            stripped = stripName(performer)
            if stripped in goldStandardNormalized:
                new_performers.append(goldStandardNormalized[stripped]) #replace with Genius versions where possible
            else:
                new_performers.append(performer)
                
        
        verse.set(util.PERFORMER_NAME, "_".join(new_performers))
    
    saveCorpusXML(corpusRoot, filename=util.OUTFILE, verbose=True)
        

                

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
        try:
            string = f"Building tree for {artist['name'].encode('utf-8')}..."
            print(string)
            root.append(buildArtistXML(artist))
            saveCorpusXML(root)

        except:
                print(f"FAILED {artist['name'].encode('utf-8')}...")
                with open("corpus_status.txt", "a+", encoding="utf-8") as outfile:
                    outfile.write(f"FAILED {artist['name'].encode('utf-8')}")
    
    
    saveCorpusXML(root,util.OUTFILE,verbose=True)
    print("Adding supplemental albums...")
    addSupplementalAlbums()
    print("Performing cleanup...")
    cleanUpDuplicateSongs()
    normalizeArtistNames()
    cleanArtistNamesForErrors()
    replaceInfrequentPerformers()
    print("Corpus built!")

    



