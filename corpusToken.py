'''
Created on Nov 25, 2022

@author: matth
'''

from illmatic import util

def parseAnnotation(annotatedToken):
    
    split = annotatedToken.split(util.ANNOTATION_DELIMITER)
    
    partOfSpeech = split[-1]
    
    wordform = ""
    lemma = ""
    
    if partOfSpeech == "SPACE":
        wordform = " "
        lemma = " "
    elif partOfSpeech == "" or partOfSpeech == "_":
        wordform = ""
        lemma = ""
        partOfSpeech = ""
    elif len(split)<3:
        wordform = ""
        lemma = ""
        partOfSpeech = ""
    else:
        wordform = split[0]
        lemma = split[1]
    
    return wordform, lemma, partOfSpeech

class CorpusToken():
    
    def __init__(self, annotatedToken):
        wordform, lemma, partOfSpeech = parseAnnotation(annotatedToken)
        self.wordform = wordform
        self.lemma = lemma
        self.partOfSpeech = partOfSpeech
           
           


