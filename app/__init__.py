# Jiefeng Ou, Wesley Leon, Alexandru Cimpoiesu
# monky
# SoftDev
# P01: ArRESTed Development

from flask import *
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

@app.route("/")
def home():
    if'username' in session:
        return render_template("home.html", user = session['username'])
    return render_template("home.html", user = "Guest")

@app.route("/login", methods=['GET','POST'])
def login():
    #if already logged in
    if 'username' in session:
        return redirect(request.referrer)

    #if info given
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        user = c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if not user:
            error = "Invalid username or password!"
            return render_template('login.html', error=error)

        session['username'] = username
        db.commit()
        return redirect(url_for('home'))

    return render_template("login.html")

@app.route("/register", methods=['GET','POST'])
def register():
    #if already logged in
    if 'username' in session:
        return redirect(request.referrer)

    #if info given
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        if("SELECT exists(SELECT 1 FROM users WHERE username = ?)", (username)):
            return render_template("register.html", error = "Username already exists!")
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
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

c.execute("""
CREATE TABLE IF NOT EXISTS cat_info (
    id TEXT PRIMARY KEY,
    name TEXT,
    origin TEXT, -- Corrected typo from 'orgin'
    life_span INTEGER,
    inteligence INTEGER,
    social_needs INTEGER,
    weight_min INTEGER,
    weight_max INTEGER
)""")

'''
 Cat returns "weight":{"imperial":"7  -  10","metric":"3 - 5"}, extract the imperial and use the upper and lower as weight min and max.
 Cat returns "life_span":"14 - 15", use upper value
'''

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
