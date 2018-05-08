from bottle import route, run, request, static_file, get, post, request
import spotipy
from spotipy import oauth2
import webfunctions
import sys
import json

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = 'id'
SPOTIPY_CLIENT_SECRET = "secret"
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative playlist-modify-private'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE)

@route('/', method="POST")
@route('/', method="GET")
def index():

	top = request.forms.get('top')
	age = request.forms.get('age')
	token = request.forms.get('token')
	if token:
		access_token = token
	else:
		access_token = ""

	#token_info = sp_oauth.get_cached_token()

#    if token_info:
#        print("Found cached token!")
#        access_token = token_info['access_token']
#    else:
	url = request.url
	code = sp_oauth.parse_response_code(url)
	if code:
		print("Found Spotify auth code in Request URL! Trying to get valid access token...")
		token_info = sp_oauth.get_access_token(code)
		access_token = token_info['access_token']

	if access_token and top and age:
		print("Access token available! Trying to get user information...")
		top = int(top)
		sp = spotipy.Spotify(access_token)
		playListTracks = webfunctions.get_playlist_tracks(access_token)
		userTracks = webfunctions.get_library_tracks(access_token)
		playListTracks.extend(userTracks)
		playListTracksCleaned = []
		seen = []
		j = 0
		while (j < len(playListTracks)):
			playlistID = playListTracks[j]["track"]["id"]
			if (playlistID not in seen):
				playListTracksCleaned.append(playListTracks[j])
				seen.append(playlistID)
			j += 1
		pointResult = webfunctions.get_points(playListTracksCleaned, age)
		i = 0
		results = getBaseHtml()
		results = results + "<h3>Your music has been analyzed, the top " + str(top) + " tracks for your party are:</h3><br>"
		results = results + "<ol>"
		if (len(pointResult) < top):
			top = len(pointResult)
		ids = ""
		while (i < top):
			results = results + " <li>" + str(i + 1) + ". " + pointResult[i][0] + " - " + pointResult[i][2] + " - " + pointResult[i][1] + " - " + str(round(pointResult[i][3])) + " normiepoints" + " </li>"
			ids = ids + pointResult[i][4] + ":"
			i = i + 1
		ids = ids[:-1]
		print("ids: " + ids)
		results = results + " </ol> <br><br><a href='/'>Logout</a><br>"
		results = results + '''
							<form action="/playlist/" method="post">
								<input name="token" type="hidden" value=''' + access_token + ''' />
								<input name="tracks" type="hidden" value=''' + ids + ''' />
								<input type="submit" value="Create a playlist" />
							</form>
							</body>
							</html>'''
		return results

	elif access_token:
		sp = spotipy.Spotify(access_token)
		current_user = sp.current_user()
		username = current_user["display_name"]
		if username == None:
			username = current_user["id"]
		result = getBaseHtml()
		result = result + '''
				<br><br>
				<p>Welcome to the Normiefier ''' + username + '''! Please provide the average age of the party you are at and how many tracks you want </p>
				<form action="/" method="post">
					Top: <input name="top" type="number" min="1" max="1000" required />
					Age: <input name="age" type="number" required>
					<input name="token" type="hidden" value=''' + access_token + ''' />
					<input type="submit">
				</form>
				</body>
				</html> '''
		return result

	else:
		return htmlForLoginButton()

@route('/playlist/', method="POST")
def createPlaylist():
	access_token = request.forms.get('token')
	tracks = request.forms.get('tracks')
	tracks = tracks.split(":")
	print("tracks: " + json.dumps(tracks))
	sp = spotipy.Spotify(access_token)
	userID = sp.current_user()["id"]
	print("Length of tracks: " + str(len(tracks)))
	userPlaylists = sp.current_user_playlists(50)
	playlistArray = userPlaylists["items"]
	while userPlaylists['next']:
		print('Getting user playlists...')
		userPlaylists = sp.next(userPlaylists)
		playlistArray.extend(userPlaylists['items'])
	j = 0
	playlistID = ""
	while j < len(playlistArray):
		if playlistArray[j]["name"] == "Normiefied":
			playlistID = playlistArray[j]["id"]
			playlistLink = playlistArray[j]["external_urls"]["spotify"]
			j = len(playlistArray)
		else:
			j = j + 1
	if (len(tracks) > 0):
		if playlistID == "":
			playlist = sp.user_playlist_create(userID, "Normiefied", public=False)
			playlistID = playlist["id"]
			playlistLink = playlist["external_urls"]["spotify"]
		i = 0
		while i*100 < len(tracks):
			low = i * 100
			high = (i + 1) * 100
			sp.user_playlist_replace_tracks(userID, playlistID, tracks[low:high])
			i = i + 1
		html = getBaseHtml()
		html = html + "<p>A playlist has been created, you can find it </p><a href=" + playlistLink + " target='_blank'>here</a><br>"
		html = html + "<a href='/'>Logout</a></body></html>"
	else:
		html = getBaseHtml()
		html = html + "<p>Something went wrong, oh no!</p></body></html>"
	return html

@route('/style.css')
def stylesheet():
	return static_file("style.css", "./")

def getBaseHtml():
	return "<html><head><title>Normiefier</title><link rel='stylesheet' href='/style.css'></head><body><h1>Welcome to the Normiefier!</h1><p>Are you at a party but you don't know what to play when they pass you the AUX cord? No worries, just login with your spotify account below and our 'sophisticated' algortihm will give you a list of the best songs to play, to the worst. Don't have Spotify? Don't worry, just download our desktop program and allow it to search through your entire music library. WARNING: This might take a very long time and expects you to have properly tagged your music files.</p>"

def htmlForLoginButton():
	auth_url = getSPOauthURI()
	base = getBaseHtml()
	htmlLoginButton = base + "<a href='" + auth_url + "'>Login to Spotify</a>"
	return htmlLoginButton


def getSPOauthURI():
	auth_url = sp_oauth.get_authorize_url()
	return auth_url

run(host='', port=8080)