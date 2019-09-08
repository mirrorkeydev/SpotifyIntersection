import webapp2
import os
import jinja2
import requests
import json
import spotipy
# from flask import Flask, request, redirect, g, render_template
import base64
# from bottle import route, run, request
import spotipy
from spotipy import oauth2
import urllib
import spotipy.util as util
from math import trunc
import unicodedata
from requests_toolbelt.adapters import appengine
import sys                          #these 3 lines fix most UnicodeDecodeErrors
reload(sys)                         #and UnicodeEncodeErrors due to names like
sys.setdefaultencoding("utf-8")     #Beyonce with the accent (#BeyonceError)

appengine.monkeypatch() #this is a patch that allows the python requests library to be used with Google App Engine

# app = Flask(__name__)

spotify_json = json.load(open("spotify.json"), "utf8")
client_id = spotify_json["client_id"]
client_secret = spotify_json["client_secret"]

jinja_current_dir = jinja2.Environment( #jinja is used for templating
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

global_dict = {}

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        pass

class MainPage(webapp2.RequestHandler):
    def get(self):
        start_template = jinja_current_dir.get_template("templates/homepage.html")
        self.response.write(start_template.render())

class FinalPage(webapp2.RequestHandler):
    def get(self):
        start_template = jinja_current_dir.get_template("templates/whoops.html")
        self.response.write(start_template.render())

    def post(self):
        #GETTING USER INFORMATION AND EXTRACTING THE APISTRING AND USER ID------------
        firsturl = self.request.get('furl') #these two collect the html form
        secondurl = self.request.get('lurl')

        firsturl_list = firsturl.split('/') #get the playlist string and user id
        firsturl_apistring = ""
        firsturl_userid = ""

        for index in range(len(firsturl_list)):
            if firsturl_list[index] == "playlist":
                firsturl_apistring = firsturl_list[index+1]
            if firsturl_list[index] == "user":
                firsturl_userid = firsturl_list[index+1]

        secondurl_list = secondurl.split('/')
        secondurl_apistring = ""
        secondurl_userid = ""


        for index in range(len(secondurl_list)):
            if secondurl_list[index] == "playlist":
                secondurl_apistring = secondurl_list[index+1]
            if secondurl_list[index] == "user":
                secondurl_userid = secondurl_list[index+1]

        print("after iterating through " + secondurl + ", we have determined that the userid is " +
            str(secondurl_userid) + "and the apistring is " + str(secondurl_apistring))
        print(firsturl_userid)
        print(secondurl_userid)
        print(secondurl_apistring)
        print(firsturl_apistring)

        #CALLING THE SPOTIFY API FOR THE FIRST PLAYLIST-1-1-1-1-1-1-1-1-1-1-1-1-1-1


        #Client credentials auth flow
        grant_type = 'client_credentials'
        body_params = {'grant_type' : grant_type}
        url='https://accounts.spotify.com/api/token'
        response=requests.post(url, data=body_params, auth = (client_id, client_secret))

        cc_api_content = response.content.split("\"") #this chunk gets the token from the string
        token = cc_api_content[3]

        #chunk below gets the first 100 songs
        api = requests.get("https://api.spotify.com/v1/users/"+firsturl_userid+"/playlists/"+firsturl_apistring+"/",
        headers={"Authorization": "Bearer " + token ,
        "Accept": "application/json","Content-Type": "application/json"})
        api_json = api.json() #changes Response object 'api' into an itemizable JSON (for analysis)
        api_text = api.text #changes Response object 'api' into text so it may be passed to jinja
        # print(api_text)

        #ANALYZING THE RECEIVED INFORMATION - FIRST PLAYLIST (FIRST 100 SONGS)----------------------
        username_1 = ""
        list_artists=[] #contains an unordered list of artist names
        list_artists_ordered=[] #contains an ordered list of artist names (based on dict_artists)
        list_songs_ordered=[] #contains a parallel ordered list with the corresponding appearance count
        dict_artists={} #contains (artist name):(how many appearances in playlist) (combines the two lists above)
        dict_songs={} #contains (song name):(unique song id)
        dict_song_artist={} #contains (song id):(artist)
        songs_analyzed_count = 0 #developer variable (only for us)
        dict_artists_id={} #contains (artist id):(artist name)

        if api_json["owner"]["display_name"] != None:
            username_1 = api_json["owner"]["display_name"]
        else:
            username_1 = api_json["owner"]["id"]

        for item in api_json["tracks"]["items"]: #this adds every new artist from songs 0-100 to list_artists
            songs_analyzed_count += 1
            try:
                if item["track"]["album"]["artists"][0]["name"] not in list_artists:
                    list_artists.append(item["track"]["album"]["artists"][0]["name"])
                    dict_artists[item["track"]["artists"][0]["name"]] = 1
                    dict_artists_id[item["track"]["album"]["artists"][0]["id"]] = item["track"]["album"]["artists"][0]["name"]
                    # print("success! " + item["track"]["artists"][0]["name"])
                else:
                    # print("artist " + item["track"]["artists"][0]["name"] + " already in list!")
                    if item["track"]["artists"][0]["name"] in dict_artists:
                        dict_artists[item["track"]["artists"][0]["name"]] += 1

            except (UnicodeEncodeError, IndexError):
                print("an error has occurred")
            try:
                # print("trying to pass key " +item["track"]["name"]+ " to dict_songs with value " + item["track"]["id"])
                dict_songs[item["track"]["name"]] = item["track"]["id"]
                dict_song_artist[item["track"]["id"]] = item["track"]["artists"][0]["name"]
            except (TypeError):
                print("Error with adding song - NoneType detected")

        # print(songs_analyzed_count)

        #ANALYZING THE RECEIVED INFORMATION - FIRST PLAYLIST (SONGS 100-200)------------------------
        total_tracks_left = api_json["tracks"]["total"] #this is necessary as the next_api_json is formatted differently
        flag = 0 #3 playlist breakdowns: 0-100 songs above, 100-200 songs below, 200+ songs further below

        next_api = ""
        next_api_json = ""
        next_api_text = ""

        if total_tracks_left > 100: #SONGS 100-200 and then 200+
            while total_tracks_left > 5: #spotify api only returns first 100 songs, so we need to request more
                if flag == 0:
                    # print("doing songs 100-200")
                    next_api = requests.get(api_json["tracks"]["next"], #calls 0-100 song json
                    headers={"Authorization": "Bearer " + token ,
                    "Accept": "application/json","Content-Type": "application/json"})
                    flag = 1 #ensures this will only run for song breakdown 100-200
                elif total_tracks_left > 100: #ANALYSIS SONGS 200+
                    # print("doing songs 200+")
                    next_api = requests.get(next_api_json["next"], #if total_tracks_left < 100, there will be no "next"
                    headers={"Authorization": "Bearer " + token ,
                    "Accept": "application/json","Content-Type": "application/json"})

                next_api_json = next_api.json()
                next_api_text = next_api.text
                # print(next_api_text)
                # print(next_api_json["items"])

                for item in range(1, len(next_api_json["items"])): #this adds every new artist to list_artists
                    x = next_api_json["items"][item]
                    songs_analyzed_count += 1
                    try:
                        if x["track"]["artists"][0]["name"] not in list_artists: #the formatting here is different than above, don't be fooled
                            list_artists.append(x["track"]["artists"][0]["name"])
                            dict_artists[x["track"]["artists"][0]["name"]] = 1
                            dict_artists_id[x["track"]["album"]["artists"][0]["id"]] = x["track"]["album"]["artists"][0]["name"]
                            # print("success! " + x["track"]["artists"][0]["name"])
                        else:
                            # print("artist " + x["track"]["artists"][0]["name"] + " already in list!")
                            if x["track"]["artists"][0]["name"] in dict_artists:
                                dict_artists[x["track"]["artists"][0]["name"]] += 1
                    except (UnicodeEncodeError, IndexError, UnicodeDecodeError):
                        print("an error has occurred")

                    try:
                        # print("trying to pass key " + x["track"]["name"]+ " to dict_songs with value " + x["track"]["id"])
                        dict_songs[x["track"]["name"]] = x["track"]["id"]
                        dict_song_artist[x["track"]["id"]] = x["track"]["artists"][0]["name"]

                    except (TypeError):
                        print("Error with adding song - NoneType detected")

                total_tracks_left -= 100
                # print("Finished the next 100 songs, " + str(total_tracks_left) + " songs left")

        # for item in list_artists: #this is a test printer that prints the artists to console
        #     try: #it will be removed later
        #         print item #find artists printed out in the console
        #     except (UnicodeEncodeError, IndexError): #the Beyonce Error
        #         item = item.encode('utf-8')
        #         print item

        # print(songs_analyzed_count)
        # print(dict_artists)
        for w in sorted(dict_artists, key=dict_artists.get, reverse=True): #this orders the dictionary by artist appearance and puts it into a new ordered list
            # print w, dict_artists[w] #key, value
            list_artists_ordered.append(w)
            list_songs_ordered.append(dict_artists[w])
        # print("finished printing Playlist 1s artists")


        #CALLING THE SPOTIFY API FOR THE SECOND PLAYLIST-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2
        # print("passing " + secondurl_userid + " and " + secondurl_apistring + " to api_2")
        api_2 = requests.get("https://api.spotify.com/v1/users/"+ secondurl_userid +"/playlists/" + secondurl_apistring + "/", #tracks?offset=100
        headers={"Authorization": "Bearer " + token ,
        "Accept": "application/json","Content-Type": "application/json"})
        api_json_2 = api_2.json() #changes Response object 'api' into an itemizable JSON
        api_text_2 = api_2.text #changes Response object 'api' into text so it may be passed to jinja

        #ANALYZING THE RECEIVED INFORMATION - SECOND PLAYLIST (FIRST 100 SONGS)-2-2-2-2-2-2-2-2-2-2-2-2-2-
        username_2 = ""
        list_artists_2=[] #contains an unordered list of artist names
        list_artists_ordered_2=[] #contains an ordered list of artist names (based on dict_artists)
        list_songs_ordered_2=[] #contains a parallel ordered list with the corresponding appearance count
        dict_artists_2={} #contains (artist name):(how many appearances in playlist) (combines the two lists above)
        dict_songs_2={} #contains (song name):(unique song id)
        dict_song_artist_2={} #contains (song id):(artist name)
        dict_artists_id_2={}

        songs_analyzed_count_2 = 0 #developer variable (only for us)

        if api_json_2["owner"]["display_name"] != None:
            username_2 = api_json_2["owner"]["display_name"]
        else:
            username_2 = api_json_2["owner"]["id"]

        for item in api_json_2["tracks"]["items"]: #this adds every new artist from songs 0-100 to list_artists
            songs_analyzed_count_2 += 1
            try:
                if item["track"]["album"]["artists"][0]["name"] not in list_artists_2:
                    list_artists_2.append(item["track"]["album"]["artists"][0]["name"])
                    dict_artists_2[item["track"]["artists"][0]["name"]] = 1
                    dict_artists_id_2[item["track"]["album"]["artists"][0]["id"]] = item["track"]["album"]["artists"][0]["name"]
                    # print("success! " + item["track"]["artists"][0]["name"])
                else:
                    # print("artist " + item["track"]["artists"][0]["name"] + " already in list!")
                    if item["track"]["artists"][0]["name"] in dict_artists_2:
                        dict_artists_2[item["track"]["artists"][0]["name"]] += 1
            except (UnicodeEncodeError, IndexError):
                print("an error has occurred")
            try:
                # print("trying to pass key " +item["track"]["name"]+ " to dict_songs_2 with value " + item["track"]["id"])
                dict_songs_2[item["track"]["name"]] = item["track"]["id"]
                dict_song_artist_2[item["track"]["id"]] = item["track"]["artists"][0]["name"]

            except (TypeError):
                print("Error with adding song - NoneType detected")

        # print(songs_analyzed_count_2)

        #ANALYZING THE RECEIVED INFORMATION - SECOND PLAYLIST (SONGS 100-200)-2-2-2-2-2-2-2-2-2-2-2-2-2-
        total_tracks_left_2 = api_json_2["tracks"]["total"] #this is necessary as the next_api_json is formatted differently
        flag_2 = 0 #3 playlist breakdowns: 0-100 songs above, 100-200 songs below, 200+ songs further below

        next_api_2 = ""
        next_api_json_2 = ""
        next_api_text_2 = ""

        if total_tracks_left_2 > 100:
            while total_tracks_left_2 > 5: #spotify api only returns first 100 songs, so we need to request more
                if flag_2 == 0 and api_json_2["tracks"]["total"] > 100:
                    # print("doing songs 100-200")
                    next_api_2 = requests.get(api_json_2["tracks"]["next"], #calls 0-100 song json
                    headers={"Authorization": "Bearer " + token ,
                    "Accept": "application/json","Content-Type": "application/json"})
                    flag_2 = 1 #ensures this will only run for song breakdown 100-200
                elif total_tracks_left_2 > 100: #ANALYSIS SONGS 200+
                    # print("doing songs 200+")
                    next_api_2 = requests.get(next_api_json_2["next"], #if total_tracks_left < 100, there will be no "next"
                    headers={"Authorization": "Bearer " + token ,
                    "Accept": "application/json","Content-Type": "application/json"})

                next_api_json_2 = next_api_2.json()
                next_api_text_2 = next_api_2.text

                for item in range(1, len(next_api_json_2["items"])): #this adds every new artist to list_artists
                    x = next_api_json_2["items"][item]
                    songs_analyzed_count_2 += 1
                    try:
                        if x["track"]["artists"][0]["name"] not in list_artists_2: #the formatting here is different than above, don't be fooled
                            list_artists_2.append(x["track"]["artists"][0]["name"])
                            dict_artists_2[x["track"]["artists"][0]["name"]] = 1
                            dict_artists_id_2[x["track"]["album"]["artists"][0]["id"]] = x["track"]["album"]["artists"][0]["name"]
                            # print("success! " + x["track"]["artists"][0]["name"])
                        else:
                            # print("artist " + x["track"]["artists"][0]["name"] + " already in list!")
                            if x["track"]["artists"][0]["name"] in dict_artists_2:
                                dict_artists_2[x["track"]["artists"][0]["name"]] += 1
                    except (UnicodeEncodeError, IndexError, UnicodeDecodeError):
                        print("an error has occurred")
                    try:
                        # print("trying to pass key " + x["track"]["name"]+ " to dict_songs with value " + x["track"]["id"])
                        dict_songs_2[x["track"]["name"]] = x["track"]["id"]
                    except (TypeError):
                        print("Error with adding song - NoneType detected")

                total_tracks_left_2 -= 100
                # print("Finished the next 100 songs, " + str(total_tracks_left_2) + " songs left")

        # for item in list_artists_2: #this is a test printer that prints the artists to console
        #     try: #it will be removed later
        #         print item #find artists printed out in the console
        #     except (UnicodeEncodeError, IndexError): #the Beyonce Error
        #         item = item.encode('utf-8')
        #         print item

        # print(songs_analyzed_count_2)
        # print(dict_artists_2)

        for w in sorted(dict_artists_2, key=dict_artists_2.get, reverse=True): #this orders the dictionary by artist appearance and puts it into a new ordered list
            # print w, dict_artists_2[w] #key, value
            list_artists_ordered_2.append(w)
            list_songs_ordered_2.append(dict_artists_2[w])
        # print("finished printing Playlist 2s artists")

        common_artists = [] #for the artists you will have in common

        for i in list_artists_ordered:
            for j in list_artists_ordered_2:
                if i == j:
                    common_artists.append(i)

        common_songs_names = [] #for songs in common with both playlists
        common_songs_ids = [] #parallel list containing id's of above songs
        common_songs_artists = [] #parallel list containing correct artist based on id
        common_artists_ids = {} #artist id: artist name

        for key in dict_songs: #dict_songs["name of song"] = 172-song-3235-id-238940
            for key2 in dict_songs_2: #populates the lists below
                if dict_songs[key] == dict_songs_2[key2]:
                    common_songs_names.append(key)
                    common_songs_ids.append(dict_songs)
                    common_songs_artists.append(dict_song_artist[dict_songs[key]])

        #Chunk below outputs how much (percentually) of a playlist is shared with the other
        total_songs_1 = api_json["tracks"]["total"]
        total_songs_2 = api_json_2["tracks"]["total"]
        total_shared_songs = len(common_songs_names)

        percent_shared = (100.0*len(common_songs_names)/api_json["tracks"]["total"])
        percent_shared_2 = (100.0*len(common_songs_names)/api_json_2["tracks"]["total"])
        trunc_percent_shared = (1.0*(trunc(percent_shared*100)))/100
        trunc_percent_shared_2 = (1.0*(trunc(percent_shared_2*100)))/100

        for artistid in dict_artists_id:
            for artistid2 in dict_artists_id_2:
                if artistid == artistid2:
                    common_artists_ids[artistid] = dict_artists_id[artistid]

        artist_images_links = {} # (artistid):(imagelink)
        #calling API for artist images
        for artistid in common_artists_ids:
            api_artists = requests.get("https://api.spotify.com/v1/artists/"+ artistid,
            headers={"Authorization": "Bearer " + token ,
            "Accept": "application/json","Content-Type": "application/json"})
            api_artists_json = api_artists.json() #changes Response object 'api' into an itemizable JSON (for analysis)
            try:
                artist_images_links[artistid] = api_artists_json["images"][2]["url"]
            except IndexError:
                try:
                    artist_images_links[artistid] = api_artists_json["images"][1]["url"]
                except IndexError:
                    try:
                        artist_images_links[artistid] = api_artists_json["images"][0]["url"]
                    except IndexError:
                        try:
                            artist_images_links[artistid] = api_artists_json["images"][0]["url"]
                        except IndexError:
                            print("no image")

#----------------------PASS DATA TO JINJA TEMPLATE-------------------------------------------
        dict = { #dictionary that will be passed to the start_template
            "u_1": username_1,
            "text": api_text,
            "next_text": next_api_text,
            "l_artists":list_artists,
            "l_artists_o": list_artists_ordered,
            "l_songs_o": list_songs_ordered,
            "c_artists":common_artists,
            "c_songs_n":common_songs_names,
            "c_songs_i":common_songs_ids,
            "c_songs_a":common_songs_artists,
            "c_artists_i":common_artists_ids,
            "a_images_l":artist_images_links,
            "d_artists":dict_artists,
            "u_2": username_2,
            "text_2": api_text_2,
            "next_text_2": next_api_text_2,
            "l_artists_2":list_artists_2,
            "l_artists_o_2": list_artists_ordered_2,
            "l_songs_o_2": list_songs_ordered_2,
            "d_artists_2":dict_artists_2,
            "url_1": firsturl,
            "url_2": secondurl,
            "apistring_1": firsturl_apistring,
            "apistring_2": secondurl_apistring,
            "userid_1": firsturl_userid,
            "userid_2": secondurl_userid,
            "d_song_artist":dict_song_artist,
            "d_song_artist_2":dict_song_artist_2,
            "t_songs_1":total_songs_1,
            "t_songs_2":total_songs_2,
            "t_shared_s":total_shared_songs,
            }

        start_template = jinja_current_dir.get_template("templates/results2.html")
        self.response.write(start_template.render(dict))

class AboutUsPage(webapp2.RequestHandler):
    def get(self):
        start_template = jinja_current_dir.get_template("templates/aboutus.html")
        self.response.write(start_template.render())

class AboutAppPage(webapp2.RequestHandler):
    def get(self):
        start_template = jinja_current_dir.get_template("templates/aboutapp.html")
        self.response.write(start_template.render())


# EVERYTHING COMMENTED BELOW THIS LINE WAS AN ATTEMPT TO USE THE AUTHENTICATION CODE FLOW.
# unfortunately, we decided to cut our losses and just stick with the client
# credentials flow, which doesn't provide all the functionality we ultimately
# wanted but that's alright. We needed to focus on refining what we had.

# class SpotifyAuth(webapp2.RequestHandler):
#     def get(self):
#
#         print("successfully entered index() function!")
#         CLIENT_ID = "59b8ca7342c2423fb79ff6951e9225e1"
#         CLIENT_SECRET = "15ebab6140284d3aa24309d876451981"
#
#         global_dict["clientid"]=CLIENT_ID
#         global_dict["clientsecret"]=CLIENT_SECRET
#
#         print("ok, now we're passing information to stuff")
#         # Spotify URLS
#         SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
#         SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
#         SPOTIFY_API_BASE_URL = "https://api.spotify.com"
#         API_VERSION = "v1"
#         SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)
#
#         global_dict["spotifytokenurl"]=SPOTIFY_TOKEN_URL
#         global_dict["spotifyapiurl"]=SPOTIFY_API_URL
#         global_dict["clientid"]=CLIENT_ID
#         global_dict["clientsecret"]=CLIENT_SECRET
#
#         # Server-side Parameters
#         CLIENT_SIDE_URL = "http://127.0.0.1"
#         PORT = 8080
#         REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
#         SCOPE = "playlist-modify-public playlist-modify-private"
#         STATE = ""
#         SHOW_DIALOG_bool = True
#         SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()
#
#         global_dict["redirecturi"]=REDIRECT_URI
#         global_dict["clientsecret"]=CLIENT_SECRET
#
#         auth_query_parameters = {
#             "response_type": "code",
#             "redirect_uri": REDIRECT_URI,
#             "scope": SCOPE,
#             # "state": STATE,
#             # "show_dialog": SHOW_DIALOG_str,
#             "client_id": CLIENT_ID
#         }
#         # Auth Step 1: Authorization
#         url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
#         auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
#         print("auth complete")
#         print(auth_url)
#         global_dict["redirect"] = auth_url
#         self.response.write("here there will be a button to AuthPart2")
#         if request:
#             print("request found pt 1")
#         else:
#             print("request not found pt 1")
#         return redirect(auth_url)
#         # return redirect(auth_url)
#         dict={
#         "auth":auth_url,
#         }
#
#         start_template = jinja_current_dir.get_template("templates/redirect.html")
#         self.response.write(start_template.render(dict))
#
# class AuthPart2(webapp2.RequestHandler):
#     def get(self):
#         if request:
#             print("request found")
#         else:
#             print("request not found")
#         print("successfully entered callback() function!")
#         # Auth Step 4: Requests refresh and access tokens
#         auth_token = request.args['code']
#         code_payload = {
#             "grant_type": "authorization_code",
#             "code": str(auth_token),
#             "redirect_uri": REDIRECT_URI
#         }
#         base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
#         headers = {"Authorization": "Basic {}".format(base64encoded)}
#         post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)
#
#         # Auth Step 5: Tokens are Returned to Application
#         response_data = json.loads(post_request.text)
#         access_token = response_data["access_token"]
#         refresh_token = response_data["refresh_token"]
#         token_type = response_data["token_type"]
#         expires_in = response_data["expires_in"]
#
#         # Auth Step 6: Use the access token to access Spotify API
#         authorization_header = {"Authorization":"Bearer {}".format(access_token)}
#
#         # Get profile data
#         user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
#         profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
#         profile_data = json.loads(profile_response.text)
#
#         # Get user playlist data
#         playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
#         playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
#         playlist_data = json.loads(playlists_response.text)
#
#         # Combine profile and playlist data to display
#         display_arr = [profile_data] + playlist_data["items"]
#         return display_arr
#         return render_template("index.html",sorted_array=display_arr)
#         print("everything should be updated now!")
#         self.response.write("bleh")
#         # start_template = jinja_current_dir.get_template("templates/aboutus.html")
#         # self.response.write(start_template.render())
#
# class PlaylistPage(webapp2.RequestHandler):
#     def get(self):
#         #attempted Authorization Code auth flow using Spotipy
#         # token = util.prompt_for_user_token(username='9jr9m0agxjjl2pcvx4jkpaj22',
#         # scope='playlist-modify-public',
#         # client_id='59b8ca7342c2423fb79ff6951e9225e1',
#         # client_secret='15ebab6140284d3aa24309d876451981',
#         # redirect_uri='http://localhost:8080/')
#
#         self.response.write("this is the playlist page, which will have a link to spotify auth")
#         # start_template = jinja_current_dir.get_template("templates/homepage.html")
#         # self.response.write(start_template.render())

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/aboutus', AboutUsPage),
    ('/final', FinalPage),
    ('/results', ResultsPage),
    ('/aboutapp', AboutAppPage)
    # ('/callback/q', AuthPart2),
    # ('/spotifyauth', SpotifyAuth),
    # ('/spotifyauth2', AuthPart2),
    # ('/playlistoutput', PlaylistPage),
], debug=True)

# if __name__ == "__main__":
#     app.run(debug=True, threaded=True, port=PORT)
