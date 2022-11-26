'''
Created on Nov 23, 2022

@author: matth
'''


from illmatic import dataloader, util, parser
from illmatic.corpusToken import CorpusToken
from collections import Counter
import nltk



def commonVerbs():
    
    return ["be", "get", "know", "come", "make", "go", "do", "gon", "give", "see", "take", "say", "ai", "wanna", "have", "let", "'re" \
            "'m", "want"]


def countPartOfSpeech(startYear,endYear,corpusTree,partOfSpeech):
    texts = []
    verbs = []
    if not corpusTree:
        corpusTree = dataloader.loadCorpusXMLTree()
    
    root = corpusTree.getroot()
    for song in root.iter(util.SONG_ROOT):
        if not util.RELEASE_DATE in song.attrib:
            continue
        
        year = int(song.attrib[util.RELEASE_DATE])
        if year>=startYear and year<=endYear:
            for verse in song.iter(util.VERSE_ROOT):
                for line in verse.iter(util.LINE_ELEMENT):
                    texts.append(line.attrib[util.LINE])
    
    texts = set(texts)
    for line in texts:
        split = line.split(" ")
        tokens = [CorpusToken(token) for token in split]
        verbs.extend([tok.lemma for tok in tokens if tok.partOfSpeech == partOfSpeech])
        
    
    counter = Counter(verbs)
    
    return counter


def countProperNouns(startYear,endYear,corpusTree):
    texts = []
    propNouns = []
    if not corpusTree:
        corpusTree = dataloader.loadCorpusXMLTree()
    
    root = corpusTree.getroot()
    for song in root.iter(util.SONG_ROOT):
        if not util.RELEASE_DATE in song.attrib:
            continue
        
        year = int(song.attrib[util.RELEASE_DATE])
        if year>=startYear and year<=endYear:
            for verse in song.iter(util.VERSE_ROOT):
                for line in verse.iter(util.LINE_ELEMENT):
                    texts.append(line.attrib[util.LINE])
                    
    texts = set(texts)                
    for line in texts:
        split = line.split(" ")
        currNoun = []
        tokens = [CorpusToken(tok) for tok in split]
        
        #following a BIO-type approach here, assuming proper nouns together are probably not just juxtaposed
        for token in tokens:
            if token.partOfSpeech != "PROPN" and len(currNoun) > 0:
                propNoun = " ".join([noun.wordform for noun in currNoun])
        
                propNouns.append(propNoun)
                currNoun = []
                
            elif token.partOfSpeech == "PROPN":
                currNoun.append(token)
                
        
        if len(currNoun) > 0:
                propNoun = " ".join([noun.wordform for noun in currNoun])
                propNouns.append(propNoun)
    
    return Counter(propNouns)



    


def countPartOfSpeechByYear(partOfSpeech):
    corpusTree = dataloader.loadCorpusXMLTree()
    common = commonVerbs()
    for year in range(1980,2020):
        partOfSpeechForYear = []
        if partOfSpeech == "PROPN":
            partOfSpeechForYear = countProperNouns(year, year, corpusTree)
        else:
            partOfSpeechForYear = countPartOfSpeech(year,year,corpusTree, partOfSpeech)
        
        
        top = [item for item in partOfSpeechForYear.most_common(50) if item[0] not in common]
        print(f" Year: {year}-------------------")
        for item in top:
            print(f"    {item}")
            


countPartOfSpeechByYear("PROPN")



"""
corpusTree = dataloader.loadCorpusXMLTree()

root = corpusTree.getroot()

whole_corpus = ""

# basic collocation search?
for song in root.iter(util.SONG_ROOT):
    lyrics = parser.removeGeniusLabels(song.attrib[util.RAW_SONG_LYRICS])
    whole_corpus += lyrics
"""
"""
print("Loading raw text file...")
lyrics = ""
with open(util.RAW_LYRICS_FILE, "r", encoding="utf-8") as rawText:
    lyrics = rawText.read()

print("Done.")
"""

"""
tokens = nltk.word_tokenize(whole_corpus)
text = nltk.text.Text(tokens)
print(text.collocation_list())

text.concordance("savage")

text.concordance("Drake")
"""


"""
Sketch: put together some stuff where we iterate over all the songs, can search on lemma or wordform, 
can fetch concordences, etc.
"""


"""
lines = [len(line.split()) for line in lyrics.split("\n")]

print(max(lines))

from transformers import GPT2LMHeadModel, GPT2TokenizerFast

device = "cuda"
model_id = "gpt2-medium"
model = GPT2LMHeadModel.from_pretrained(model_id).to(device)
tokenizer = GPT2TokenizerFast.from_pretrained(model_id)




encodings = tokenizer(lyrics[100000:200000], return_tensors="pt", max_length=512, truncation=True)

import torch
from tqdm import tqdm
import gc

max_length = model.config.n_positions
stride = 128
seq_len = encodings.input_ids.size(1)

nlls = []
prev_end_loc = 0
for begin_loc in tqdm(range(0, seq_len, stride)):
    end_loc = min(begin_loc + max_length, seq_len)
    trg_len = end_loc - prev_end_loc  # may be different from stride on last loop
    input_ids = encodings.input_ids[:, begin_loc:end_loc].to(device)
    target_ids = input_ids.clone()
    target_ids[:, :-trg_len] = -100
    

    with torch.no_grad():
        outputs = model(input_ids, labels=target_ids)

        # loss is calculated using CrossEntropyLoss which averages over input tokens.
        # Multiply it with trg_len to get the summation instead of average.
        # We will take average over all the tokens to get the true average
        # in the last step of this example.
        neg_log_likelihood = outputs.loss * trg_len

    nlls.append(neg_log_likelihood)

    prev_end_loc = end_loc
    if end_loc == seq_len:
        break

ppl = torch.exp(torch.stack(nlls).sum() / end_loc)


print(ppl)
"""
