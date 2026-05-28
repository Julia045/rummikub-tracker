import streamlit as st
import libsql


def get_connection():
    return libsql.connect(
        st.secrets["LIBSQL_URL"],
        auth_token=st.secrets["LIBSQL_AUTH_TOKEN"]
    )



def create_tables():
    connection = get_connection()
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
        name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rounds (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_night_id INTEGER,
        winner TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS round_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        round_id INTEGER,
        player_name TEXT,
        points INTEGER
    )
    """)

    connection.commit()
    connection.close()


def save_game_night(name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO game_nights (name) VALUES (?)",
        (name,)
    )

    cursor.execute("SELECT last_insert_rowid()")
    game_night_id = cursor.fetchone()[0]

    connection.commit()
    connection.close()

    return game_night_id


def get_game_nights():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, name FROM game_nights")
    game_nights = cursor.fetchall()

    connection.close()

    return game_nights


def save_player(game_night_id, player_name):
    connection = get_connection()
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


def get_players(game_night_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT name FROM players
        WHERE game_night_id = ?
        """,
        (game_night_id,)
    )

    players = cursor.fetchall()

    connection.close()

    return players


def save_round(game_night_id, winner):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO rounds (game_night_id, winner)
        VALUES (?, ?)
        """,
        (game_night_id, winner)
    )

    cursor.execute("SELECT last_insert_rowid()")
    round_id = cursor.fetchone()[0]

    connection.commit()
    connection.close()

    return round_id


def get_rounds(game_night_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, winner FROM rounds
        WHERE game_night_id = ?
        """,
        (game_night_id,)
    )

    rounds = cursor.fetchall()

    connection.close()

    return rounds


def save_round_points(round_id, player_name, points):
    connection = get_connection()
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


def get_round_points(round_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT player_name, points
        FROM round_points
        WHERE round_id = ?
        """,
        (round_id,)
    )

    round_points = cursor.fetchall()

    connection.close()

    return round_points


def delete_game_night(game_night_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM round_points
        WHERE round_id IN (
            SELECT id FROM rounds WHERE game_night_id = ?
        )
        """,
        (game_night_id,)
    )

    cursor.execute(
        "DELETE FROM rounds WHERE game_night_id = ?",
        (game_night_id,)
    )

    cursor.execute(
        "DELETE FROM players WHERE game_night_id = ?",
        (game_night_id,)
    )

    cursor.execute(
        "DELETE FROM game_nights WHERE id = ?",
        (game_night_id,)
    )

    connection.commit()
    connection.close()

def get_history_data():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            game_nights.id,
            game_nights.name,
            players.name,
            rounds.id,
            rounds.winner,
            round_points.player_name,
            round_points.points
        FROM game_nights
        LEFT JOIN players
            ON players.game_night_id = game_nights.id
        LEFT JOIN rounds
            ON rounds.game_night_id = game_nights.id
        LEFT JOIN round_points
            ON round_points.round_id = rounds.id
        ORDER BY game_nights.id, rounds.id
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows