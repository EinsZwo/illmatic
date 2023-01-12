'''
Created on Nov 27, 2022

@author: EinsZwo
'''


import nltk
from illmatic import analyzer
from datasets import load_dataset

def referencePerplexityCalculations():
    """
    Calculate perplexity on reference corpora
    Based on the huggingface tutorial of perplexity
    """
    device, model, tokenizer = analyzer.setupPerplexity()
    
    
    files = ['shakespeare-macbeth.txt', 'melville-moby_dick.txt']
    
    for file in files:
        words = nltk.corpus.gutenberg.raw(file)
        
        perplexity = analyzer.calcPerplexity(tokenizer, model, device, words)
        
        with open("reference-perplexity.txt", "a+") as outfile:
            outfile.write(f"{file} : {perplexity}\n")

    
    wiki = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
    data = "\n\n".join(wiki["text"])
    perplexity = analyzer.calcPerplexity(tokenizer, model, device, data)

    with open("reference-perplexity.txt", "a+") as outfile:
        outfile.write(f"{dataset} : {perplexity}\n")
        
