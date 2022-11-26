'''
Created on Nov 20, 2022

@author: matth
'''

import re
import spacy
from illmatic import dataloader
nlp = spacy.load("en_core_web_sm")

POSSIBLE_LABELS = ["verse", "hook", "sample", "vocal", "vocals", "chorus", "intro", "outro", \
                   "guitar solo", "post-chorus", "refrain", "skit", "spoken", "outro skit", "interlude", "closing", "break", \
                   "incomprehensible", ]


def isLabelLine(line):
    return '[' in line

def isExceptionLine(line):
    for label in POSSIBLE_LABELS:
        if '[' + label + ']' in line.lower():
            return True
    
    #todo: handle skits with UNK? or remove
    # todo: clean up
    
    for label in ["Verse", "Bridge", "Chorus", "Hook", "Skit"]:
        pattern = '\[' + label + '[ ]?[0-9]*]'
        if len(re.findall(pattern, line)) > 0:
            return True
    
    return '[Produce' in line \
        or '[Sample' in line

def isPerformerLine(line):
    return isLabelLine(line) and not isExceptionLine(line)

def parseArtistsFromLabel(line):
    
    #TODO handle things that are just [Hook] so it's the artist's name
    line = line.split("[")
    
    if(len(line) > 1):
        line = line[1]
    else:
        line = line[0]
        
    regex = '\(?x[0-9]*\)?'
    line = re.sub(regex, "", line)
    
    line = line.replace('[', '')
    line = line.replace(']', '')
    line = line.replace('/', ':')

    splitted = line.split(':')
    artists = splitted[0]
    if(len(splitted) > 1):
        artists = splitted[1]
    
    artists = artists.replace(',', ' &')
    artists = artists.replace('+', ' &')
    artists = artists.split('&')
    cleaned = []
    
    for artist in artists:
        if not artist.lower().strip() in POSSIBLE_LABELS and len(artist)>0: 
            artist = artist.replace('(', '')
            artist = artist.replace(')', '')
            cleaned.append(artist.strip())
    
    return cleaned

    #TODO better name
def annotateSong(song):
    # TODO: don't do this for every song?
    # TODO: Choose a better mode?
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(song)
    joined = ' '.join([f"{token.text}_{token.lemma_}_{token.pos_}" for token in doc])

    #TODO this is probably wrong since we're ending up with different lengths of stuff
    split = joined.split("\n")
    trimmed = [line.strip() for line in split if line.strip() != "_" and line.strip() != ""]
    joined = "\n".join(trimmed)
    return joined


def cleanRawLyrics(lyrics):
    """
    Cleans some errant HTML before processing
    """
    regex = '[0-9]*Embed'
    lyrics = re.sub(regex, "", lyrics)
    return lyrics

def getLyricsByArtist(rawLyrics, songArtist):
    rawLyrics = cleanRawLyrics(rawLyrics)
    annotatedLines = annotateSong(rawLyrics).split("\n")
    rawLines = [line for line in rawLyrics.split("\n") if line != "\n" and line != ""]
    artists = []
    lyrics = []
    lyricsBatch = []
    currentArtist = songArtist
    assert (len(annotatedLines) == len(rawLines))
    for rawLine, annotatedLine in zip(rawLines, annotatedLines):
        
        if (isExceptionLine(rawLine)):
            continue
        
        if (isPerformerLine(rawLine)):
            newPerformers = parseArtistsFromLabel(rawLine)
            if (len(newPerformers)>0) and ("_".join(newPerformers) != currentArtist):
                if(len(lyricsBatch)>0):
                    artists.append(currentArtist)
                    lyrics.append(lyricsBatch)
                currentArtist = "_".join(newPerformers)
                lyricsBatch = []
        
        else:
            lyricsBatch.append(annotatedLine)
    
    if(len(lyricsBatch) > 0):
        artists.append(currentArtist)
        lyrics.append(lyricsBatch)
    
    return (artists, lyrics)


def removeGeniusLabels(rawLyrics):
    """
    Returns only the text from the raw lyrics that are spoken--
        removes all the labels used in Genius to denote song structure, performing artists, etc.
    """
    rawLyrics = cleanRawLyrics(rawLyrics)
    lines = rawLyrics.split("\n")
    cleanedLyrics  = [line for line in lines if ('[' not in line and ']' not in line)]
    return "\n".join(cleanedLyrics)


    
def getLyricsByArtistDEBUG(rawLyrics, songArtist, songTitle):
    rawLyrics = cleanRawLyrics(rawLyrics)
    annotatedLines = annotateSong(rawLyrics).split("\n")
    rawLines = [line for line in rawLyrics.split("\n") if line != "\n" and line != ""]
    artists = []
    lyrics = []
    lyricsBatch = []
    currentArtist = songArtist
    if (len(annotatedLines) != len(rawLines)):
        print(f"Failed: {songTitle}")
        with open("DEBUG.txt", "a+") as debugFile:
            debugFile.write(f"{songTitle}-------------------------\n")
            debugFile.write("\n".join(rawLines))
            debugFile.write("\n".join(annotatedLines))
        print()
        
    for rawLine, annotatedLine in zip(rawLines, annotatedLines):
        
        if (isExceptionLine(rawLine)):
            continue
        
        if (isPerformerLine(rawLine)):
            newPerformers = parseArtistsFromLabel(rawLine)
            if (len(newPerformers)>0) and ("_".join(newPerformers) != currentArtist):
                if(len(lyricsBatch)>0):
                    artists.append(currentArtist)
                    lyrics.append(lyricsBatch)
                currentArtist = "_".join(newPerformers)
                lyricsBatch = []
        
        else:
            lyricsBatch.append(annotatedLine)
    
    if(len(lyricsBatch) > 0):
        artists.append(currentArtist)
        lyrics.append(lyricsBatch)
    
    return (artists, lyrics)



"""
song = lyrics[0]
doc = nlp(song)
for token in doc:
    print(token.text, token.lemma_, token.pos_)


for song in songs:

    lines = song.split("\n")
    for line in lines:
        if isLabelLine(line):
            print(line)
            if(isPerformerLine(line)):
                artists = parseArtistsFromLabel(line)
                if(len(artists) > 0):
                    print("_".join(artists))   
"""

