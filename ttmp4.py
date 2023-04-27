#!/usr/bin/env python3
from flask import *
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup as Soup
from requests import get as _get
from re import match
from os.path import isfile

app = Flask(__name__)

@app.route("/")
def index():
    url = request.args.get("url")
    if not url:
        return send_from_directory("static", "index.html")
    if url.startswith("https://vm.tiktok.com/"):
        curl = Popen(["curl", url], stdout=PIPE, stderr=PIPE)
        out, err = curl.communicate()
        url = Soup(out).find("a")["href"].split("?")[0]
    if not match("https://www.tiktok.com/@\w+?/video/\d+", url):
        return "bad url"
    if url[-1] == "/":
        url = url[:-1]
    if not isfile("static/" + url.split("/")[-1] + ".mp4"):
        print(url)
        ytdl = Popen(["yt-dlp", "-S", "codec:h264", "-o", "static/%(display_id)s.%(ext)s", url], stdout=PIPE)
        out, err = ytdl.communicate()
        code = ytdl.wait()
        if code != 0:
            return "not a video url"
    return redirect(url_for("static", filename=url.split("/")[-1] + ".mp4"))

if __name__ == "__main__":
    app.run(port=51761, host="0.0.0.0")
