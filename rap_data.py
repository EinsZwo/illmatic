'''
Created on Sept 11, 2021

@author: EinsZwo
'''



from lyricsgenius import Genius

token = "fDc8DVQcL6GnOecNnW3t8tXikTV1JgXkX-t9mg_Zrs9L1LzW5CKQYP3g5kygAAWK"

genius = Genius(access_token=token)



artist_names = [ "RZA" ]

# "The Notorious B.I.G.",
# "Black Star", "Common", "Common Market", "Da Lench Mob", "Dead Prez", "Rage Against the Machine", "Ice Cube", "Killer Mike", "MF Doom", "Mos Def", "Nas", "Talib Kweli", "Scarface", "Chuck D", "Wu Tang Clan", "Geto Boys",  "Raekwon"
# "Del the Funky Homosapien", "KRS-One", "GZA", "2Pac", "Atmosphere", "Beastie Boys", "A Tribe Called Quest", "Eminem"
# "Biz Markie", "Eazy-E" "DJ Jazzy Jeff & The Fresh Prince", "Kurtis Blow", "MC Hammer" "Eric B. & Rakim", "Rakim", "Kool Moe Dee"
# 1980s: "Too $hort", "Brand Nubian", "Chubb Rock", "Grand Puba"  "Bun B", "Missy Elliot" , "Pusha T", "Ludacris", "Big Boi"
# "Treacherous Three", "Fat Boys", "UTFO", "Sugarhill Gang", "Funky Four Plus One", "Afrika Bambaataa", "The Fearless Four", "Schoolly D", "Salt N Pepa", "MC Lyte"
# "The Roots", "Cold Crush Brothers", "Grandmaster Flash & The Furious Five" ,  "Coolio", "Kendrick Lamar",  "213", "Nate Dogg",
# "Lil Wayne", "Jay Z", "Kool G Rap", "Boogie Down Productions", "Warren G", "Diggable Planets","Odd Future", 
# , "Terminator X", "KMD", "Redman", "UGK", "Doja Cat", "Noname", "Princess Nokia", "Snow tha Product", 
# "T-Pain", "The Beatnuts", "The Pharcyde", "Main Source", "Diamond D", "Drake", "West Coast Crew", "Will Smith", "Dr. Octagon", "Comptons Most Wanted", "King Tee", "Bone Thugs-N-Harmony"
# "City High", "Macklemore", "Lil Jon", "Usher", "Lil Kim", "Kriss Kross", "Fugees", "MC Serch", "Luniz", "Lupe Fiasco",
# "Phife Dawg","Large Professor",  "J Dilla", "Rage Against The Machine", "Little Nas X", "Soulja Boy", "Bad Bunny", "Jungle Brothers", "Mase", "Fat Joe", "Big Pun", "Blue Scholars", "Kung Fu Vampire", "Tech N9ne", "Gravediggaz", "Insane Poetry"
# "Da Baby", "Lil Baby", "Tyler the Creator", "FLO RIDA", "Nelly", "DMX", "Young M.C.", "Master P", "Ultramagnetic MCs", "The Sequence", "L\'Trimm"
#  "Vanilla Ice", "2 Live Crew",  "Matronix", "De La Soul" 



# slick rick? queen latifa? "De La Soul", "Dr Dre",  "DJ Quik",  "Ghostface Killah", "P Diddy",  "Lauren Hill" "Q Tip",  "MC Ren", 



failedArtists = []


artist_albums = [ "Joe Budden    Halfway House","Common    Universal Mind Control","Ludacris    Theater of the Mind","Soulja Boy    iSouljaBoyTellEm", "Tyga    No Introduction","2 Pistols    Death Before Dishonor","Killer Mike    I Pledge Allegiance to the Grind II","Nas    Untitled","David Banner    The Greatest Story Ever Told","Yung Berg    Look What You Made Me","The Game    LAX","T.I.    Paper Trail"]
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

print()
print()

print("Failed artists: ")
for artist in failedArtists:
    print(artist)