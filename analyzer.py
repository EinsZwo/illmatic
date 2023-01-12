'''

@author: EinsZwo
'''


from illmatic import dataloader, util
from illmatic.corpusToken import CorpusToken
from illmatic.corpusbuilder import stripName
from collections import Counter
from transformers import GPT2LMHeadModel, GPT2TokenizerFast
import torch
from tqdm import tqdm
from illmatic.dataloader import loadCorpusXMLTree
import random
import matplotlib.pyplot as plt

def commonVerbs():
    """
    stop word-like list of common lemmas to ignore when analyzing verbs over time
    """
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
                    texts.append(line.attrib[util.ANNOTATED_LINE])
    
    texts = set(texts)
    for line in texts:
        split = line.split(" ")
        tokens = [CorpusToken(token) for token in split]
        verbs.extend([tok.lemma for tok in tokens if tok.partOfSpeech == partOfSpeech])
        
    
    counter = Counter(verbs)
    
    return counter

    


def countPartOfSpeechByYear(partOfSpeech):
    corpusTree = dataloader.loadCorpusXMLTree()
    common = commonVerbs()
    for year in range(1980,2020):
        partOfSpeechForYear = []

        partOfSpeechForYear = countPartOfSpeech(year,year,corpusTree, partOfSpeech)
        
        
        top = [item for item in partOfSpeechForYear.most_common(50) if item[0] not in common]
        print(f" Year: {year}-------------------")
        for item in top:
            print(f"    {item}")
                  
        
        



def calcPerplexity(tokenizer, model,device,lyrics):
    # https://huggingface.co/docs/transformers/perplexity
    # sliding window strategy to evaluate perplexity over a set
    encodings = tokenizer(lyrics, return_tensors="pt")
    max_length = model.config.n_positions
    stride = 128
    seq_len = encodings.input_ids.size(1)
    
    lyrics = lyrics.replace(util.UNKNOWN_TOKEN, "") #this might not be the best approach?
    
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
    return ppl.item()


def setupPerplexity():
    """
    Sets up perplexity parameters for experimentation
    """
    device = "cuda"
    model_id = "gpt2-medium"
    model = GPT2LMHeadModel.from_pretrained(model_id).to(device)
    tokenizer = GPT2TokenizerFast.from_pretrained(model_id)
    
    
    return device, model, tokenizer


    

def getSongLyricsForArtist(artistName,corpusRoot=None,getTokens=False):
    
    if corpusRoot is None:
        corpusRoot = dataloader.loadCorpusXMLTree().getroot()
        
    simpleName = stripName(artistName)
    
    all_songs = []
    for song in corpusRoot.iter(util.SONG_ROOT):
        song_verses = []
        for verse in song.iter(util.VERSE_ROOT):
            performers = verse.get(util.PERFORMER_NAME).split("_")
            
            for performer in performers:
                if stripName(performer)==simpleName:
                    if(getTokens):
                        lines = [line.get(util.ANNOTATED_LINE).split(" ") for line in verse.iter(util.LINE_ELEMENT)]
                        tokens = []
                        for line in lines:
                            tokens.append([CorpusToken(token) for token in line])
                        song_verses.extend(tokens)
                    else:
                        song_verses.extend([line.get(util.RAW_LINE) for line in verse.iter(util.LINE_ELEMENT)])
                    
        if(len(song_verses)>0):
            all_songs.append(song_verses)
            
    return all_songs


def getSongLyricsForYearRange(yearStart,yearEnd,corpusRoot=None,getTokens=False):
    
    if corpusRoot is None:
        corpusRoot = dataloader.loadCorpusXMLTree().getroot()
            
    all_songs = []
    for song in corpusRoot.iter(util.SONG_ROOT):
        song_verses = []
        year = song.get(util.RELEASE_DATE)
        if song.get(util.RELEASE_DATE) is None or year == "":
            continue
        
        year = int(year)
        
        if(year>=yearStart and year<=yearEnd): #should be refactored
            if(getTokens):
                lines = [line.get(util.ANNOTATED_LINE).split(" ") for line in song.iter(util.LINE_ELEMENT)]
                tokens = []
                for line in lines:
                    tokens.append([CorpusToken(token) for token in line])
                song_verses.extend(tokens)
            else:
                song_verses.extend([line.get(util.RAW_LINE) for line in song.iter(util.LINE_ELEMENT)])
                    
        if(len(song_verses)>0):
            all_songs.append(song_verses)
            
    return all_songs
    
       
