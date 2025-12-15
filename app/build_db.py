from __init__ import key_load
import requests
import sqlite3
import time

DB_FILE="database.db"
db = sqlite3.connect(DB_FILE, check_same_thread=False)
c = db.cursor()


nuthatch_key = key_load("NuthatchAPI")



def fetch_bird_data():
    nuthatch_key = key_load("NuthatchAPI")
    API_BASE_URL = "https://nuthatch.lastelm.software"
    API_ENDPOINT = "/v2/birds"
    birds_data = []
    page = 1
    page_max = 10

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
            time.sleep(1)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API request: {e}")
            break

    insert_query = """
    INSERT INTO bird_info (
        id, name, family, "order", status, wingspan_min, wingspan_max, length_min, length_max
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        family = excluded.family,
        status = excluded.status,
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
            bird.get("conservationStatus"),
            bird.get("wingspanMin"),
            bird.get("wingspanMax"),
            bird.get("lengthMin"),
            bird.get("lengthMax")
        )
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

    while page < page_max:
        params = {"page": page,'x-api-key' : cat_key, "limit":100}

        try:
            url = f"{API_BASE_URL}{API_ENDPOINT}"
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            cats = data.get("images", [])
            cat_data.extend(cats)
            page +=1
            time.sleep(1)
            print(response)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred during API request: {e}")
            break

    insert_query = """
    INSERT INTO bird_info (
        id, name, origin, "life_span", intelligence, social_needs, weight_min, weight_max
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(id) DO UPDATE SET
        name = excluded.name,
        family = excluded.family,
        status = excluded.status,
        wingspan_min = excluded.wingspan_min;
    """
    data_to_insert = []
    for cat in cat_data:
        life_span_upper = int(cat.get("life_span", "0 - 0").split(" - ")[1].strip())
        imperial_weight_str = cat.get("weight", {}).get("imperial", "0 - 0")
        weight_parts = [part.strip() for part in imperial_weight_str.split(" - ")]
        weight_min = int(weight_parts[0]) if weight_parts else 0
        weight_max = int(weight_parts[1]) if len(weight_parts) > 1 else 0

        print(cat)
        cat.get("id"),
        cat.get("name"),
        cat.get("origin"),
        life_span_upper,
        cat.get("intelligence"),
        cat.get("social_needs"),
        weight_min,
        weight_max
        data_to_insert.append(record)

    try:
        c.executemany(insert_query, data_to_insert)
        db.commit()
        print(f"\nSuccessfully inserted/updated {len(data_to_insert)} cat records.")
    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")
    finally:
        db.close()
fetch_bird_data()
fetch_cat_data()
