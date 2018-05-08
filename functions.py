from mutagen.flac import FLAC
from mutagen.asf import ASF
from mutagen.easyid3 import EasyID3
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import fnmatch
import datetime
import csv

client_credentials_manager = SpotifyClientCredentials("id", "secret")
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def get_file_title(fileType, absolpath):
    if fileType == ".mp3":
        audio = EasyID3(absolpath)
        if "artist" in audio and "title" in audio and "album" in audio:
            return [audio["title"][0], audio["artist"][0], audio["album"][0]]
        else:
            return None
    elif fileType == ".asf":
        audio = ASF(absolpath)
        if "artist" in audio and "title" in audio and "album" in audio:
            return [audio["title"][0], audio["artist"][0], audio["album"][0]]
        else:
            return None
    elif fileType == ".flac":
        audio = FLAC(absolpath)
        if "artist" in audio and "title" in audio and "album" in audio:
            return [audio["title"][0], audio["artist"][0], audio["album"][0]]
        else:
            return None
    else:
        return None


def get_popularity_of_track_and_nostalgia_points(trackTitle, artist, age, albumName):
    search = sp.search(q=trackTitle, type="track")
    albumSearch = sp.search(q=albumName + " " + artist, type="album")
    i = 0
    j = 0
    howLongAgo = 99999
    if len(search['tracks']['items']) >= 0:
        while i < len(search['tracks']['items']):
            if fnmatch.fnmatch(search['tracks']['items'][i]['name'].lower(), trackTitle.lower() + "*") or search['tracks']['items'][i]['name'].lower() == trackTitle.lower():
                while j < len(albumSearch['albums']['items']):
                    if albumSearch['albums']['items'][j]['artists'][0]['name'].lower() == artist.lower():
                        albumID = albumSearch['albums']['items'][j]['uri']
                        album = sp.album(albumID)
                        releaseYear = int(album['release_date'][:4])
                        currentYear = datetime.datetime.now().year
                        howLongAgo = currentYear - releaseYear
                    j += 1
                popularity = int(search['tracks']['items'][i]['popularity'])
                if (howLongAgo <= 1):
                    popularity += 10
                elif (age - howLongAgo > 12 and age - howLongAgo < 24):
                    popularity += 15
                return popularity
            i += 1
        return -1
    else:
        return -1


def get_popularity_of_artists_and_genre(artist):
	search = sp.search(q=artist, limit=1, type="artist")
	if len(search['artists']['items']) > 0:
		popularity = search['artists']['items'][0]['popularity']
		genres = search['artists']['items'][0]['genres']
		genrePoints = get_genre_points(genres)
		return [popularity, genrePoints]
	else:
		return [0, 0]


def calculate_normie_points(trackPopularityAndNostalgia, artistPopularity, genrePoints):
	print(trackPopularityAndNostalgia, artistPopularity, genrePoints)
	if genrePoints != 0:
		return round((trackPopularityAndNostalgia + int(artistPopularity) + genrePoints) / 3)
	else:
		return round((trackPopularityAndNostalgia + int(artistPopularity)) / 2)


def get_genre_points(genres):
	normie = 0
	counter = 0
	for genre in genres:
		rank = read_table(genre)
		if (rank is not None):
			normie += 1522 / rank
			counter += 1521
	if counter > 0:	
		return (normie / counter)
	else:
		return 0


def read_table(genre):
	file = open("ranked_genres_table.csv", "r")
	reader = csv.reader(file)
	for line in reader:
			if (genre == line[1]):
				return int(line[0])