def perplexityForArtist(artist_list=[]):
    corpusRoot = loadCorpusXMLTree().getroot()
    
    if(len(artist_list)==0):
        artist_list = [artist.get(util.ARTIST_NAME) for artist in corpusRoot.iter(util.ARTIST_HEAD)]
    
    
    existing = []
    with open("perplexity.txt", "r",encoding='ansi') as infile:
        existing = (line.split(",") for line in infile.readlines())
        
    existing = [line[0] for line in existing if len(line)>0]
    
    device, model, tokenizer = setupPerplexity()
    
    perplexity = {}
    
    for artist in artist_list:
        
        
        if artist in existing:
            print(f"Skipping {artist} (already processed)...")
            continue
        
        try:
            artist_perplexity = []
            lyrics = getSongLyricsForArtist(artist, corpusRoot)
            
            for i in range(0,3):
                random.shuffle(lyrics)
                lines = ""
                
                for song in lyrics:
                    lines += "\n".join(song) + "\n\n"
                    
                
                    
                artist_perplexity.append(calcPerplexity(tokenizer,model,device,lines))
            
            
            perplexity = sum(artist_perplexity) / len(artist_perplexity)
            
            with open("perplexity.txt", "a+",encoding='utf-8') as outfile:
                outfile.write(f"{artist},{perplexity},{artist_perplexity[0]},{artist_perplexity[1]},{artist_perplexity[2]},\n")
                
            
            
        except:
            with open("perplexity_errors.txt","a+",encoding='utf-8') as outfile:
                outfile.write(f"Failed artist: {artist}")
            


def findVerbsForYear():
    corpusRoot = loadCorpusXMLTree().getroot()
    common_verbs = commonVerbs()
    for year in range(1979,2022):
        verbs = []
        allVerbs = []
        songs = getSongLyricsForYearRange(year, year, corpusRoot, getTokens=True)
        for song in songs:
            for line in song:
                verbs.extend([token.lemma for token in line if token.partOfSpeech == "VERB"])

        counter = Counter(verbs)
        
        yearVerbs = counter.most_common(50)
        
        with open("verbs_by_year.txt","a+") as outfile:
            outfile.write(f"{year} (Total verbs: {len(verbs)})\n")
            for verb in yearVerbs:
                if verb[0] not in common_verbs:
                    outfile.write(f"    {verb} ({round(verb[1]/len(verbs),4)})\n")
            outfile.write("\n\n\n")
            
    for yearBatch in range(1980,2025,5):
        verbs = []
        songs = getSongLyricsForYearRange(yearBatch, yearBatch+4, corpusRoot, getTokens=True)
        for song in songs:
            for line in song:
                verbs.extend([token.lemma for token in line if token.partOfSpeech == "VERB"])
        
        
        counter = Counter(verbs)
        yearVerbs = counter.most_common(50)
        with open("verbs_by_year.txt","a+") as outfile:
            outfile.write(f"{yearBatch}-{yearBatch+4} (Total verbs: {len(verbs)})\n")
            for verb in yearVerbs:
                if verb[0] not in common_verbs:
                    outfile.write(f"    {verb} ({round(verb[1]/len(verbs),4)})\n")
            outfile.write("\n\n\n")
            
