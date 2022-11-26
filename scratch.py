'''
Created on Sept 11, 2021

@author: EinsZwo
'''


# first: read in some data to play around with


import spacy
from spacy import displacy
from collections import Counter
import en_core_web_trf
import os
nlp = en_core_web_trf.load()

import json
from os.path import exists
import nltk
import re
from nltk.chunk import conlltags2tree, tree2conlltags
from pprint import pprint
import collections

RAP_ARTIST_LIST = ["Black Star", "Common", "Common Market", "Da Lench Mob", "Dead Prez", "Rage Against the Machine", "Ice Cube", "Killer Mike", "MF Doom", "Mos Def", "Nas", "Public Enemy", "Talib Kweli", "Scarface"]

def addEndOfSentence(lyrics):
    lines = lyrics.splitlines()
    return ". ".join(lines)

def nltk_preprocess(lyrics):
    #try a rudimentary EOS-type schema
    sentences = nltk.sent_tokenize(lyrics.lower())
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences

def nltk_getTree(tagged_words):
    grammar = 'NP: {<DT>?<JJ>*<NN>}'
    cp = nltk.RegexpParser(grammar)
    return cp.parse(tagged_words)

def get_IOB(lyrics):
    pre_proc = nltk_preprocess(lyrics)
    for sentence in pre_proc:
        tree = nltk_getTree(sentence)
        iob_tagged = tree2conlltags(tree)
        yield iob_tagged
        
def countableNamedEntity(ne_type):
    return True

def genius_stop_words():
    return ['URLCopyEmbedCopy', 'EmbedShare', '(', ')', '-interlude-']


def strip_genius_labels(lyrics):
    pattern = r'\[.*?\]'
    stripped = re.sub(pattern,"", lyrics)
    
    stop_words = genius_stop_words()
    for word in stop_words:
        stripped = stripped.replace(word, "")
        
    return stripped


def get_genius_tags(lyrics):
    pattern = r'\[.*?\]'
    stripped = re.findall(pattern, lyrics)
    
    return stripped




"""
for rap_artist in artist_list:
    filename = rap_artist + ".json"
    if not exists(filename):
        continue

    script_dir = os.path.dirname(os.path.abspath(__file__))
    rel_path = "rapdata/" + filename
    abs_file_path = os.path.join(script_dir, rel_path)
    
    file = open(abs_file_path)
    
    files = 0
    artist = json.load(file)
    for song in artist['songs']:
        print(song['title'])
        print(song['artist'])
        print(song['release_date'])
        
        print(get_genius_tags(song['lyrics']))
        
        #lyrics = strip_genius_labels(song['lyrics'])
        #print(lyrics)
        #pre_proc = nltk_preprocess(lyrics)
            #for sentence in pre_proc:
            #print(nltk_getTree(sentence))
            #nltk_getTree(sentence).draw()
        #print(pre_proc)
        
        #for x in get_IOB(lyrics):
        #    pprint(x)
        
        #usually more efficient to do nlp.pipe and buffer in batches, than as one-by-one
        #doc = nlp(lyrics)
        
        #for entity in doc.ents:
        #    if(countableNamedEntity(entity.label)):
                
        #        if entity.text in ne_dict:
        #            ne_dict[entity.text] += 1
        #        else:
        #            ne_dict[entity.text] = 1
                
        #break
        #pprint([(entity.text, entity.label_) for entity in doc.ents])

    
    file.close()
   

sorted_x = dict(sorted(ne_dict.items(), key=lambda item: item[1], reverse=True))

print(sorted_x)
"""

