#!/usr/bin/env python3
# set CDN_PATH to url path to cdn and REMOTE_PATH to rsync path to same directory
from urllib.parse import urljoin
from flask import *
from subprocess import Popen, PIPE
from bs4 import BeautifulSoup as Soup
from requests import get as _get
from re import match
from os import getenv
from os.path import isfile
from secrets import token_urlsafe

app = Flask(__name__)
app.secret_key = token_urlsafe(16)

@app.endpoint('static')
def static(filename):
    if filename[-5:] == ".webp":
        return app.send_static_file(filename)
    test = _get(urljoin(getenv("CDN_PATH"), filename))
    if test:
        return redirect(urljoin(getenv("CDN_PATH"), filename))
    return app.send_static_file(filename)

@app.route("/")
def index():
    url = request.args.get("url", "").split("?")[0]
    if not url:
        listing = Popen(["bash", "-c", "ls -tc static/*.webp"], stdout=PIPE)
        out, err = listing.communicate()
        out = out.decode("utf-8").strip()
        return render_template("index.html", listing=[l[:-5] for l in out.split()][:100], thumbs="thumbs" in request.args)
    if not match("^https?://([a-z0-9]+[.])*tiktok.com", url):
        flash(f"not a tiktok.com url")
        return redirect(url_for("index"))
    url = _get(url).url.split("?",1)[0]
    if not match("https://www.tiktok.com/@[a-zA-Z0-9\._]+?/video/\d+", url):
        flash(f"bad url acquired after resolving redirects: {url}")
        return redirect(url_for("index"))
    if url[-1] == "/":
        url = url[:-1]
    if not isfile("static/" + url.split("/")[-1] + ".mp4"):
        print(url)
        ytdl = Popen(["yt-dlp", "-S", "codec:h264", "-o", "static/%(display_id)s.%(ext)s", "--write-thumbnail", url], stdout=PIPE)
        out, err = ytdl.communicate()
        code = ytdl.wait()
        if code != 0:
            flash("not a video url")
            return redirect(url_for("index"))
        rsync = Popen(["rsync", "-vaP", "static/", getenv("REMOTE_PATH")])
        code = ytdl.wait()
    return redirect(url_for("static", filename=url.split('/')[-1] + ".mp4"))

if __name__ == "__main__":
    app.run(port=51761, host="0.0.0.0")