def graphVerbsForYear(wordlist=[]):
    """
    Generates a graph of the percentage of verbs in wordlist for each year in the corpus
    """
    years = {}
    corpusRoot = loadCorpusXMLTree().getroot()
    common_verbs = commonVerbs()
    
    
    for year in range(1979,2022):
        verbs = []
        allVerbs = []
        songs = getSongLyricsForYearRange(year, year, corpusRoot, getTokens=True)
        for song in songs:
            for line in song:
                verbs.extend([token.lemma for token in line if token.partOfSpeech == "VERB"])

        counter = Counter(verbs)
        total = sum(counter.values())
        
        wordDict = {}
        for word in wordlist:
            wordDict[word] = (counter.get(word,0) / total) * 100
        
        years[year] = wordDict
        
    
    
    for word in wordlist:
        print(word + "\n")
        wordPercentage = []
        for year in years:
            wordPercentage.append((year,years[year][word]))
        
        # graph
        plt.scatter(*zip(*wordPercentage))
        plt.title(f"\"{word}\" as a percentage of all verbs over time ")
        plt.ylabel("Percentage of all verbs")
        plt.xlabel("Year")
        plt.show()

def findVerbsForYearsUnique():
    corpusRoot = loadCorpusXMLTree().getroot()
    common_verbs = commonVerbs()
    yearBatches = {}
    
    final = {}
    for yearBatch in range(1980,2025,10):
        verbs = []
        songs = getSongLyricsForYearRange(yearBatch, yearBatch+4, corpusRoot, getTokens=True)
        for song in songs:
            for line in song:
                verbs.extend([token.lemma for token in line if token.partOfSpeech == "VERB"])
        
        
        counter = Counter(verbs)
        yearVerbs = counter.most_common(75)
        yearVerbs = [verb[0] for verb in yearVerbs if verb[0] not in common_verbs]
        
        yearBatches[yearBatch] = yearVerbs
        
    # get only verbs which are unique to the list
    for yearBatch in yearBatches:
        verbs = yearBatches[yearBatch]
        for comparison in yearBatches:
            if yearBatch == comparison:
                continue
            
            verbs = [verb for verb in verbs if verb not in yearBatches[comparison]]
            
        final[yearBatch] = verbs  
         
    with open("verbs_UNIQUE_decade.txt","a+") as outfile:
        for yearBatch in final:
            outfile.write(f"{yearBatch}-{yearBatch+9}\n")
            for verb in final[yearBatch]:
                outfile.write(f"    {verb}\n")
            outfile.write("\n\n\n")

def findCollocations(nodeType,attribute,criteria,lemma,partOfSpeech,corpusRoot=None):
    collocations = []
    
    if corpusRoot is None:
        corpusRoot = loadCorpusXMLTree().getroot()

    for node in corpusRoot.iter(nodeType):
        nodeAttrib = node.get(attribute)
        if nodeAttrib is None:
            continue
        
        meetsCriteria = True
        for criterion in criteria:
            toEval = str(nodeAttrib)+criterion
            if not eval(toEval):
                meetsCriteria = False
                
        if not meetsCriteria:
            continue
        
        for line in node.iter(util.LINE_ELEMENT):
            tokens = [CorpusToken(token) for token in line.get(util.ANNOTATED_LINE).split(" ")]
            for token in tokens:
                if token.lemma==lemma and token.partOfSpeech==partOfSpeech:
                    collocations.append(line.get(util.RAW_LINE))
                    
    
    return collocations


def formatSearchResult(verse,song,artist):
    performer = verse.get(util.PERFORMER_NAME)
    songTitle = song.get(util.SONG_NAME)
    artistName = artist.get(util.ARTIST_NAME)
    
    return f"{songTitle} by {artistName} (Performed by {performer})"

