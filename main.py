import webapp2
import os
import jinja2
import requests
from google.appengine.api import urlfetch
import json
#from models import Food #not needed
import unicodedata
from requests_toolbelt.adapters import appengine
import sys                          #these 3 lines fix most UnicodeDecodeErrors
reload(sys)                         #and UnicodeEncodeErrors due to names like
sys.setdefaultencoding("utf-8")     #Beyonce with the accent (#BeyonceError)

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

class ResultsPage(webapp2.RequestHandler):
    def get(self):
        #CALLING THE SPOTIFY API FOR THE FIRST PLAYLIST-1-1-1-1-1-1-1-1-1-1-1-1-1-1
        api = requests.get("https://api.spotify.com/v1/users/mirrorkey/playlists/3QnM2I2B8vZYEqhignp37n/", #tracks?offset=100
        headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
        "Accept": "application/json","Content-Type": "application/json"})
        api_json = api.json() #changes Response object 'api' into an itemizable JSON
        api_text = api.text #changes Response object 'api' into text so it may be passed to jinja

        #ANALYZING THE RECEIVED INFORMATION - FIRST PLAYLIST (FIRST 100 SONGS)----------------------
        username_1 = ""
        list_artists=[] #contains an unordered list of artist names
        list_artists_ordered=[] #contains an ordered list of artist names (based on dict_artists)
        list_songs_ordered=[] #contains a parallel ordered list with the corresponding appearance count
        dict_artists={} #contains (artist name):(how many appearances in playlist) (combines the two lists above)
        list_songs=[] #contains an unordered list of the playlist's songs
        songs_analyzed_count = 0 #developer variable (only for us)

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
                    print("success! " + item["track"]["artists"][0]["name"])
                else:
                    print("artist " + item["track"]["artists"][0]["name"] + " already in list!")
                    if item["track"]["artists"][0]["name"] in dict_artists:
                        dict_artists[item["track"]["artists"][0]["name"]] += 1

            except (UnicodeEncodeError, IndexError):
                print("an error has occurred")

        print(songs_analyzed_count)

        #ANALYZING THE RECEIVED INFORMATION - FIRST PLAYLIST (SONGS 100-200)------------------------
        total_tracks_left = api_json["tracks"]["total"] #this is necessary as the next_api_json is formatted differently
        flag = 0 #3 playlist breakdowns: 0-100 songs above, 100-200 songs below, 200+ songs further below

        next_api = ""
        next_api_json = ""
        next_api_text = ""

        while total_tracks_left > 5: #spotify api only returns first 100 songs, so we need to request more
            if flag == 0:
                print("doing songs 100-200")
                next_api = requests.get(api_json["tracks"]["next"], #calls 0-100 song json
                headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
                "Accept": "application/json","Content-Type": "application/json"})
                flag = 1 #ensures this will only run for song breakdown 100-200
            elif total_tracks_left > 100: #ANALYSIS SONGS 200+
                print("doing songs 200+")
                next_api = requests.get(next_api_json["next"], #if total_tracks_left < 100, there will be no "next"
                headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
                "Accept": "application/json","Content-Type": "application/json"})

            next_api_json = next_api.json()
            next_api_text = next_api.text

            for item in range(1, len(next_api_json["items"])): #this adds every new artist to list_artists
                x = next_api_json["items"][item]
                songs_analyzed_count += 1
                try:
                    if x["track"]["artists"][0]["name"] not in list_artists: #the formatting here is different than above, don't be fooled
                        list_artists.append(x["track"]["artists"][0]["name"])
                        dict_artists[x["track"]["artists"][0]["name"]] = 1
                        print("success! " + x["track"]["artists"][0]["name"])
                    else:
                        print("artist " + x["track"]["artists"][0]["name"] + " already in list!")
                        if x["track"]["artists"][0]["name"] in dict_artists:
                            dict_artists[x["track"]["artists"][0]["name"]] += 1
                except (UnicodeEncodeError, IndexError, UnicodeDecodeError):
                    print("an error has occurred")

            total_tracks_left -= 100
            print("Finished the next 100 songs, " + str(total_tracks_left) + " songs left")

        for item in list_artists: #this is a test printer that prints the artists to console
            try: #it will be removed later
                print item #find artists printed out in the console
            except (UnicodeEncodeError, IndexError): #the Beyonce Error
                item = item.encode('utf-8')
                print item

        print(songs_analyzed_count)
        print(dict_artists)
        for w in sorted(dict_artists, key=dict_artists.get, reverse=True): #this orders the dictionary by artist appearance and puts it into a new ordered list
            print w, dict_artists[w] #key, value
            list_artists_ordered.append(w)
            list_songs_ordered.append(dict_artists[w])
        print("finished printing Playlist 1s artists")


        #CALLING THE SPOTIFY API FOR THE SECOND PLAYLIST-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2
        api_2 = requests.get("https://api.spotify.com/v1/users/tomvestuto/playlists/7dMD9LPqoXwMXdG8syTm8q/", #tracks?offset=100
        headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
        "Accept": "application/json","Content-Type": "application/json"})
        api_json_2 = api_2.json() #changes Response object 'api' into an itemizable JSON
        api_text_2 = api_2.text #changes Response object 'api' into text so it may be passed to jinja

        #ANALYZING THE RECEIVED INFORMATION - SECOND PLAYLIST (FIRST 100 SONGS)-2-2-2-2-2-2-2-2-2-2-2-2-2-
        username_2 = ""
        list_artists_2=[] #contains an unordered list of artist names
        list_artists_ordered_2=[] #contains an ordered list of artist names (based on dict_artists)
        list_songs_ordered_2=[] #contains a parallel ordered list with the corresponding appearance count
        dict_artists_2={} #contains (artist name):(how many appearances in playlist) (combines the two lists above)
        list_songs_2=[] #contains an unordered list of the playlist's songs
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
                    print("success! " + item["track"]["artists"][0]["name"])
                else:
                    print("artist " + item["track"]["artists"][0]["name"] + " already in list!")
                    if item["track"]["artists"][0]["name"] in dict_artists_2:
                        dict_artists_2[item["track"]["artists"][0]["name"]] += 1

            except (UnicodeEncodeError, IndexError):
                print("an error has occurred")

        print(songs_analyzed_count_2)

        #ANALYZING THE RECEIVED INFORMATION - SECOND PLAYLIST (SONGS 100-200)-2-2-2-2-2-2-2-2-2-2-2-2-2-
        total_tracks_left_2 = api_json_2["tracks"]["total"] #this is necessary as the next_api_json is formatted differently
        flag_2 = 0 #3 playlist breakdowns: 0-100 songs above, 100-200 songs below, 200+ songs further below

        next_api_2 = ""
        next_api_json_2 = ""
        next_api_text_2 = ""

        while total_tracks_left_2 > 5: #spotify api only returns first 100 songs, so we need to request more
            if flag_2 == 0:
                print("doing songs 100-200")
                next_api_2 = requests.get(api_json_2["tracks"]["next"], #calls 0-100 song json
                headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
                "Accept": "application/json","Content-Type": "application/json"})
                flag_2 = 1 #ensures this will only run for song breakdown 100-200
            elif total_tracks_left_2 > 100: #ANALYSIS SONGS 200+
                print("doing songs 200+")
                next_api_2 = requests.get(next_api_json_2["next"], #if total_tracks_left < 100, there will be no "next"
                headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
                "Accept": "application/json","Content-Type": "application/json"})

            next_api_json_2 = next_api_2.json()
            next_api_text_2 = next_api_2.text

            for item in range(1, len(next_api_json["items"])): #this adds every new artist to list_artists
                x = next_api_json_2["items"][item]
                songs_analyzed_count_2 += 1
                try:
                    if x["track"]["artists"][0]["name"] not in list_artists_2: #the formatting here is different than above, don't be fooled
                        list_artists_2.append(x["track"]["artists"][0]["name"])
                        dict_artists_2[x["track"]["artists"][0]["name"]] = 1
                        print("success! " + x["track"]["artists"][0]["name"])
                    else:
                        print("artist " + x["track"]["artists"][0]["name"] + " already in list!")
                        if x["track"]["artists"][0]["name"] in dict_artists_2:
                            dict_artists_2[x["track"]["artists"][0]["name"]] += 1
                except (UnicodeEncodeError, IndexError, UnicodeDecodeError):
                    print("an error has occurred")

            total_tracks_left_2 -= 100
            print("Finished the next 100 songs, " + str(total_tracks_left_2) + " songs left")

        for item in list_artists_2: #this is a test printer that prints the artists to console
            try: #it will be removed later
                print item #find artists printed out in the console
            except (UnicodeEncodeError, IndexError): #the Beyonce Error
                item = item.encode('utf-8')
                print item

        print(songs_analyzed_count_2)
        print(dict_artists_2)

        for w in sorted(dict_artists_2, key=dict_artists_2.get, reverse=True): #this orders the dictionary by artist appearance and puts it into a new ordered list
            print w, dict_artists_2[w] #key, value
            list_artists_ordered_2.append(w)
            list_songs_ordered_2.append(dict_artists_2[w])
        print("finished printing Playlist 2s artists")

