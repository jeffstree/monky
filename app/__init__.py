# Jiefeng Ou, Wesley Leon, Alexandru Cimpoiesu
# monky
# SoftDev
# P01: ArRESTed Development

from flask import Flask, render_template, request
import sqlite3

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
    print(username, password)
    return render_template("login.html");

@app.route("/register", methods=['GET','POST'])
def register():
    return render_template("register.html");


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
