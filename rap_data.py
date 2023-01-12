'''
Created on Oct 11, 2022
'''



from lyricsgenius import Genius

token = "fDc8DVQcL6GnOecNnW3t8tXikTV1JgXkX-t9mg_Zrs9L1LzW5CKQYP3g5kygAAWK"

genius = Genius(access_token=token)


failedArtists = []


# a '    '-delimited tuple list of artist and album by the artist to download
artist_albums = ["Tyler, The Creator    Goblin","Killer Mike    PL3DGE","Big K.R.I.T.    R4: The Prequel","Pitbull    Planet Pit","Canibus    Lyrical Law"]


for artist_album in artist_albums:
    numTries = 0
    gotArtist = False
    split = artist_album.split("    ")
    artist_name = split[0]
    album_name = split[1]
    while not gotArtist:
        try:
            numTries+=1
            if numTries > 10:
                
                failedArtists.append(artist_name+"    "+album_name)
                gotArtist=True
                print(f"\nSkipping {artist_album}...\n")
                break
            
            album = genius.search_album(album_name, artist_name)
            album.save_lyrics(filename=(artist_name+"_"+album_name),extension='json',overwrite=True)
            gotArtist = True
            break
        
        except:
            pass 
    
with open("failed_artists.txt", "a" ) as file:
    file.write("\n")
    file.write("\n".join(failedArtists))


print("Failed artists: ")
for artist in failedArtists:
    print(artist)