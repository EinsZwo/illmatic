'''
Created on Nov 29, 2022

@author: matth
'''
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer,TfidfVectorizer



filenames = []
for year in range(1980,2020,5):
    songYear = year
    if songYear == 1980:
        songYear = songYear-1
    
    filename=f"{year}_{year+4}.txt"
    filenames.append(filename)
    
vectorizer = TfidfVectorizer(input='filename',use_idf=True,stop_words='english',max_df=0.7)

print(filenames)

tfidf = vectorizer.fit_transform(filenames)




for doc in tfidf:
    df = pd.DataFrame(doc.T.todense(), index=vectorizer.get_feature_names_out(), columns=["TF-IDF"])
    df = df.sort_values('TF-IDF', ascending=False)
    print (df.head(50))