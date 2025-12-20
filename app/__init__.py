
import sqlite3
from flask import Flask, render_template, request, session, redirect, url_for, flash, jsonify
import os
import datetime
import sys
import random
from build_db import query_cat, query_bird, query_pokemon
import datetime

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

def get_random_target(game_type):
    table_map = {'poke': 'poke_info', 'cat': 'cat_info', 'bird': 'bird_info'}
    table = table_map[game_type]
    
    db = get_db_connection()
    c = db.cursor()
    try:
        c.execute(f'SELECT * FROM {table} ORDER BY RANDOM() LIMIT 1')
        row = c.fetchone()
        if row:
            return dict(row)
    except Exception:
        pass
    finally:
        db.close()
        
    fallbacks = {'poke': FALLBACK_POKEMON, 'cat': FALLBACK_CATS, 'bird': FALLBACK_BIRDS}
    return random.choice(fallbacks[game_type])


def initialize_game_session(game_type):
    if 'username' not in session:
        return
    
    today = datetime.date.today().isoformat()

    if session.get('session_day') != today:
        keys_to_reset = [
            'poke_target', 'poke_guesses', 'poke_won', 'poke_is_daily',
            'cat_target', 'cat_guesses', 'cat_won', 'cat_is_daily',
            'bird_target', 'bird_guesses', 'bird_won', 'bird_is_daily'
        ]
        for k in keys_to_reset:
            session.pop(k, None)
        session['session_day'] = today

    target_key = f'{game_type}_target'
    is_daily_key = f'{game_type}_is_daily'
    won_key = f'{game_type}_won'
    guesses_key = f'{game_type}_guesses'

    if target_key not in session:
        user = session['username']
        db = get_db_connection()
        c = db.cursor()
        table_stats = {'poke': 'poke_stats', 'cat': 'cat_stats', 'bird': 'bird_stats'}[game_type]
        c.execute(f'SELECT last_daily FROM {table_stats} WHERE username = ?', (user,))
        row = c.fetchone()
        db.close()

    fallbacks = {'poke': FALLBACK_POKEMON, 'cat': FALLBACK_CATS, 'bird': FALLBACK_BIRDS}
    return r.choice(fallbacks[game_type])

def get_random_target(game_type):
    table_map = {'poke': 'poke_info', 'cat': 'cat_info', 'bird': 'bird_info'}
    table = table_map[game_type]
    
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

def check_numeric(guess_val, target_val):
    if guess_val == target_val:
        return 'match'
    elif guess_val < target_val:
        return 'Too low'
    else:
        return 'Too high'

def check_range(guess_val, target_min, target_max):
    if target_min <= guess_val <= target_max:
        return 'match'
    elif guess_val < target_min:
        return 'Too low'
    else:
        return 'Too high'

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
            return dict(row)
    except Exception:
        pass
    finally:
        db.close()
        
    fallbacks = {'poke': FALLBACK_POKEMON, 'cat': FALLBACK_CATS, 'bird': FALLBACK_BIRDS}
    return random.choice(fallbacks[game_type])


