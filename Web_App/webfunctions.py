import spotipy
from spotipy import oauth2
from spotipy.oauth2 import SpotifyClientCredentials
import csv
import datetime
def get_playlist_tracks(access_token):
    sp = spotipy.Spotify(access_token)
    userPlaylists = sp.current_user_playlists(50)
    playlistArray = userPlaylists["items"]
    while userPlaylists['next']:
        print('Getting user playlists...')
        userPlaylists = sp.next(userPlaylists)
        playlistArray.extend(userPlaylists['items'])
    tracks = []
    if (len(playlistArray) > 0):
        i = 0
        while i < len(playlistArray):
            try:
                results = sp.user_playlist_tracks(playlistArray[i]["owner"]["id"], playlistArray[i]["id"])
                tracks.extend(results['items'])
                while results['next']:
                    print("Getting playlist tracks")
                    results = sp.next(results)
                    tracks.extend(results['items'])
            except spotipy.client.SpotifyException:
                print("Got a 404")
            i = i + 1
    return tracks

def get_library_tracks(access_token):
    sp = spotipy.Spotify(access_token)
    j = 0;
    results = sp.current_user_saved_tracks(50)
    tracks = results['items']
    while results['next']:
        print("Getting library tracks")
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def get_points(tracksList, age):
    age = int(age)
    client_credentials_manager = SpotifyClientCredentials("1966863ffee1447487dd26e031db4d64", "e68f42eff93b4d19905cf30dc1496d97")
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    i = 0
    albumList = []
    artistList = []
    trackIdList = []
    while (i < len(tracksList)):
        albumList.append(tracksList[i]['track']['album']['id'])
        artistList.append(tracksList[i]['track']['artists'][0]['id'])
        trackIdList.append(tracksList[i]['track']['id'])
        i = i + 1
    k = 0
    albumRequest = []
    while (k * 20 < len(albumList)):
        low = k * 20
        high = (k+1) * 20
        try:
            albumRequest.append(sp.albums(albumList[low:high]))
        except AttributeError:
            print("Got an AttributeError in album")
            albumRequest.append([None])
        k += 1
    l = 0
    artistRequest = []
    while (l * 20 < len(artistList)):
        low = l * 20
        high = (l + 1) * 20
        try:
            artistRequest.append(sp.artists(artistList[low:high]))
        except AttributeError:
            print("Got an AttributeError in artist")
            artistRequest.append([None])
        l += 1
    trackFeatures = []
    m = 0
    while (m * 100 < len(tracksList)):
        low = m * 100
        high = (m + 1) * 100
        try:
            trackFeatures.append(sp.audio_features(trackIdList[low:high]))
        except AttributeError:
            print("Got an AttributeError in trackFeatures")
            trackFeatures.append([None])
        m += 1
    result = []
    j = 0
    while (j < len(tracksList)):
        if artistRequest[j // 21] == None:
            genrePoints = 0
            artistPopularity = 0
        else:
            try:
                genrePoints = get_genre_points(artistRequest[j // 21]['artists'][j % 20]['genres'])
            except TypeError:
                genrePoints = 0
            try:
                artistPopularity = artistRequest[j // 21]['artists'][j % 20]['popularity']
            except TypeError:
                artistPopularity = 0
        nostalgiaPoints = 0
        if albumRequest[j // 21] == None:
            nostalgiaPoints = 0
        else:
            try:
                album = albumRequest[j // 21]['albums'][j % 20]
                releaseYear = int(album['release_date'][:4])
                currentYear = datetime.datetime.now().year
                howLongAgo = currentYear - releaseYear
                if (howLongAgo <= 1):
                    nostalgiaPoints = 10
                elif (age - howLongAgo > 12 and age - howLongAgo < 24):
                    nostalgiaPoints = 15
                else:
                    nostalgiaPoints = 0
            except TypeError:
                nostalgiaPoints = 0
        if trackFeatures[j // 101] == None:
            dancability = 0
        else:
            try:
                dancability = trackFeatures[j // 101][j % 100]['danceability']
            except IndexError:
                dancability = 0
            except TypeError:
                dancability = 0
        trackPopularity = tracksList[j]['track']['popularity']
        if (genrePoints > 0):
            normiePoints = (genrePoints + artistPopularity + trackPopularity + (dancability * 100) + nostalgiaPoints) / 4
        else:
            normiePoints = (artistPopularity + trackPopularity + (dancability * 100) + nostalgiaPoints) / 3
        #Return points in the format: TrackName - AlbumName - ArtistName - Points
        result.append([tracksList[j]['track']['name'], tracksList[j]['track']['album']['name'], tracksList[j]['track']['artists'][0]['name'], normiePoints, tracksList[j]['track']['id']])
        j = j + 1
    return sorted(result, key=lambda x: x[3], reverse=True)    



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
    file = open("../ranked_genres_table.csv", "r")
    reader = csv.reader(file)
    for line in reader:
            if (genre == line[1]):
                return int(line[0])    


