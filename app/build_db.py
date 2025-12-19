# Jiefeng Ou, Wesley Leon, Alexandru Cimpoiesu
# monky
# SoftDev
# P01: ArRESTed Development

import requests
import sqlite3
import time
import random
import urllib
import json
import os
DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()
#==========================================================
#SQLITE3 DATABASE LIES BENEATH HERE
#==========================================================


'''bird_info (id, name, family, order, wingspan_min, wingspan_max, length_min, length_max)'''
c.execute("""
CREATE TABLE IF NOT EXISTS bird_info (
    id INTEGER PRIMARY KEY,
    name TEXT,
    family TEXT,
    "order" TEXT,
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
db.commit()

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
def get_json(site, keys={}):
    try:
        request = urllib.request.Request(site, headers = keys)
        with urllib.request.urlopen(request) as response:
            return json.load(response)
    except Exception as exception:
        print(f"Error fetching API for {site}: {exception}")
        return None

def fetch_bird_data():
    nuthatch_key = key_load("NuthatchAPI")
    API_BASE_URL = "https://nuthatch.lastelm.software"
    API_ENDPOINT = "/v2/birds"
    birds_data = []
    page = 1
    page_max = 30

    headers = {
        "API-Key": nuthatch_key
    }
    while page < page_max:
        params = {"page": page}

        try:
            url = f"{API_BASE_URL}{API_ENDPOINT}"
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            birds_page = data.get("entities", [])
            birds_data.extend(birds_page)
            page +=1
            time.sleep(0.01)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API request: {e}")
            break

    insert_query = """
    INSERT INTO bird_info (
        id, name, family, "order", wingspan_min, wingspan_max, length_min, length_max
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        family = excluded.family,
        wingspan_min = excluded.wingspan_min;
    """
    data_to_insert = []
    for bird in birds_data:
        record = (
            bird.get("id"),
            bird.get("name"),
            bird.get("family"),
            bird.get("order"),
            bird.get("wingspanMin"),
            bird.get("wingspanMax"),
            bird.get("lengthMin"),
            bird.get("lengthMax")
        )
        if all(record):
            data_to_insert.append(record)

    try:
        c.executemany(insert_query, data_to_insert)
        db.commit()
        print(f"\nSuccessfully inserted/updated {len(data_to_insert)} bird records.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")


def fetch_cat_data():
    cat_key = key_load("TheCatAPI")
    API_BASE_URL = "https://api.thecatapi.com"
    API_ENDPOINT = "/v1/images/search"
    cat_data = []
    page = 0
    page_max = 200
    headers = {
        "x-api-key": cat_key
    }
    while page < page_max:
        params = {"page": page,"api_key" : cat_key, "has_breeds" : 1}

        try:
            url = f"{API_BASE_URL}{API_ENDPOINT}"
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()[0]
            cats = data.get("breeds", [])
            cat_data.extend(cats)
            time.sleep(0.01)
            page+=1

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API request: {e}")
            break

    insert_query = """
    INSERT OR IGNORE INTO cat_info (
        id, name, origin, "life_span", intelligence, social_needs, weight_min, weight_max
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    data_to_insert = []
    for cat in cat_data:
        life_span_upper = int(cat.get("life_span", "0 - 0").split(" - ")[1].strip())
        imperial_weight_str = cat.get("weight", {}).get("imperial", "0 - 0")
        weight_parts = [part.strip() for part in imperial_weight_str.split(" - ")]
        weight_min = int(weight_parts[0]) if weight_parts else 0
        weight_max = int(weight_parts[1]) if len(weight_parts) > 1 else 0
        record = (
            cat.get("id"),
            cat.get("name"),
            cat.get("origin"),
            life_span_upper,
            cat.get("intelligence"),
            cat.get("social_needs"),
            weight_min,
            weight_max
        )
        if all(record):
            data_to_insert.append(record)

    try:
        c.executemany(insert_query, data_to_insert)
        db.commit()
        print(f"\nSuccessfully inserted/updated {len(data_to_insert)} cat records.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")


def fetch_poke_data():
    poke_data = []
    for poke_num in range(1, 650):
        pokemon_data = get_json(f"https://pokeapi.co/api/v2/pokemon/{poke_num}")
        if poke_num <= 151:
            gen = 1
        elif poke_num <= 251:
            gen = 2
        elif poke_num <= 386:
            gen = 3
        elif poke_num <= 493:
            gen = 4
        else:
            gen = 5
        stats = (
            pokemon_data['id'],
            pokemon_data['name'],
            pokemon_data['types'][0]['type']['name'],
            pokemon_data['types'][1]['type']['name'] if len(pokemon_data['types']) > 1 else "No Type",
            pokemon_data['height'] / 10.0,
            pokemon_data['weight'] / 10.0,
            gen
            )
        poke_data.append(stats)
    try:
        c.executemany("INSERT OR IGNORE INTO poke_info (id, name, type_one, type_two, height, weight, generation) VALUES (?, ?, ?, ?, ?, ?, ?)", poke_data)
        db.commit()
        print(f"\nSuccessfully inserted/updated {len(poke_data)} pokemon records.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")

def fetch_all():
    fetch_poke_data()
    fetch_bird_data()
    fetch_cat_data()
    db.close()
    print("Finished Fetching")

def query_pokemon(name):
    c.execute("SELECT * FROM poke_info WHERE name = ? COLLATE NOCASE", (name,))
    return c.fetchone()

def query_cat(name):
    c.execute("SELECT * FROM cat_info WHERE name = ? COLLATE NOCASE", (name,))
    return c.fetchone()

def query_bird(name):
    c.execute("SELECT * FROM bird_info WHERE name = ? COLLATE NOCASE", (name,))
    return c.fetchone()

if __name__ == "__main__":
    fetch_all()
