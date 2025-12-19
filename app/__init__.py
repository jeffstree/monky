# Jiefeng Ou, Wesley Leon, Alexandru Cimpoiesu
# monky
# SoftDev
# P01: ArRESTed Development

from flask import *
import sqlite3
import os
import urllib
import json
import random
from build_db import query_cat, query_bird, query_pokemon
app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_FILE="database.db"

def db_connect():
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    return db
#c = db.cursor()
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS poke_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS cat_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS bird_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
db.commit()

@app.route("/poke", methods=['GET', 'POST'])
def poke():
    return render_template("poke.html")

@app.route("/cat", methods=['GET', 'POST'])
def cat():
    return render_template("cat.html")

@app.route("/bird", methods=['GET', 'POST'])
def bird():
    return render_template("bird.html")

@app.route("/")
def home():
    if 'username' in session:
        user = session['username']
        print(c.execute("SELECT * FROM cat_stats WHERE username=?", (user,)))
        pokedata = c.execute("SELECT * FROM poke_stats WHERE username=?", (user,)).fetchone()
        catdata = c.execute("SELECT * FROM cat_stats WHERE username=?", (user,)).fetchone()
        birddata = c.execute("SELECT * FROM bird_stats WHERE username=?", (user,)).fetchone()
    else:
        user = "Guest"
        pokedata = None
        catdata = None
        birddata = None

    return render_template("home.html", user = user, pokedata = pokedata, catdata = catdata, birddata = birddata)

@app.route("/login", methods=['GET','POST'])
def login():
    #if already logged in
    if 'username' in session:
        if request.referrer != None:
            return redirect(request.referrer)
        else:
            return redirect(url_for('home'))

    #if info given
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if not user:
            error = "Invalid username or password!"
            return render_template('login.html', error=error)

        session['username'] = username
        return redirect(url_for('home'))

    return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    #if already logged in
    if 'username' in session:
        if request.referrer != None:
            return redirect(request.referrer)
        else:
            return redirect(url_for('home'))

    #if info given
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if " " in username:
            return render_template("register.html", error = "Username cannot contain spaces!")
        if username == "Guest":
            return render_template("register.html", error = "Username not allowed!")
        if c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone():
            return render_template("register.html", error = "Username already exists!")

        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        c.execute("INSERT OR REPLACE INTO cat_stats (username, wins, last_daily, daily_streak) VALUES (?, ?, ?, ?)", (username, 0, None, 0))
        c.execute("INSERT OR REPLACE INTO poke_stats (username, wins, last_daily, daily_streak) VALUES (?, ?, ?, ?)", (username, 0, None, 0))
        c.execute("INSERT OR REPLACE INTO bird_stats (username, wins, last_daily, daily_streak) VALUES (?, ?, ?, ?)", (username, 0, None, 0))
        session['username'] = username

        return redirect(url_for('home'))

    return render_template("register.html")

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(request.referrer)


@app.route("/pokemon", methods=['GET', 'POST'])
def pokemon_game():
    target_pokemon = query_pokemon("pikachu")
    win = False
    if request.method == "POST":
        guess = request.form['guess'].lower().strip()
        stats = query_pokemon(guess)
        print(stats)
        print("-------------------")
        print(target_pokemon)
        if stats:
            if stats[1] == target_pokemon[1]:
                win = True
            feedback = {
                "name": stats[1],
                "type_one": "match" if stats[2] == target_pokemon[2] else "no",
                "type_two": "match" if stats[3] == target_pokemon[3] else "no",
                "height": "match" if stats[4] == target_pokemon[4] else
                    ("higher" if target_pokemon[4] > stats[4] else "lower"),
                "weight": "match" if stats[5] == target_pokemon[5] else
                    ("higher" if target_pokemon[5] > stats[5] else "lower"),
                "generation": "match" if stats[6] == target_pokemon[6] else
                    ("higher" if target_pokemon[6] > stats[6] else "lower")
            }
        else:
            feedback = "not "
    return render_template("poke.html", target=target_pokemon[1] if win else None, feedback=feedback, won=win,)



#==========================================================
#SQLITE3 DATABASE LIES ABOVE HERE
#==========================================================

db.commit() #save changes

if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()

db.close()  #close database
