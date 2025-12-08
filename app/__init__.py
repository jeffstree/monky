# Jiefeng Ou, Wesley Leon, Alexandru Cimpoiesu
# monky
# SoftDev
# P01: ArRESTed Development

from flask import *
import sqlite3
import os

app = Flask(__name__)

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET','POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    return render_template("login.html");

@app.route("/register", methods=['GET','POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password));
    return render_template("register.html");
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

#users (username, password)
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)""")

#poke_stats (username, wins, last_daily, daily_streak)
c.execute("""
CREATE TABLE IF NOT EXISTS poke_stats (
    username TEXT,
    wins INTEGER,
    last_daily DATE,
    daily_streak INTEGER,
    FOREIGN KEY (username) REFERENCES users(username)
)""")

#cat_stats (username, wins, last_daily, daily_streak)
c.execute("""
CREATE TABLE IF NOT EXISTS cat_stats (
    username TEXT,
    wins INTEGER,
    last_daily DATE,
    daily_streak INTEGER,
    FOREIGN KEY (username) REFERENCES users(username)
)""")

#bird_stats (username, wins, last_daily, daily_streak)
c.execute("""
CREATE TABLE IF NOT EXISTS bird_stats (
    username TEXT,
    wins INTEGER,
    last_daily DATE,
    daily_streak INTEGER,
    FOREIGN KEY (username) REFERENCES users(username)
)""")

#==========================================================
#SQLITE3 DATABASE LIES ABOVE HERE
#==========================================================

db.commit() #save changes

if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()

db.close()  #close database