def initialize_game_session(game_type):
    if 'username' not in session:
        return
    
    today = datetime.date.today().isoformat()

    if session.get('session_day') != today:
        keys_to_reset = [
            'poke_target', 'poke_guesses', 'poke_won', 'poke_is_daily',
            'cat_target', 'cat_guesses', 'cat_won', 'cat_is_daily',
            'bird_target', 'bird_guesses', 'bird_won', 'bird_is_daily'
        ]
        for k in keys_to_reset:
            session.pop(k, None)
        session['session_day'] = today

    target_key = f'{game_type}_target'
    is_daily_key = f'{game_type}_is_daily'
    won_key = f'{game_type}_won'
    guesses_key = f'{game_type}_guesses'

    if target_key not in session:
        user = session['username']
        user_data = (
            ("Pokemon",) + c.execute("SELECT wins, last_daily, daily_streak FROM poke_stats WHERE username=?", (user,)).fetchone(),
            ("Cat",) + c.execute("SELECT wins, last_daily, daily_streak FROM cat_stats WHERE username=?", (user,)).fetchone(),
            ("Bird",) + c.execute("SELECT wins, last_daily, daily_streak FROM bird_stats WHERE username=?", (user,)).fetchone()
        )
        print(user_data)
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
        else:
            user_data.append((game_name, 0, 'Never', 0))
            
    db.close()
    return render_template('home.html', user=user, user_data=user_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
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

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/poke')
def poke():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    initialize_game_session('poke')
    
    guesses = session.get('poke_guesses', [])
    won = session.get('poke_won', False)
    target = session.get('poke_target')
    
    return render_template('poke.html', guesses=reversed(guesses), won=won, target=target)


@app.route('/pokemon_game', methods=['POST'])
def pokemon_game():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    guess_name = request.form['guess'].lower().strip()
    
    if 'poke_target' not in session:
        return redirect(url_for('poke'))

    target = session['poke_target']

    guessed_data = build_db.query_pokemon(guess_name)
    if not guessed_data:
        flash('Pokemon not found!')
        return redirect(url_for('poke'))

    guessed_stats = {
        'name': guessed_data[1],
        'type_one': guessed_data[2],
        'type_two': guessed_data[3],
        'height': guessed_data[4],
        'weight': guessed_data[5],
        'generation': guessed_data[6]
    }
    
    feedback = {
        'name': {'val': guessed_stats['name'], 'status': 'match'},
        'type_one': {'val': guessed_stats['type_one'], 'status': 'match' if guessed_stats['type_one'] == target['type_one'] else 'no_match'},
        'type_two': {'val': guessed_stats['type_two'], 'status': 'match' if guessed_stats['type_two'] == target['type_two'] else 'no_match'},
        'height': {'val': guessed_stats['height'], 'status': check_numeric(guessed_stats['height'], target['height'])},
        'weight': {'val': guessed_stats['weight'], 'status': check_numeric(guessed_stats['weight'], target['weight'])},
        'generation': {'val': guessed_stats['generation'], 'status': check_numeric(guessed_stats['generation'], target['generation'])}
    }
    
    guesses = session.get('poke_guesses', [])
    guesses.append(feedback)
    session['poke_guesses'] = guesses
    
    if guessed_stats['name'] == target['name']:
        session['poke_won'] = True
        handle_win('poke')
        
    return redirect(url_for('poke'))

@app.route('/cat')
def cat():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    initialize_game_session('cat')
    
    guesses = session.get('cat_guesses', [])
    won = session.get('cat_won', False)
    target = session.get('cat_target')
    
    return render_template('cat.html', guesses=reversed(guesses), won=won, target=target)


@app.route('/cat_game', methods=['POST'])
def cat_game():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    guess_name = request.form['guess'].strip()
    
    if 'cat_target' not in session:
        return redirect(url_for('cat'))

    target = session['cat_target']

    guessed_data = build_db.query_cat(guess_name)
    if not guessed_data:
        flash('Cat breed not found!')
        return redirect(url_for('cat'))

    guessed_stats = {
        'name': guessed_data[1],
        'origin': guessed_data[2],
        'life_span': guessed_data[3],
        'intelligence': guessed_data[4],
        'social_needs': guessed_data[5],
        'weight_max': guessed_data[7]
    }
    
    feedback = {
        'name': {'val': guessed_stats['name'], 'status': 'match'},
        'origin': {'val': guessed_stats['origin'], 'status': 'match' if guessed_stats['origin'] == target['origin'] else 'no_match'},
        'life_span': {'val': guessed_stats['life_span'], 'status': check_numeric(guessed_stats['life_span'], target['life_span'])},
        'intelligence': {'val': guessed_stats['intelligence'], 'status': check_numeric(guessed_stats['intelligence'], target['intelligence'])},
        'social_needs': {'val': guessed_stats['social_needs'], 'status': check_numeric(guessed_stats['social_needs'], target['social_needs'])},
        'weight_max': {'val': guessed_stats['weight_max'], 'status': check_numeric(guessed_stats['weight_max'], target['weight_max'])}
    }
    
    guesses = session.get('cat_guesses', [])
    guesses.append(feedback)
    session['cat_guesses'] = guesses
    
    if guessed_stats['name'] == target['name']:
        session['cat_won'] = True
        handle_win('cat')
        
    return redirect(url_for('cat'))


@app.route('/bird')
def bird():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    initialize_game_session('bird')
    
    guesses = session.get('bird_guesses', [])
    won = session.get('bird_won', False)
    target = session.get('bird_target')
    
    return render_template('bird.html', guesses=reversed(guesses), won=won, target=target)


@app.route('/bird_game', methods=['POST'])
def bird_game():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    guess_name = request.form['guess'].strip()
    
    if 'bird_target' not in session:
        return redirect(url_for('bird'))

    target = session['bird_target']

    guessed_data = build_db.query_bird(guess_name)
    if not guessed_data:
        flash('Bird not found!')
        return redirect(url_for('bird'))

    guessed_stats = {
        'name': guessed_data[1],
        'family': guessed_data[2],
        'order': guessed_data[3],
        'wingspan': guessed_data[5],
        'length': guessed_data[7]
    }
    
    feedback = {
        'name': {'val': guessed_stats['name'], 'status': 'match'},
        'family': {'val': guessed_stats['family'], 'status': 'match' if guessed_stats['family'] == target['family'] else 'no_match'},
        'order': {'val': guessed_stats['order'], 'status': 'match' if guessed_stats['order'] == target['order'] else 'no_match'},
        'wingspan': {'val': guessed_stats['wingspan'], 'status': check_range(guessed_stats['wingspan'], target['wingspan_min'], target['wingspan_max'])},
        'length': {'val': guessed_stats['length'], 'status': check_numeric(guessed_stats['length'], target['length'])}
    }
    
    guesses = session.get('bird_guesses', [])
    guesses.append(feedback)
    session['bird_guesses'] = guesses
    
    if guessed_stats['name'] == target['name']:
        session['bird_won'] = True
        handle_win('bird')
        
    return redirect(url_for('bird'))


if __name__ == "__main__": #false if this file imported as module
    app.debug = True  #enable PSOD, auto-server-restart on code chg
    app.run()
