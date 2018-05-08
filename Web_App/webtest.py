from bottle import route, run, request, static_file, get, post, request
import spotipy
from spotipy import oauth2
import webfunctions

PORT_NUMBER = 8080
SPOTIPY_CLIENT_ID = '1966863ffee1447487dd26e031db4d64'
SPOTIPY_CLIENT_SECRET = 'e68f42eff93b4d19905cf30dc1496d97'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read playlist-read-private playlist-read-collaborative'
CACHE = '.spotipyoauthcache'

sp_oauth = oauth2.SpotifyOAuth( SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET,SPOTIPY_REDIRECT_URI,scope=SCOPE,cache_path=CACHE)

@route('/')
def index():

    top = request.forms.get('top')
    age = request.forms.get('age')
    access_token = ""

    token_info = sp_oauth.get_cached_token()

    if token_info:
        print("Found cached token!")
        access_token = token_info['access_token']
    else:
        url = request.url
        code = sp_oauth.parse_response_code(url)
        if code:
            print("Found Spotify auth code in Request URL! Trying to get valid access token...")
            token_info = sp_oauth.get_access_token(code)
            access_token = token_info['access_token']

    if access_token and top and age:
        print("Access token available! Trying to get user information...")
        sp = spotipy.Spotify(access_token)
        playListTracks = webfunctions.get_playlist_tracks(access_token)
        userTracks = webfunctions.get_library_tracks(access_token)
        playListTracks.extend(userTracks)
        pointResult = webfunctions.get_points(playListTracks, age)
        i = 0
        results = getBaseHtml()
        results = results + "<ol>"
        while (i < top):
        	results = results + " <li>" + str(i + 1) + ". " + pointResult[i][0] + " - " + pointResult[i][2] + " - " + pointResult[i][1] + " - " + str(round(pointResult[i][3])) + " normiepoints" + " </li>"
        	i = i + 1
        results = results + " </ol> </body></html>"
        return results

    else if access_token:
        sp = spotipy.Spotify(access_token)
        result = getBaseHtml()
        result = result + '''
                <br><br>
                <p>Welcome to the Normiefier ''' + sys.argv[1] '''! Please provide the average age of the party you are at and how many tracks you want </p>
                <form action="/" method="post">
                    Top: <input name="top" type="number" min="1" max="1000" required />
                    Age: <input name="age" type="number" required>
                    <input type="submit">
                </form>
                </body>
                </html>
        '''
        return result

    else:
        return htmlForLoginButton()

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