#----------------------PASS DATA TO JINJA TEMPLATE-------------------------------------------
        dict = { #dictionary that will be passed to the start_template
            "u_1": username_1,
            "text": api_text,
            "next_text": next_api_text,
            "l_artists":list_artists,
            "l_artists_o": list_artists_ordered,
            "l_songs_o": list_songs_ordered,
            "d_artists":dict_artists,
            "u_2": username_2,
            "text_2": api_text_2,
            "next_text_2": next_api_text_2,
            "l_artists_2":list_artists_2,
            "l_artists_o_2": list_artists_ordered_2,
            "l_songs_o_2": list_songs_ordered_2,
            "d_artists_2":dict_artists_2,
        }

        start_template = jinja_current_dir.get_template("templates/homepage.html")
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

class MainPage(webapp2.RequestHandler):
    def get(self):
        start_template = jinja_current_dir.get_template("templates/homepage.html")
        self.response.write(start_template.render())

class FinalPage(webapp2.RequestHandler):
    def get(self):
        start_template = jinja_current_dir.get_template("templates/results.html")
        self.response.write(start_template.render())
    def post(self):
        #GETTING USER INFORMATION AND EXTRACTING THE APISTRING AND USER ID------------
        firsturl = self.request.get('furl')
        secondurl = self.request.get('lurl')
        firstname = self.request.get('fname')
        secondname = self.request.get('lname')

        firsturl_list = firsturl.split('/')
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
        api = requests.get("https://api.spotify.com/v1/users/"+firsturl_userid+"/playlists/"+firsturl_apistring+"/", #tracks?offset=100
        headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
        "Accept": "application/json","Content-Type": "application/json"})
        api_json = api.json() #changes Response object 'api' into an itemizable JSON
        api_text = api.text #changes Response object 'api' into text so it may be passed to jinja
        # print(api_text)

        #ANALYZING THE RECEIVED INFORMATION - FIRST PLAYLIST (FIRST 100 SONGS)----------------------
        username_1 = ""
        list_artists=[] #contains an unordered list of artist names
        list_artists_ordered=[] #contains an ordered list of artist names (based on dict_artists)
        list_songs_ordered=[] #contains a parallel ordered list with the corresponding appearance count
        dict_artists={} #contains (artist name):(how many appearances in playlist) (combines the two lists above)
        list_songs=[] #contains an unordered list of the playlist's songs
        songs_analyzed_count = 0 #developer variable (only for us)

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
                    # print("success! " + item["track"]["artists"][0]["name"])
                else:
                    # print("artist " + item["track"]["artists"][0]["name"] + " already in list!")
                    if item["track"]["artists"][0]["name"] in dict_artists:
                        dict_artists[item["track"]["artists"][0]["name"]] += 1

            except (UnicodeEncodeError, IndexError):
                print("an error has occurred")

        print(songs_analyzed_count)

        #ANALYZING THE RECEIVED INFORMATION - FIRST PLAYLIST (SONGS 100-200)------------------------
        total_tracks_left = api_json["tracks"]["total"] #this is necessary as the next_api_json is formatted differently
        flag = 0 #3 playlist breakdowns: 0-100 songs above, 100-200 songs below, 200+ songs further below

        next_api = ""
        next_api_json = ""
        next_api_text = ""

        if total_tracks_left > 100:
            while total_tracks_left > 5: #spotify api only returns first 100 songs, so we need to request more
                if flag == 0:
                    print("doing songs 100-200")
                    next_api = requests.get(api_json["tracks"]["next"], #calls 0-100 song json
                    headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
                    "Accept": "application/json","Content-Type": "application/json"})
                    flag = 1 #ensures this will only run for song breakdown 100-200
                elif total_tracks_left > 100: #ANALYSIS SONGS 200+
                    print("doing songs 200+")
                    next_api = requests.get(next_api_json["next"], #if total_tracks_left < 100, there will be no "next"
                    headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
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
                            # print("success! " + x["track"]["artists"][0]["name"])
                        else:
                            # print("artist " + x["track"]["artists"][0]["name"] + " already in list!")
                            if x["track"]["artists"][0]["name"] in dict_artists:
                                dict_artists[x["track"]["artists"][0]["name"]] += 1
                    except (UnicodeEncodeError, IndexError, UnicodeDecodeError):
                        print("an error has occurred")

                total_tracks_left -= 100
                print("Finished the next 100 songs, " + str(total_tracks_left) + " songs left")

        # for item in list_artists: #this is a test printer that prints the artists to console
        #     try: #it will be removed later
        #         print item #find artists printed out in the console
        #     except (UnicodeEncodeError, IndexError): #the Beyonce Error
        #         item = item.encode('utf-8')
        #         print item

        print(songs_analyzed_count)
        # print(dict_artists)
        for w in sorted(dict_artists, key=dict_artists.get, reverse=True): #this orders the dictionary by artist appearance and puts it into a new ordered list
            # print w, dict_artists[w] #key, value
            list_artists_ordered.append(w)
            list_songs_ordered.append(dict_artists[w])
        print("finished printing Playlist 1s artists")


        #CALLING THE SPOTIFY API FOR THE SECOND PLAYLIST-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2-2
        print("passing " + secondurl_userid + " and " + secondurl_apistring + " to api_2")
        api_2 = requests.get("https://api.spotify.com/v1/users/"+ secondurl_userid +"/playlists/" + secondurl_apistring + "/", #tracks?offset=100
        headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
        "Accept": "application/json","Content-Type": "application/json"})
        api_json_2 = api_2.json() #changes Response object 'api' into an itemizable JSON
        api_text_2 = api_2.text #changes Response object 'api' into text so it may be passed to jinja

        #ANALYZING THE RECEIVED INFORMATION - SECOND PLAYLIST (FIRST 100 SONGS)-2-2-2-2-2-2-2-2-2-2-2-2-2-
        username_2 = ""
        list_artists_2=[] #contains an unordered list of artist names
        list_artists_ordered_2=[] #contains an ordered list of artist names (based on dict_artists)
        list_songs_ordered_2=[] #contains a parallel ordered list with the corresponding appearance count
        dict_artists_2={} #contains (artist name):(how many appearances in playlist) (combines the two lists above)
        list_songs_2=[] #contains an unordered list of the playlist's songs
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
                    # print("success! " + item["track"]["artists"][0]["name"])
                else:
                    # print("artist " + item["track"]["artists"][0]["name"] + " already in list!")
                    if item["track"]["artists"][0]["name"] in dict_artists_2:
                        dict_artists_2[item["track"]["artists"][0]["name"]] += 1

            except (UnicodeEncodeError, IndexError):
                print("an error has occurred")

        print(songs_analyzed_count_2)

        #ANALYZING THE RECEIVED INFORMATION - SECOND PLAYLIST (SONGS 100-200)-2-2-2-2-2-2-2-2-2-2-2-2-2-
        total_tracks_left_2 = api_json_2["tracks"]["total"] #this is necessary as the next_api_json is formatted differently
        flag_2 = 0 #3 playlist breakdowns: 0-100 songs above, 100-200 songs below, 200+ songs further below

        next_api_2 = ""
        next_api_json_2 = ""
        next_api_text_2 = ""

        if total_tracks_left_2 > 100:
            while total_tracks_left_2 > 5: #spotify api only returns first 100 songs, so we need to request more
                if flag_2 == 0 and api_json_2["tracks"]["total"] > 100:
                    print("doing songs 100-200")
                    next_api_2 = requests.get(api_json_2["tracks"]["next"], #calls 0-100 song json
                    headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
                    "Accept": "application/json","Content-Type": "application/json"})
                    flag_2 = 1 #ensures this will only run for song breakdown 100-200
                elif total_tracks_left_2 > 100: #ANALYSIS SONGS 200+
                    print("doing songs 200+")
                    next_api_2 = requests.get(next_api_json_2["next"], #if total_tracks_left < 100, there will be no "next"
                    headers={"Authorization": "Bearer BQDuyY3lOC1mn5AjKYiscfyXpj_8okLC00UuCGBBsHjIyOdodFyudi_hXeeudfDpVMr8c99Cf7jUaDjY6n-SfWTiO8Sc2-FlMsMs5ratmMGj7gkPCIRnC5TJ858ZJfbkExePxT-2Nr0U4wzj8R-e2zDB2IzNdBw",
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
                            # print("success! " + x["track"]["artists"][0]["name"])
                        else:
                            # print("artist " + x["track"]["artists"][0]["name"] + " already in list!")
                            if x["track"]["artists"][0]["name"] in dict_artists_2:
                                dict_artists_2[x["track"]["artists"][0]["name"]] += 1
                    except (UnicodeEncodeError, IndexError, UnicodeDecodeError):
                        print("an error has occurred")

                total_tracks_left_2 -= 100
                print("Finished the next 100 songs, " + str(total_tracks_left_2) + " songs left")

        # for item in list_artists_2: #this is a test printer that prints the artists to console
        #     try: #it will be removed later
        #         print item #find artists printed out in the console
        #     except (UnicodeEncodeError, IndexError): #the Beyonce Error
        #         item = item.encode('utf-8')
        #         print item

        print(songs_analyzed_count_2)
        # print(dict_artists_2)

        for w in sorted(dict_artists_2, key=dict_artists_2.get, reverse=True): #this orders the dictionary by artist appearance and puts it into a new ordered list
            print w, dict_artists_2[w] #key, value
            list_artists_ordered_2.append(w)
            list_songs_ordered_2.append(dict_artists_2[w])
        print("finished printing Playlist 2s artists")

#----------------------PASS DATA TO JINJA TEMPLATE-------------------------------------------
        dict = { #dictionary that will be passed to the start_template
            "u_1": username_1,
            "text": api_text,
            "next_text": next_api_text,
            "l_artists":list_artists,
            "l_artists_o": list_artists_ordered,
            "l_songs_o": list_songs_ordered,
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
            "name_1": firstname,
            "name_2": secondname,
            }

        start_template = jinja_current_dir.get_template("templates/results.html")
        self.response.write(start_template.render(dict))

class AboutUsPage(webapp2.RequestHandler):
    def get(self):
        start_template = jinja_current_dir.get_template("templates/aboutus.html")
        self.response.write(start_template.render())

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/about-us', AboutUsPage),
    ('/final', FinalPage),
    ('/results', ResultsPage),
], debug=True)
