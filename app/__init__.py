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

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

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
#==========================================================
#KEYLOADING LIES BENEATH HERE
#==========================================================

def key_load(key_name):
    try:
        key_path = os.path.join(os.path.dirname(__file__), "keys", f"key_{key_name}.txt")
        with open (key_path, "r") as f:
            text = f.read().strip()
            if not text:
                print(f"File is empty for: {key_name}")
                return None
            print(f"Loaded key for: {key_name}")
            return text
    except Exception as exception:
        print(f"Failed to load key for {key_name}: {exception}")
        return None

cat_key = key_load("TheCatAPI")
nuthatch_key = key_load("NuthatchAPI")

def get_json(site, keys={}):
    try:
        request = urllib.request.Request(site, headers = keys)
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except Exception as exception:
        print(f"Error fetching API for {site}: {exception}")
        return None

def pokemon_parser():
    poke_num = random.randint(1,151)
    data = get_json(f"https://pokeapi.co/api/v2/pokemon/{poke_num}")
    url = data['species']['url']
    pokemon_data = get_json(url)
    if pokemon_data:
       generation = pokemon_data['generation']['name']
    else:
        generation = "generation-i"
    data_map = {"generation-i":1, "generation-ii":2, "generation-iii":3, "generation-iv":4, "generation-v":5}
    gen = data_map.get(generation)
    stats = {
        "id": data['id'],
        "name": data['name'],
        "type_one": data['types'][0]['type']['name'],
        "type_two": data['types'][1]['type']['name'] if len(data['types']) > 1 else "No Type",
        "height": data['height'] / 10.0,
        "weight": data['weight'] / 10.0,
        "generation": gen,
    }
    return stats
#==========================================================
#KEYLOADING LIES ABOVE HERE
#==========================================================


#==========================================================
#SQLITE3 DATABASE LIES BENEATH HERE
#==========================================================

'''users (username, password)'''
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)""")

'''poke_stats (username, wins, last_daily, daily_streak)'''
c.execute("""
CREATE TABLE IF NOT EXISTS poke_stats (
    username TEXT,
    wins INTEGER,
    last_daily DATE,
    daily_streak INTEGER,
    FOREIGN KEY (username) REFERENCES users(username)
)""")

'''cat_stats (username, wins, last_daily, daily_streak)'''
c.execute("""
CREATE TABLE IF NOT EXISTS cat_stats (
    username TEXT,
    wins INTEGER,
    last_daily DATE,
    daily_streak INTEGER,
    FOREIGN KEY (username) REFERENCES users(username)
)""")

'''bird_stats (username, wins, last_daily, daily_streak)'''
c.execute("""
CREATE TABLE IF NOT EXISTS bird_stats (
    username TEXT,
    wins INTEGER,
    last_daily DATE,
    daily_streak INTEGER,
    FOREIGN KEY (username) REFERENCES users(username)
)""")

'''bird_info (id, name, family, order, status, wingspan_min, wingspan_max, length_min, length_max)'''
c.execute("""
CREATE TABLE IF NOT EXISTS bird_info (
    id INTEGER PRIMARY KEY,
    name TEXT,
    family TEXT,
    "order" TEXT,
    status TEXT,
    wingspan_min INTEGER,
    wingspan_max INTEGER,
    length_min INTEGER,
    length_max INTEGER
)""")

'''
cat_info(id, name, origin, life_span, intelligence, social_needs, weight_min, weight_max)
Cat returns "weight":{"imperial":"7  -  10","metric":"3 - 5"}, extract the imperial and use the upper and lower as weight min and max.
Cat returns "life_span":"14 - 15", use upper value
'''
c.execute("""
CREATE TABLE IF NOT EXISTS cat_info (
    id TEXT PRIMARY KEY,
    name TEXT,
    origin TEXT,
    life_span INTEGER,
    intelligence INTEGER,
    social_needs INTEGER,
    weight_min INTEGER,
    weight_max INTEGER
)""")

'''poke_info(id, name, type_one, type_two, height, weight, generation)'''
c.execute("""
CREATE TABLE IF NOT EXISTS poke_info (
    id INTEGER PRIMARY KEY,
    name TEXT,
    type_one TEXT,
    type_two TEXT,
    height INTEGER,
    weight INTEGER,
    generation INTEGER
)""")

# Height and Weight are divided by 10
# Generation is returned as

# name:"generation-iv"
# url:"https://pokeapi.co/api/v2/generation/4/"

# need to grab the generation number from the url.


#==========================================================
#SQLITE3 DATABASE LIES ABOVE HERE
#==========================================================

db.commit() #save changes

if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()

db.close()  #close database
