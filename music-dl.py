# Downloads music from YouTube, with the help of youtube-dl

import requests
from lxml import html

# from ColorPython import pprint
import sys
import jsonpath
import re
from ColorPython import pprint
import pyperclip
import subprocess

session = requests.Session()

SEARCH_URL = "https://www.youtube.com/results?search_query={}&pbj=1"
query = "+".join(sys.argv[1:])

# The Default Headers Structure as retrieved from the Browser Network Tab
headers = {
    "authority": "www.youtube.com",
    "method": "GET",
    "path": "/results?search_query=Selena+Gomez&pbj=1",
    "scheme": "https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cookie": "YSC=pX1wriYqdUk; PREF=f1=50000000; VISITOR_INFO1_LIVE=RIzYnvypwUA; GPS=1; ST-149uald=oq=Selena%20Gomez&gs_l=youtube.12...0.0.4.91178.0.0.0.0.0.0.0.0..0.0....0...1ac..64.youtube..0.0.0....0.wPO2j0iriHg&feature=web-masthead-search&itct=CC8Q7VAiEwi005XhjbzjAhVVE7cAHbyWDh8ojh4%3D&csn=DSkvXfSYC9Wm3LUPvK26-AE",
    "referer": "https://www.youtube.com/",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
    "x-client-data": "CMisygE=",
    "x-spf-previous": "https://www.youtube.com/",
    "x-spf-referer": "https://www.youtube.com/",
    "x-youtube-ad-signals": "dt=1563371562443&flash=0&frm&u_tz=330&u_his=17&u_java&u_h=768&u_w=1366&u_ah=768&u_aw=1366&u_cd=24&u_nplug&u_nmime&bc=31&bih=238&biw=1351&brdim=0%2C23%2C0%2C23%2C1366%2C0%2C1366%2C745%2C1366%2C238&vis=1&wgl=true&ca_type=image",
    "x-youtube-client-name": "1",
    "x-youtube-client-version": "2.20190716",
    "x-youtube-page-cl": "258186736",
    "x-youtube-page-label": "youtube.ytfe.desktop_20190715_4_RC0",
    "x-youtube-sts": "18092",
    "x-youtube-utc-offset": "330",
    "x-youtube-variants-checksum": "36d09dd54f6181aa90df58b067fee2e3",
}


# By Default, youtube will return the JSON encoded response in 'br' encoding, that will be of no use to us
headers.update({"accept-encoding": "gzip"})

# response will a JSON response
def search_youtube(query):
    response = session.get(SEARCH_URL.format(query), headers=headers)

    # Now, the response i got should have this
    assert (
        response.headers["content-encoding"] == "gzip"
    ), "Content Encoding not returned in gzip"

    # assert 'videoRenderer' in response.json()

    data = dict(response.json()[1])

    # print (data)
    videos = jsonpath.jsonpath(data, "$..videoRenderer")

    # Fetching details of every video

    """
    info : A dictionary that will take account of all the data
        - count: will be it's key
        - all other data would be given in a dict with informative keys

        like,
            info = {
                        1: {'title': 'Title A', 'videoID': 'adsfasf', 'views': '600 M'},
                        2: {'title': 'Title B', 'videoID': 'adffdsf', 'views': '2 B'}
                    }
    """
    print(pprint("green", "bold", "Choose from the following: "))
    info = {}
    count = 1
    for video in videos:
        title = jsonpath.jsonpath(video, "$..title..text")
        views = jsonpath.jsonpath(video, "$..shortViewCountText..simpleText")
        videoID = jsonpath.jsonpath(video, "$..videoId")
        length = jsonpath.jsonpath(video, "$..lengthText..simpleText")
        # title = video['title']['runs'][0]['text']
        assert len(videoID) != 0 and len(title) != 0 and len(views) > 0
        assert len(length) != 0

        try:
            views = " ".join(re.match(r"(\d+\.*\d*)([A-Z])", views[0]).groups())
        except Exception:
            views = views[0]
        title, videoID, length = title[0], videoID[0], length[0]

        info[count] = {
            "title": title,
            "videoID": videoID,
            "views": views,
            "length": length,
            "url": f"https://www.youtube.com/watch?v={videoID}&pbj=1",
        }

        print(
            f"[{count:<2}] {pprint('yellow', 'normal', title)} ({pprint('cyan', 'normal', views):<10}) ({length})"
        )
        count += 1
    return info


def input_choice():
    choice = input(" Choice >> ")
    if choice == "quit":
        choice = -1
    else:
        try:
            choice = int(choice)
        except ValueError:
            print(f"Invalid Input... Try Again ....")
            return input_choice()
    return choice


# Starting with the First Download

# info = search_youtube (query)
# choice = input_choice()
# if choice == -1:
# print ("Thank You for using....")
# sys.exit (1)
# # print (f"Video URL: {pprint('red', 'bold', info[choice]['url'])}")
# video_url = info[choice]['url']
# pyperclip.copy (video_url)
#
# download_process = subprocess.run (f'youtube-dl --embed-thumbnail -f m4a {video_url}'.split(' '))

# After the 1st download is complete, prompt the user for further actions
def input_query():
    query = input(pprint("red", "bold", "[YouTube Search]") + ": ")
    return query


while True:
    if len(query) == 0:
        query = input_query()
    if query == "quit":
        break
    info = search_youtube(query)
    choice = input_choice()
    if choice == -1:
        break
    video_url = info[choice]["url"]

    file_name = re.sub("(\(|\[).*(\)|\])", "", info[choice]["title"])
    file_name = file_name.strip()
    parts = file_name.split("-")
    file_name = "-".join(map(str.strip, parts))
    print(f"Title: {file_name}")
    # subprocess.run (f'youtube-dl --add-metadata --embed-thumbnail -f m4a {video_url} -o {file_name.replace(" ", "_")}.m4a'.split(' '))
    subprocess.run(
        f'youtube-dl -f m4a {video_url} -o {file_name.replace(" ", "_")}.m4a'.split(" ")
    )
    query = ""


print(f"Thank You for using the tool.....")
# import os
# os.system (f"youtube-dl --add-metadata -f bestaudio {video_url}")

# ########## Shit Code ######################{{{
# r2 = session.get (video_url, headers=headers)
#
# new_data = r2.json()
# links = jsonpath.jsonpath (new_data, '$..url_encoded_fmt_stream_map')
#
# # print (f"length of links: {len(links)}")
# from urllib import parse
# import pyperclip
#
# dlink = links[0].split('url=')[-1]
# dlink = parse.unquote (dlink)
#
# pyperclip.copy (dlink)
#
# dres = session.get (dlink, stream=True)
# print ("Download Init...")
# with open ("Download.mp4", 'wb') as file:
# for data in dres.iter_content (chunk_size=128*1024):
# file.write (data)
# print ("Downloading ....", end='\r')
#
# print ("Download Complete")
# # print (dlink)
# ########## Shit Code ######################}}}
