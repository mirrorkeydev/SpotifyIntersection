import webapp2
import os
import jinja2
import requests
from google.appengine.api import urlfetch
import json
#from models import Food #not needed
import unicodedata
from requests_toolbelt.adapters import appengine
import sys                          #|these 3 lines fix most UnicodeDecodeErrors
reload(sys)                         #|and UnicodeEncodeErrors due to names like
sys.setdefaultencoding("utf-8")     #|Beyonce with the accent (#BeyonceError)

appengine.monkeypatch() #this is a patch that allows the python requests library to be used with Google App Engine


jinja_current_dir = jinja2.Environment( #jinja is used for templating
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

    #TODO: count how many times an artist is in your playlist (key-value pairs)
    #TODO: order your artists by how many songs you have from them
    #TODO: get started on song count
    #TODO: Spotify Client Credentials Flow
    #TOKNOW: There are now 3 places where you need to update the authenticator

class MainPage(webapp2.RequestHandler):
    def get(self):
        #CALLING THE SPOTIFY API FOR ONE PLAYLIST----------------------------------
        api = requests.get("https://api.spotify.com/v1/users/mirrorkey/playlists/3QnM2I2B8vZYEqhignp37n/", #tracks?offset=100
        headers={"Authorization": "Bearer BQD9munmcGzOCQPgvblQ9DhDJcqgCEQQlMFuJO3tBWdzUDnTRzOl8Hh_QyfUx3V4DHG6gW3v6GJlgqgxctnkHwNXdJA8R7rYXHM-5ytcFWItBzA962R-0WSGz5TvqQS6YmxVWk2EYtj89H_U5IhUrNhcgtLNTQU",
        "Accept": "application/json","Content-Type": "application/json"})
        api_json = api.json() #changes Response object 'api' into an itemizable JSON
        api_text = api.text #changes 'api' into text so it may be viewed

        #ANALYZING THE RECEIVED INFORMATION (FIRST 100 SONGS)----------------------
        list_artists=[] #will contain a playlist's artists when it is filled (names)
        list_songs=[] #will contain a playlist's songs when it is filled (unique song ID's)
        songs_analyzed_count = 0

        for item in api_json["tracks"]["items"]: #this adds every new artist to list_artists
            songs_analyzed_count += 1
            try:
                if item["track"]["album"]["artists"][0]["name"] not in list_artists:
                    list_artists.append(item["track"]["album"]["artists"][0]["name"])
                    print("success!")
                else:
                    print("artist already in list!")
            except (UnicodeEncodeError, IndexError):
                print("an error has occurred")

        print(songs_analyzed_count)

        total_tracks_left = api_json["tracks"]["total"] #this is necessary as the next_api_json is formatted differently
        flag = 0 #3 playlist breakdowns: 0-100 songs above, 100-200 songs below, 200+ songs further below

        next_api = ""
        next_api_json = ""
        next_api_text = ""

        while total_tracks_left > 5: #spotify api only returns first 100 songs, so we need to request more
            if flag == 0:
                print("doing songs 100-200")
                next_api = requests.get(api_json["tracks"]["next"], #calls 0-100 song json
                headers={"Authorization": "Bearer BQD9munmcGzOCQPgvblQ9DhDJcqgCEQQlMFuJO3tBWdzUDnTRzOl8Hh_QyfUx3V4DHG6gW3v6GJlgqgxctnkHwNXdJA8R7rYXHM-5ytcFWItBzA962R-0WSGz5TvqQS6YmxVWk2EYtj89H_U5IhUrNhcgtLNTQU",
                "Accept": "application/json","Content-Type": "application/json"})
                flag = 1 #ensures this will only run for song breakdown 100-200
            elif total_tracks_left > 100: #song breakdown 200+
                print("doing songs 200+")
                next_api = requests.get(next_api_json["next"], #if total_tracks_left < 100, there will be no "next"
                headers={"Authorization": "Bearer BQD9munmcGzOCQPgvblQ9DhDJcqgCEQQlMFuJO3tBWdzUDnTRzOl8Hh_QyfUx3V4DHG6gW3v6GJlgqgxctnkHwNXdJA8R7rYXHM-5ytcFWItBzA962R-0WSGz5TvqQS6YmxVWk2EYtj89H_U5IhUrNhcgtLNTQU",
                "Accept": "application/json","Content-Type": "application/json"})

            next_api_json = next_api.json()
            next_api_text = next_api.text

            for item in range(1, len(next_api_json["items"])): #this adds every new artist to list_artists
                x = next_api_json["items"][item]
                songs_analyzed_count += 1
                try:
                    if x["track"]["artists"][0]["name"] not in list_artists: #the formatting here is different than above, don't be fooled
                        list_artists.append(x["track"]["artists"][0]["name"])
                        print("success!")
                    else:
                        print("artist " + x["track"]["artists"][0]["name"] + " already in list!")
                except (UnicodeEncodeError, IndexError, UnicodeDecodeError):
                    print("an error has occurred")

            total_tracks_left -= 100
            print("Finished the next 100 songs, " + str(total_tracks_left) + " songs left")

        for item in list_artists: #this is a test printer that prints the artists to console
            try:
                print item #find artists printed out in the console
            except (UnicodeEncodeError, IndexError): #the Beyonce Error
                item = item.encode('utf-8')
                print item

        print(songs_analyzed_count)

        dict = { #dictionary that will be passed to the start_template
            "text": api_text,
            "next_text": next_api_text,
            "test":"hello",
            "artists":list_artists
        }

        start_template = jinja_current_dir.get_template("templates/welcome.html")
        self.response.write(start_template.render(dict))

    # def post(self):
    #     the_fav_food = self.request.get('user-fav-food')
    #
    #     #put into database (optional)
    #     food_record = Food(food_name = the_fav_food)
    #     food_record.put()
    #
    #     #pass to the template via a dictionary
    #     variable_dict = {'fav_food_for_view': the_fav_food}
    #     end_template = jinja_current_dir.get_template("templates/results.html")
    #     self.response.write(end_template.render(variable_dict))

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        food_list_template = jinja_current_dir.get_template("templates/foodlist.html")
        fav_foods = Food.query().order(-Food.food_name).fetch(3)
        dict_for_template = {'top_fav_foods': fav_foods}
        self.response.write(food_list_template.render(dict_for_template))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/results', ResultsPage)
], debug=True)
