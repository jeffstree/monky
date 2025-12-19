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
from build_db import query_cat, query_bird, query_pokemon
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

DB_FILE="database.db"
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
app.secret_key = os.urandom(24)

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()
c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
c.execute('CREATE TABLE IF NOT EXISTS poke_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS cat_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS bird_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
db.commit()

FALLBACK_POKEMON = [
    {'name': 'pikachu', 'type_one': 'electric', 'type_two': 'No Type', 'height': 4, 'weight': 60, 'generation': 1},
    {'name': 'charizard', 'type_one': 'fire', 'type_two': 'flying', 'height': 17, 'weight': 905, 'generation': 1},
    {'name': 'bulbasaur', 'type_one': 'grass', 'type_two': 'poison', 'height': 7, 'weight': 69, 'generation': 1},
    {'name': 'squirtle', 'type_one': 'water', 'type_two': 'No Type', 'height': 5, 'weight': 90, 'generation': 1},
    {'name': 'jigglypuff', 'type_one': 'normal', 'type_two': 'fairy', 'height': 5, 'weight': 55, 'generation': 1}
]

FALLBACK_CATS = [
    {'name': 'Abyssinian', 'origin': 'Egypt', 'life_span': 15, 'intelligence': 5, 'social_needs': 5, 'weight_max': 10},
    {'name': 'Siamese', 'origin': 'Thailand', 'life_span': 15, 'intelligence': 5, 'social_needs': 5, 'weight_max': 15},
    {'name': 'Maine Coon', 'origin': 'United States', 'life_span': 14, 'intelligence': 4, 'social_needs': 4, 'weight_max': 18},
    {'name': 'Persian', 'origin': 'Iran (Persia)', 'life_span': 15, 'intelligence': 3, 'social_needs': 2, 'weight_max': 12},
    {'name': 'Ragdoll', 'origin': 'United States', 'life_span': 17, 'intelligence': 4, 'social_needs': 5, 'weight_max': 20}
]

FALLBACK_BIRDS = [
    {'name': 'Bald Eagle', 'family': 'Accipitridae', 'order': 'Accipitriformes', 'wingspan_min': 180, 'wingspan_max': 230, 'length': 102},
    {'name': 'Peregrine Falcon', 'family': 'Falconidae', 'order': 'Falconiformes', 'wingspan_min': 74, 'wingspan_max': 120, 'length': 58},
    {'name': 'Blue Jay', 'family': 'Corvidae', 'order': 'Passeriformes', 'wingspan_min': 34, 'wingspan_max': 43, 'length': 30},
    {'name': 'Northern Cardinal', 'family': 'Cardinalidae', 'order': 'Passeriformes', 'wingspan_min': 25, 'wingspan_max': 31, 'length': 23},
    {'name': 'Great Horned Owl', 'family': 'Strigidae', 'order': 'Strigiformes', 'wingspan_min': 101, 'wingspan_max': 145, 'length': 63}
]

def get_daily_target(game_type):
    today = datetime.date.today()
    seed = today.year * 10000 + today.month * 100 + today.day
    r = random.Random(seed)

    table_map = {'poke': 'poke_info', 'cat': 'cat_info', 'bird': 'bird_info'}
    table = table_map[game_type]
    
    db = get_db_connection()
    c = db.cursor()
    try:
        c.execute(f'SELECT count(*) FROM {table}')
        total = c.fetchone()[0]
        if total > 0:
            offset = r.randint(0, total - 1)
            c.execute(f'SELECT * FROM {table} LIMIT 1 OFFSET ?', (offset,))
            row = c.fetchone()
            return dict(row)
    except Exception:
        pass
    finally:
        db.close()

    fallbacks = {'poke': FALLBACK_POKEMON, 'cat': FALLBACK_CATS, 'bird': FALLBACK_BIRDS}
    return r.choice(fallbacks[game_type])

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
        user_data = (
            ("Pokemon",) + c.execute("SELECT wins, last_daily, daily_streak FROM poke_stats WHERE username=?", (user,)).fetchone(),
            ("Cat",) + c.execute("SELECT wins, last_daily, daily_streak FROM cat_stats WHERE username=?", (user,)).fetchone(),
            ("Bird",) + c.execute("SELECT wins, last_daily, daily_streak FROM bird_stats WHERE username=?", (user,)).fetchone()
        )
        print(user_data)
        db = get_db_connection()
        c = db.cursor()
        table_stats = {'poke': 'poke_stats', 'cat': 'cat_stats', 'bird': 'bird_stats'}[game_type]
        c.execute(f'SELECT last_daily FROM {table_stats} WHERE username = ?', (user,))
        row = c.fetchone()
        db.close()
        
        last_daily = row['last_daily'] if row else None
        
        if last_daily != today:
            session[target_key] = get_daily_target(game_type)
            session[is_daily_key] = True
        else:
            session[target_key] = get_random_target(game_type)
            session[is_daily_key] = False
            
        session[guesses_key] = []
        session[won_key] = False

def handle_win(game_type):
    if not session.get(f'{game_type}_is_daily'):
        return
    
    session[f'{game_type}_is_daily'] = False

    user = session['username']
    today = datetime.date.today()
    today_iso = today.isoformat()
    yesterday_iso = (today - datetime.timedelta(days=1)).isoformat()
    
    table_stats = {'poke': 'poke_stats', 'cat': 'cat_stats', 'bird': 'bird_stats'}[game_type]
    
    db = get_db_connection()
    c = db.cursor()
    c.execute(f'SELECT wins, last_daily, daily_streak FROM {table_stats} WHERE username = ?', (user,))
    row = c.fetchone()
    
    if row:
        wins = row['wins'] + 1
        last_daily = row['last_daily']
        streak = row['daily_streak']
        
        if last_daily == yesterday_iso:
            streak += 1
        else:
            streak = 1
            
        c.execute(f'UPDATE {table_stats} SET wins = ?, last_daily = ?, daily_streak = ? WHERE username = ?',
                  (wins, today_iso, streak, user))
    
    db.commit()
    db.close()




def get_db_connection():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row
    return db

def init_tables():
    db = get_db_connection()
    c = db.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS poke_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS cat_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS bird_stats (username TEXT REFERENCES users(username), wins INTEGER, last_daily DATE, daily_streak INTEGER)')
    
    db.commit()
    db.close()



def check_numeric(guess_val, target_val):
    if guess_val == target_val:
        return 'match'
    elif guess_val < target_val:
        return 'Too low'
    else:
        user_data = None
        user = "Guest"

    return render_template("home.html", user = user , user_data = user_data)

@app.route("/login", methods=['GET','POST'])
def login():
    #if already logged in
    if 'username' in session:
        if request.referrer != None:
            return redirect(request.referrer)
        return 'Too high'

def check_range(guess_val, target_min, target_max):
    if target_min <= guess_val <= target_max:
        return 'match'
    elif guess_val < target_min:
        return 'Too low'
    else:
        return 'Too high'


init_tables()

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user = session['username']
    db = get_db_connection()
    c = db.cursor()
    
    games = [('Pokemon', 'poke_stats'), ('Cat', 'cat_stats'), ('Bird', 'bird_stats')]
    user_data = []
    
    for game_name, table in games:
        c.execute(f'SELECT wins, last_daily, daily_streak FROM {table} WHERE username = ?', (user,))
        row = c.fetchone()
        if row:
            user_data.append((game_name, row['wins'], row['last_daily'], row['daily_streak']))
        else:
            return redirect(url_for('home'))
            user_data.append((game_name, 0, 'Never', 0))
            
    db.close()
    return render_template('home.html', user=user, user_data=user_data)

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
        
        db = get_db_connection()
        c = db.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        db.close()
        
        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return redirect(url_for('login'))
            
    return render_template('login.html')

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
        
        db = get_db_connection()
        c = db.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            c.execute('INSERT INTO poke_stats (username, wins, last_daily, daily_streak) VALUES (?, 0, NULL, 0)', (username,))
            c.execute('INSERT INTO cat_stats (username, wins, last_daily, daily_streak) VALUES (?, 0, NULL, 0)', (username,))
            c.execute('INSERT INTO bird_stats (username, wins, last_daily, daily_streak) VALUES (?, 0, NULL, 0)', (username,))
            db.commit()
            db.close()
            flash('Registration successful')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            db.close()
            flash('Username already exists')
            return redirect(url_for('register'))
            
    return render_template('register.html')

@app.route("/logout", methods=['GET', 'POST'])
def logout():
    if 'username' in session:
        session.pop('username')
    return redirect(request.referrer)


@app.route("/pokemon", methods=['GET', 'POST'])
@app.route("/poke_game", methods=['GET', 'POST'])
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

@app.route("/cat_game", methods=['GET', 'POST'])
def cat_game():
    target_pokemon = query_cat("pikachu")
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

@app.route("/bird_game", methods=['GET', 'POST'])
def bird_game():
    target_pokemon = query_bird("pikachu")
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
