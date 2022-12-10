'''
Created on Nov 20, 2022

@author: matth
'''

import re
from illmatic import util
import en_core_web_md
#import en_core_web_trf

nlp = en_core_web_md.load()

POSSIBLE_LABELS = ["verse", "hook", "sample", "vocal", "vocals", "chorus", "intro", "outro", \
                   "guitar solo", "post-chorus", "refrain", "skit", "spoken", "outro skit", "interlude", "closing", "break", \
                   "incomprehensible", "both", "instrumental", "all", "scratches", "pre"]


def possibleGeniusLabels():
    return POSSIBLE_LABELS

def isLabelLine(line):
    return '[' in line

def isExceptionLine(line):
    for label in POSSIBLE_LABELS:
        if '[' + label + ']' in line.lower() or "[-" + label + "-]" in line.lower():
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

def removeSongStructure(line):
    regex = "[Vv]erse[ ]*([0-9]|[I]*)?"
    line = re.sub(regex, "", line)
    regex = "VERSE[ ]*([0-9]|[I]*)?"
    line = re.sub(regex, "", line)
    
    if "hooker" not in line.lower():
        
        
        regex = "[Hh]ook[ ]*[0-9]?"
        line = re.sub(regex, "", line)
    
    line = re.sub("[Cc]horus","",line)
    
    line = re.sub("[Ii]ntro","",line)
    return line

def parseArtistsFromLabel(line,songArtist):
    
    line = line.split("[")
    
    if(len(line) > 1):
        line = line[1]
    else:
        line = line[0]
        
    # if the song
    if(line.lower()=="hook" or line.lower()=="both" or line.lower()=="all"):
        return [songArtist]
        
    line = line.split("]")[0]
        
    regex = '\(?x[0-9]*\)?'
    line = re.sub(regex, "", line)
    
    # clean out things like *sound effect* or *sample*
    regex = "\*.*\*"
    line = re.sub(regex, "", line)
    
    line = removeSongStructure(line)
    
    regex = "\".*\""
    line = re.sub(regex, "", line)
    
    line = line.replace('ft.', '&')
    line = line.replace('featuring.', '&')
    line = line.replace('[', '')
    line = line.replace(']', '')
    line = line.replace('/', ':')
    line = line.replace("-", "")

    splitted = line.split(':')
    artists = splitted[0]
    if(len(splitted) > 1):
        artists = splitted[1]
    
    # handle artists who have oddly formatted names
    artists = artists.replace('Tyler,', 'Tyler')

    
    artists = artists.replace(',', ' &')
    artists = artists.replace('+', ' &')
    artists = artists.replace(' with ', ' & ')
    artists = artists.replace(' and ', ' & ')
    artists = artists.split('&')
    cleaned = []
    
    for artist in artists:
        if not artist.lower().strip() in POSSIBLE_LABELS and len(artist)>0 and 'sample' not in artist.lower():
            artist = artist.replace('(', '')
            artist = artist.replace(')', '')
            cleaned.append(artist.strip())
    
    return cleaned

    #TODO better name
def annotateSong(song):
    # TODO: don't do this for every song?
    # TODO: Choose a better mode?
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
    regex = '[0-9]*Embed[Share]?'
    lyrics = re.sub(regex, "", lyrics)
    lyrics = re.sub("You might also like", "", lyrics)
    lyrics = re.sub("URLCopy", "", lyrics)
    lyrics = re.sub("EmbedCopy", "", lyrics)
    lyrics = lyrics.replace("[?]", util.UNKNOWN_TOKEN)
    lyrics = lyrics.replace("]","]\n") #split the tags so they are each on their own line
    return lyrics

def getLyricsByArtist(rawLyrics, songArtist):
    rawLyrics = cleanRawLyrics(rawLyrics)
    rawLines = [line for line in rawLyrics.split("\n") if line != "\n" and line.strip() != ""]
    annotatedLines = annotateSong("\n".join(rawLines)).split("\n")
    artists = []
    lyrics = []
    lyricsBatch = []
    currentArtist = songArtist
    assert (len(annotatedLines) == len(rawLines))
    for rawLine, annotatedLine in zip(rawLines, annotatedLines):
        
        if (isExceptionLine(rawLine)):
            continue
        
        if (isPerformerLine(rawLine)):
            newPerformers = parseArtistsFromLabel(rawLine,songArtist)

        
            if (len(newPerformers)>0) and ("_".join(newPerformers) != currentArtist):
                if(len(lyricsBatch)>0):
                    artists.append(currentArtist)
                    lyrics.append(lyricsBatch)
                currentArtist = "_".join(newPerformers)
                lyricsBatch = []

        
        else:
            lyricsBatch.append((annotatedLine,rawLine))
    
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




    