def searchText(textToFind,ignoreCase=True,corpusRoot=None):
    if(ignoreCase):
        textToFind = textToFind.lower()
        
    songLines = {}
    
    if corpusRoot is None:
        corpusRoot = loadCorpusXMLTree().getroot()
    
    parent_map = {c:p for p in corpusRoot.iter() for c in p}
    
    for line in corpusRoot.findall(f".//{util.LINE_ELEMENT}[@{util.RAW_LINE}]"):
        searchText = line.get(util.RAW_LINE)
        if(ignoreCase):
            searchText = searchText.lower()
        if textToFind in searchText:
            verse = parent_map[line]
            song = parent_map[verse]
            artist = parent_map[song]
            
            index = formatSearchResult(verse, song, artist)
            textToAdd = f"    {line.get(util.RAW_LINE)}"
            
            if index in songLines:
                songLines[index] += "\n" + textToAdd
            else:
                songLines[index] = textToAdd
                
                
    for index in songLines:
        print((index +"\n").encode('utf-8'))
        print(songLines[index] + "\n")
        
        
def vocabularyForArtist(artist_list=[],sample_size=5000,filename="vocab.txt"):
    """
    Samples an artist's vocabulary size, by taking sample_size tokens from their shuffled discography. Average of 3 runs. Saves to filename
    """
    
    corpusRoot = loadCorpusXMLTree().getroot()
    
    
    
    if(len(artist_list)==0):
        artist_list = [artist.get(util.ARTIST_NAME) for artist in corpusRoot.iter(util.ARTIST_HEAD)]
   
                
    
    for artist in artist_list:
        
        vocab = []
        lyrics = getSongLyricsForArtist(artist, corpusRoot,getTokens=True)
        
        for i in range(0,3):
            random.shuffle(lyrics)
            tokens = [tok for song in lyrics for line in song for tok in line]
            tokens = [tok.lemma + "_" + tok.partOfSpeech for tok in tokens]
            
            if (len(tokens)>sample_size):
                tokens = tokens[:sample_size]
                
            
            vocab.append(len(set(tokens)))
        
        avgVocab = sum(vocab)/3
        
        with open(filename, "a+",encoding='utf-8') as outfile:
            outfile.write(f"{artist},{round(avgVocab,2)},{vocab[0]},{vocab[1]},{vocab[2]}\n")

def tokensForArtist(artist_list=[]):
    corpusRoot = loadCorpusXMLTree().getroot()
    
    """
    Counts the tokens for each artist
    """
    
    
    if(len(artist_list)==0):
        artist_list = [artist.get(util.ARTIST_NAME) for artist in corpusRoot.iter(util.ARTIST_HEAD)]
   
    tok_len = []
    tok_artist = []
    
    for artist in artist_list:
        
        vocab = []
        lyrics = getSongLyricsForArtist(artist, corpusRoot,getTokens=True)
        tokens = [tok for song in lyrics for line in song for tok in line]
        tok_len.append(len(tokens))
        tok_artist.append((artist,len(tokens)))              
        
    print(f"Tokens: {sum(tok_len)}")
    print(f"Number of song artists: {len(tok_len)}")
    print(tok_artist)


def yearDistributionXML():
    """
    Generates a plot for distribution of songs per release year
    """
    corpus = loadCorpusXMLTree().getroot()
    years = []
    
    songs = [song for song in corpus.iter(util.SONG_ROOT)]
    print(len(songs))
    
    artists = [song for song in corpus.iter(util.ARTIST_HEAD)]
    print(len(artists))
    
    for song in corpus.iter(util.SONG_ROOT):
        if util.RELEASE_DATE in song.attrib and song.attrib[util.RELEASE_DATE] is not None:
            years.append(int(song.attrib[util.RELEASE_DATE]))
            
    years_distro = Counter(years)
    rounded = {}
    ignore_list = []
    for key in years_distro.keys():
        if(key < 1950):
            ignore_list.append(key)
            
        else:
            rounded_year = int(round(key/5.0)*5.0)
            if(key in rounded):
                rounded[rounded_year] += years_distro[key]
            else:
                rounded[rounded_year] = years_distro[key]
        
    
    for key in ignore_list:
        del years_distro[key]
        
    plt.bar(years_distro.keys(), years_distro.values())
    plt.title("Number of songs by year")
    plt.show()
    
    plt.title("Number of songs by half decade")
    plt.bar(rounded.keys(), rounded.values())
    
    plt.show()


