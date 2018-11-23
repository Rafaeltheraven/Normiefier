import os
import functions

dir_path = r"path"
musicArray = []
limit = 70
averageAge = 20


for dirpath, _, filename in os.walk(dir_path):
    for f in filename:
        absolpath = os.path.join(dirpath, f)
        longPathFix = u"\\\\?\\" + absolpath
        print(longPathFix.encode("utf-8"))
        fileType = os.path.splitext(f)[1]
        titleAndArtist = functions.get_file_title(fileType, longPathFix)
        if (titleAndArtist is not None):
            title = titleAndArtist[0]
            artist = titleAndArtist[1]
            album = titleAndArtist[2]
            popularityOfTrack = functions.get_popularity_of_track_and_nostalgia_points(title, artist, averageAge, album)
            popularityOfArtistAndGenre = functions.get_popularity_of_artists_and_genre(artist)
            normiePoints = functions.calculate_normie_points(popularityOfTrack, popularityOfArtistAndGenre[0], popularityOfArtistAndGenre[1])
            if (normiePoints >= limit):
                print("added")
                musicArray.append([title, artist, normiePoints])

txt = open("normiefied.txt", "w")
for item in musicArray:
    txt.writelines("%s\n" % item)
txt.close()
