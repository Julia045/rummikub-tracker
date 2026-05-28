import streamlit as st
import pandas as pd
from database import (
    create_tables,
    save_game_night,
    get_game_nights,
    save_player,
    save_round as save_round_to_db,
    save_round_points,
    get_players,
    get_rounds,
    get_round_points,
    delete_game_night,
    get_history_data
)

if "password_correct" not in st.session_state:
    st.session_state.password_correct = False


def check_password():
    if st.session_state.password == st.secrets["APP_PASSWORD"]:
        st.session_state.password_correct = True
    else:
        st.error("Falsches Passwort")


if not st.session_state.password_correct:
    st.text_input(
        "Passwort",
        type="password",
        key="password",
        on_change=check_password
    )
    st.stop()

st.title("Rummikub Score Tracker")
if "tables_created" not in st.session_state:
    create_tables()
    st.session_state.tables_created = True

if "game_night" not in st.session_state:
        st.session_state.game_night = {
            "id": None,
            "name": "",
            "players": [],
            "rounds": []
        }

if "game_night_name_set" not in st.session_state:
        st.session_state.game_night_name_set = False

tab_setup, tab_spiel, tab_wertung, tab_historie = st.tabs([
    "🎲 Spielabend und Spieler",
    "➕ Runden",
    "🏆 Gesamtwertung",
    "📚 Alte Spielabende"
])

with tab_setup:
    st.subheader("Neuer Spielabend")

    if not st.session_state.game_night_name_set:

        with st.form("game_night_form"):
            game_night_name = st.text_input("Name des Spielabends")
            submitted = st.form_submit_button("Spielabend starten")

        if submitted:
            if game_night_name:
                game_night_id = save_game_night(game_night_name)

                st.session_state.game_night = {
                    "id": game_night_id,
                    "name": game_night_name,
                    "players": [],
                    "rounds": []
                }

                st.session_state.game_night_name_set = True
                st.rerun()
            else:
                st.warning("Bitte gib einen Namen ein.")

    else:
        st.subheader(st.session_state.game_night["name"])

    st.subheader("Spieler")

    def add_player():
        player_name = st.session_state.player_input

        if player_name:
            if player_name in st.session_state.game_night["players"]:
                st.warning("Dieser Spieler wurde bereits hinzugefügt.")
            else:
                st.session_state.game_night["players"].append(player_name)
                save_player(
                    st.session_state.game_night["id"],
                    player_name
                )
                st.session_state.player_input = ""
        else:
            st.warning("Name fehlt")

    with st.form("player_form"):

        st.text_input(
            "Spielername",
            key="player_input"
        )

        st.form_submit_button(
            "Spieler hinzufügen",
            on_click=add_player
        )

    for player in st.session_state.game_night["players"]:
        st.write(f"• {player}")

with tab_spiel:
    st.subheader("Neue Runde")

    def save_round_app():

        winner = st.session_state.round_winner

        round_points = {}

        for player in st.session_state.game_night["players"]:

            if player == winner:
                round_points[player] = 0

            else:
                round_points[player] = st.session_state[f"points_{player}"]
        
        round_id = save_round_to_db(
        st.session_state.game_night["id"],
        winner
    )

        for player, points in round_points.items():

            save_round_points(
                round_id,
                player,
                points
            )

        round_data = {
            "winner": winner,
            "points": round_points
        }

        st.session_state.game_night["rounds"].append(round_data)

        for player in st.session_state.game_night["players"]:

            if player != winner:
                st.session_state[f"points_{player}"] = 0


    if len(st.session_state.game_night["players"]) >= 2:

        st.subheader("Runde eintragen")

        winner = st.selectbox(
            "Wer hat die Runde gewonnen?",
            st.session_state.game_night["players"],
            key="round_winner"
        )

        for player in st.session_state.game_night["players"]:

            if player == winner:
                st.write(f"{player}: 0 Punkte (Gewinner)")

            else:
                st.number_input(
                    f"Punkte für {player}",
                    min_value=0,
                    step=1,
                    key=f"points_{player}"
                )

        st.button("Runde speichern", on_click=save_round_app)

    st.subheader("Gespeicherte Runden")

    for index, round_data in enumerate(st.session_state.game_night["rounds"], start=1):

        st.markdown(f"### Runde {index}")

        st.write(f"🏆 Gewinner: {round_data['winner']}")

        for player, points in round_data["points"].items():
            st.write(f"• {player}: {points} Punkte")
        
        if st.button("Runde löschen", key=f"delete_round_{index}"):
            st.session_state.game_night["rounds"].pop(index - 1)
            st.rerun()

