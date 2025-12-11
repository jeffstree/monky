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
    total_fetched = 0

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
fetch_bird_data()
