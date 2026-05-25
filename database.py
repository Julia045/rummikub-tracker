import sqlite3


def create_tables():
    connection = sqlite3.connect("rummikub.db")
    cursor = connection.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_nights (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_night_id INTEGER,
        name TEXT,
        FOREIGN KEY (game_night_id) REFERENCES game_nights(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_night_id INTEGER,
        winner TEXT,
        FOREIGN KEY (game_night_id) REFERENCES game_nights(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS round_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER,
        player_name TEXT,
        points INTEGER,
        FOREIGN KEY (round_id) REFERENCES rounds(id)
    )
    """)

    connection.commit()
    connection.close()


def save_game_night(name):
    connection = sqlite3.connect("rummikub.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO game_nights (name) VALUES (?)",
        (name,)
    )

    game_night_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return game_night_id

def get_game_nights():

    connection = sqlite3.connect("rummikub.db")
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM game_nights")

    game_nights = cursor.fetchall()

    connection.close()

    return game_nights

def save_player(game_night_id, player_name):

    connection = sqlite3.connect("rummikub.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO players (game_night_id, name)
        VALUES (?, ?)
        """,
        (game_night_id, player_name)
    )

    connection.commit()
    connection.close()

def save_round(game_night_id, winner):

    connection = sqlite3.connect("rummikub.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO rounds (game_night_id, winner)
        VALUES (?, ?)
        """,
        (game_night_id, winner)
    )

    round_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return round_id

def save_round_points(round_id, player_name, points):

    connection = sqlite3.connect("rummikub.db")
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO round_points (round_id, player_name, points)
        VALUES (?, ?, ?)
        """,
        (round_id, player_name, points)
    )

    connection.commit()
    connection.close()