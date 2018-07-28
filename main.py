#!/usr/bin/python
#
# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import webapp2
import os
import jinja2
import requests
from google.appengine.api import urlfetch
import json
from models import Food #not needed
import unicodedata
from requests_toolbelt.adapters import appengine

appengine.monkeypatch() #this is a patch that allows the python requests library to be used with Google App Engine

jinja_current_dir = jinja2.Environment( #jinja is used for templating
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        #api_key = "CHDZ8UreSrk50StUryZevwgH5D6U16Ec"
        api = requests.get("https://api.spotify.com/v1/users/mirrorkey/playlists/3QnM2I2B8vZYEqhignp37n/", #tracks?offset=100
        headers={"Authorization": "Bearer BQDhFXPijHJXC23KQf7b4whwzOU5dOTiahaj9zgHovgYVH7kH0GbLe6X_RxR9CSGqfmI0cRs60vGXo63F0GUqT_RFKJyKgXzM2LCQeCDpfn_Z4GKq0ouzrtCheoGNPgwc2LnFuBdZV01LssB8-dhq4wd1904xDM",
        "Accept": "application/json","Content-Type": "application/json"})
        # giphy_endpoint = "http://api.giphy.com/v1/gifs/search?q=google&limit=500&api_key="
        # response = urlfetch.fetch(giphy_endpoint).content
        # json_response = json.loads(response)
        list_artists=[] #will contain a playlist's artists when it is filled

        final_api = api.json() #changes Response object 'api' into an itemizable JSON

        print("about to start iteming")#test print statement
        for item in final_api["tracks"]["items"]:
            try:
                list_artists.append(item["track"]["album"]["artists"][0]["name"])
                print("success!")
            except (UnicodeEncodeError, IndexError):
                print("whoops lol")

        tracks = final_api["tracks"]["items"]
        api2 = api.text

        for item in list_artists:
            try:
                print item #find artists printed out in the console
            except (UnicodeEncodeError, IndexError): #the Beyonce Error
                item = item.encode('utf-8')
                print item

        dict = {
            "api_json": api2,
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
#
# class ResultsPage(webapp2.RequestHandler):
#     def get(self):
#         food_list_template = jinja_current_dir.get_template("templates/foodlist.html")
#         fav_foods = Food.query().order(-Food.food_name).fetch(3)
#         dict_for_template = {'top_fav_foods': fav_foods}
#         self.response.write(food_list_template.render(dict_for_template))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/results', ResultsPage)
], debug=True)
