from __init__ import key_load, get_json
import requests
import sqlite3
import time
import random

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()

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
        print(bird)
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
    finally:
        db.close()

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
        print(cat)
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
    finally:
        db.close()

def fetch_poke_data():
    poke_data = []
    for poke_num in range(1, 650):
        data = get_json(f"https://pokeapi.co/api/v2/pokemon/{poke_num}")
        url = data['species']['url']
        pokemon_data = get_json(url)
        if pokemon_data:
           generation = pokemon_data['generation']['name']
        else:
            generation = "generation-i"
        data_map = {"generation-i":1, "generation-ii":2, "generation-iii":3, "generation-iv":4, "generation-v":5}
        gen = data_map.get(generation)
        stats = (
            data['id'],
            data['name'],
            data['types'][0]['type']['name'],
            data['types'][1]['type']['name'] if len(data['types']) > 1 else "No Type",
            data['height'] / 10.0,
            data['weight'] / 10.0,
            gen
            )
        poke_data.append(stats)
    try:
        c.executemany("INSERT OR IGNORE INTO poke_info (id, name, type_one, type_two, height, weight, generation) VALUES (?, ?, ?, ?, ?, ?, ?)", poke_data)
        db.commit()
        print(f"\nSuccessfully inserted/updated {len(data_to_insert)} pokemon records.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    finally:
        db.close()
def fetch_all():
    fetch_poke_data()
    fetch_bird_data()
    fetch_cat_data()

def query_pokemon(name):
    c.execute("SELECT * FROM poke_info WHERE name = ? COLLATE NOCASE", (name,))
    return c.fetchone()

def query_cat(name):
    c.execute("SELECT * FROM cat_info WHERE name = ? COLLATE NOCASE", (name,))
    return c.fetchone()

def query_bird(name):
    c.execute("SELECT * FROM bird_info WHERE name = ? COLLATE NOCASE", (name,))
    return c.fetchone()
