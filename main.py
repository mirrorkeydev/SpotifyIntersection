import webapp2
import os
import jinja2
import requests
from google.appengine.api import urlfetch
import json
#from models import Food #not needed
import unicodedata
from requests_toolbelt.adapters import appengine

appengine.monkeypatch() #this is a patch that allows the python requests library to be used with Google App Engine

jinja_current_dir = jinja2.Environment( #jinja is used for templating
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

    #TODO: count how many times an artist is in your playlist (key-value pairs)
    #TODO: order your artists by how many songs you have from them
    #TODO: get started on song count
    #TODO: Spotify Client Credentials Flow
    #TOKNOW: There are now 2 places where you need to update the authenticator

class MainPage(webapp2.RequestHandler):
    def get(self):
        #CALLING THE SPOTIFY API FOR ONE PLAYLIST----------------------------------
        api = requests.get("https://api.spotify.com/v1/users/Christopher%20Kang/playlists/5cwOYhLtcppuXKRYrudBmq/", #tracks?offset=100
        headers={"Authorization": "Bearer BQBAOwM0UbhUL7mzG0JIkeMw2RYdEmZTFefdoYKseGn7jL3vCF-JyIiWhuEhoaCGx-myGloRhfFh8V9QyMJpxH9B1PyaYig97_-8xkisrusgEpYPvTOgOQUKFtZ9hfRsDVgHxkYGnvA_yo0YgJ29TEI8e4zssic",
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

        total_tracks = api_json["tracks"]["total"] #this is necessary as the next_api_json is formatted differently

        while total_tracks > 100: #spotify api only returns first 100 songs, so we need to request more
            next_api = requests.get(api_json["tracks"]["next"],
            headers={"Authorization": "Bearer BQBAOwM0UbhUL7mzG0JIkeMw2RYdEmZTFefdoYKseGn7jL3vCF-JyIiWhuEhoaCGx-myGloRhfFh8V9QyMJpxH9B1PyaYig97_-8xkisrusgEpYPvTOgOQUKFtZ9hfRsDVgHxkYGnvA_yo0YgJ29TEI8e4zssic",
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
                        print("artist already in list!")
                except (UnicodeEncodeError, IndexError):
                    print("an error has occurred")

            total_tracks -= 100

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