with tab_wertung:

    if st.session_state.game_night["rounds"]:

        st.subheader("Gesamtwertung")

        total_points = {}
        win_counter = {}

        for player in st.session_state.game_night["players"]:
            total_points[player] = 0
            win_counter[player] = 0

        for round_data in st.session_state.game_night["rounds"]:
            winner = round_data["winner"]
            win_counter[winner] += 1

            for player, points in round_data["points"].items():
                total_points[player] += points

        sorted_total_points = sorted(
            total_points.items(),
            key=lambda item: item[1]
        )

        table_data = []

        for place, (player, points) in enumerate(sorted_total_points, start=1):

            table_data.append({
                "Platz": place,
                "Spieler": player,
                "Punkte": points,
                "Siege": win_counter[player]
            })
        
        scoreboard_df = pd.DataFrame(table_data)
        for place, (player, points) in enumerate(sorted_total_points, start=1):
            if place == 1:
                medal = "🥇"
            elif place == 2:
                medal = "🥈"
            elif place == 3:
                medal = "🥉"
            else:
                medal = f"{place}."

            st.markdown(
                f"### {medal} {player} — {points} Punkte | {win_counter[player]} Siege"
            )

        #winner = min(total_points, key=lambda player: total_points[player])
        #st.success(f"Aktueller Gewinner: {winner}")

    else:
        st.info("Noch keine Runde gespeichert.")

with tab_historie:

    st.subheader("Alte Spielabende")

    history_rows = get_history_data()

    history = {}

    for row in history_rows:
        game_night_id = row[0]
        game_night_name = row[1]
        player_name = row[2]
        round_id = row[3]
        winner = row[4]
        point_player_name = row[5]
        points = row[6]

        if game_night_id not in history:
            history[game_night_id] = {
                "name": game_night_name,
                "players": set(),
                "rounds": {}
            }

        if player_name:
            history[game_night_id]["players"].add(player_name)

        if round_id:
            if round_id not in history[game_night_id]["rounds"]:
                history[game_night_id]["rounds"][round_id] = {
                    "winner": winner,
                    "points": {}
                }

            if point_player_name:
                history[game_night_id]["rounds"][round_id]["points"][point_player_name] = points

    if history:

        for game_night_id, game_night_data in history.items():

            st.markdown(f"### {game_night_data['name']}")

            if st.button(
                "Spielabend löschen",
                key=f"delete_history_{game_night_id}"
            ):
                delete_game_night(game_night_id)
                st.rerun()

            total_points = {}
            win_counter = {}

            for player in game_night_data["players"]:
                total_points[player] = 0
                win_counter[player] = 0

            for round_data in game_night_data["rounds"].values():
                winner = round_data["winner"]

                if winner in win_counter:
                    win_counter[winner] += 1

                for player_name, points in round_data["points"].items():
                    if player_name in total_points:
                        total_points[player_name] += points

            sorted_total_points = sorted(
                total_points.items(),
                key=lambda item: item[1]
            )

            for place, (player, points) in enumerate(sorted_total_points, start=1):
                st.write(
                    f"{place}. {player}: {points} Punkte | Siege: {win_counter[player]}"
                )

            st.divider()

    else:
        st.info("Noch keine alten Spielabende gespeichert.")