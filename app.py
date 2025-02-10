from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
import sqlite3
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os

load_dotenv()
        
cid = os.getenv("CID")
secret = os.getenv("SECRET")
<<<<<<< HEAD
=======
print(cid)
print(secret)
>>>>>>> 7a2670e (Initial Commit)

app = Flask(__name__)
db = sqlite3.connect("music.db", check_same_thread=False)
db.execute("PRAGMA foreign_keys = ON")
cursor = db.cursor()
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=cid,
                                               client_secret=secret,
                                               redirect_uri="http://localhost:3000",
                                               scope="user-library-read"))

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

previous_genrechoice = None
songlist = []

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

class SearchForm(FlaskForm):
    q = StringField('q', validators=[DataRequired()])

class PageResult:
   def __init__(self, data, page = 1, number = 20):
     self.__dict__ = dict(zip(['data', 'page', 'number'], [data, page, number]))
     self.full_listing = [self.data[i:i+number] for i in range(0, len(self.data), number)]
   def __iter__(self):
     for i in self.full_listing[self.page-1]:
       yield i
   def __repr__(self): #used for page linking
     return "/{}".format(self.page+1) #view the next page

@app.route("/")
@login_required
def root():
    return redirect(url_for("index"))

@app.route("/index", methods=["GET","POST"])
def index():
    cursor.execute("SELECT genre FROM genres")
    genre = cursor.fetchall()
    genrelist = [str(x[0]) for x in genre]
    
    genrechoice = request.args.get("genreselect")  # Get the selected genre from the dropdown
    print("Genre:", genrechoice)
    songs = []
    items = []

    page = request.args.get('page', 1, type=int)  # Get the page number from the query parameter
    per_page = 20  # Number of items per page
    offset = (page - 1) * per_page  # Calculate the offset based on the page number

    # Get the search results for the current page
    result = sp.search(q="genre: {genre}".format(genre=genrechoice), type="track", limit=per_page, offset=offset)
    items = result['tracks']['items']

    for i in items:
        if i["name"] not in songs:
            songs.append(i["name"])

    total_songs = result['tracks']['total']  # Calculate total songs
    total_pages = (total_songs // per_page) + (1 if total_songs % per_page > 0 else 0)  # Calculate total pages

    cursor.execute("SELECT name FROM playlists WHERE user_id = ?", (session["user_id"],))
    playlists = [x[0] for x in cursor.fetchall()]

    return render_template("index.html", genrelist=genrelist, songs=songs, page=page, total_pages=total_pages, playlists=playlists)

@app.route("/playlist", methods=["GET","POST"])
@login_required
def playlist():
    cursor.execute("SELECT name FROM playlists WHERE user_id = ?", (session["user_id"],))
    playlists = []
    temp = cursor.fetchall()
    for x in temp:
        playlists.append(''.join(x))
    return render_template("playlist.html", playlists=playlists)

@app.route("/create_playlist", methods=["GET","POST"])
@login_required
def create_playlist():
    if request.method == "POST":
        name = request.form.get("playlist_name")
        check = list(cursor.execute("SELECT name FROM playlists WHERE user_id = ? AND name = ?", (session["user_id"], name)))
        if len(check) > 0:
            flash("Playlist already exists", "warning")
            return render_template("create_playlist.html")
        else:
            cursor.execute("INSERT INTO playlists (user_id, name) VALUES (?, ?)", (session["user_id"], name))
            db.commit()
            flash("Playlist successfully added", "success")
            return redirect("/playlist")
    return render_template("create_playlist.html")

@app.route("/add_song_to_playlist", methods=["POST"])
@login_required
def add_song_to_playlist():
    data = request.get_json()

    song = data.get('song')
    playlist = data.get('playlist')

    if not song or not playlist:
        return jsonify({'success': False, 'message': 'Missing song or playlist data.'})

    cursor.execute("SELECT id FROM playlists WHERE user_id = ? AND name = ?", (session["user_id"], playlist))
    playlist = cursor.fetchone()

    if playlist:
        playlist_id = playlist[0]
        cursor.execute("SELECT * FROM songs WHERE playlist_id = ? AND name = ? AND user_id = ?", (playlist_id, song, session["user_id"]))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute("INSERT INTO songs (playlist_id, user_id, name) VALUES (?, ?, ?)", (playlist_id, session["user_id"], song))
            db.commit()
            return {"status": "success", "message": "Song successfully added to playlist"}
        else:
            return {"status": "error", "message": "Song already in the playlist"}
    return {"status": "error", "message": "Playlist not found!"}

@app.route("/playlist/<playlist_name>", methods=["GET"])
@login_required
def playlist_songs(playlist_name):
    cursor.execute("SELECT id FROM playlists WHERE user_id = ? AND name = ?", (session["user_id"], playlist_name))
    playlist = cursor.fetchone()

    if not playlist:
        flash("Playlist not found", "danger")
        return redirect("/playlist")

    playlist_id = playlist[0]
    cursor.execute("SELECT name FROM songs WHERE playlist_id = ? AND user_id = ?", (playlist_id, session["user_id"]))
    songs = [row[0] for row in cursor.fetchall()]

    return render_template("playlist_songs.html", playlist_name=playlist_name, songs=songs)

@app.route("/delete_playlist", methods=["POST"])
@login_required
def delete_playlist():
    playlist_name = request.args.get("playlist_name")
    print(playlist_name)
    cursor.execute("SELECT id FROM playlists WHERE user_id = ? AND name = ?", (session["user_id"], playlist_name))
    playlist = cursor.fetchone()

    if not playlist:
        flash("Playlist not found", "danger")
        return redirect("/playlist")
    
    cursor.execute("DELETE FROM playlists WHERE id = ? AND user_id = ?", (playlist[0], session["user_id"]))
    db.commit()
    return redirect("/playlist")

@app.route("/delete_song", methods=["GET", "POST"])
@login_required
def delete_song():
    song_name = request.args.get("song_name")
    playlist_name = request.args.get("playlist")
    print(song_name)
    cursor.execute("SELECT id FROM playlists WHERE user_id = ? AND name = ?", (session["user_id"], playlist_name))
    playlist = cursor.fetchone()
    cursor.execute("SELECT id FROM songs WHERE user_id = ? AND playlist_id = ? AND name = ?", (session["user_id"], playlist[0], song_name))
    song = cursor.fetchone()

    cursor.execute("DELETE FROM songs WHERE id = ? AND user_id = ? AND playlist_id = ?", (song[0], session["user_id"], playlist[0]))
    db.commit()
    return redirect(("/playlist/"+playlist_name))

@app.route("/register", methods=["GET","POST"])
def register():
        #Clears leftover user_id from cache
    session.clear()
    if request.method == "POST":
        if not request.form.get("username") or not request.form.get("password") or not request.form.get("confirmation"):
            flash("Invalid: Missing Fields", "danger")
            return render_template("register.html")
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirmation")

        cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
        check = cursor.fetchall()
        if len(check) > 0:
            flash("Error: Username must be unique", "danger")
            return render_template("register.html")
        if password != confirm:
            flash("Error: Passwords must match", "danger")
            return render_template("register.html")

        cursor.execute("INSERT INTO users(username, password) VALUES (?, ?)", (username, generate_password_hash(password)))
        db.commit()
        return redirect("/")
    else:
        return render_template('register.html')

@app.route("/login", methods=["GET","POST"])
def login():
    #Clears leftover user_id from cache
    session.clear()
    #get login input from page
    if request.method == "POST":
        if not request.form.get("username"):
            flash("Error: No Username Found", "danger")
            return render_template("login.html")

        elif not request.form.get("password"):
            flash("Error: No Password Found", "danger")
            return render_template("login.html")
        
        user = list(cursor.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),)))

        #check if username exists in db
        if len(user) != 1 or not check_password_hash(user[0][2], request.form.get("password")) != True:
            flash("Duplicate Username/Password", "danger")
            return render_template("login.html")
            
        else:
            session["user_id"] = user[0][0]
            flash("Success: Login Successful", "success")
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Success: Logged out", "Success")
    return redirect("/")

if __name__ == '__main__':
    app.run()