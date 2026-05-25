import streamlit as st

st.title("Rummikub Score Tracker")


if "game_night" not in st.session_state:
    st.session_state.game_night = {
        "name": "Rummikub Abend",
        "players": [],
        "rounds": []
    }

st.text_input("Spielername", key="player_input")


def add_player():
    player_name = st.session_state.player_input

    if player_name:
        if player_name in st.session_state.game_night["players"]:
            st.warning("Dieser Spieler wurde bereits hinzugefügt.")
        else:
            st.session_state.game_night["players"].append(player_name)
            st.session_state.player_input = ""
    else:
        st.warning("Name fehlt")


st.button("Spieler hinzufügen", on_click=add_player)

st.subheader("Spieler")

for player in st.session_state.game_night["players"]:
    st.write(f"• {player}")


def save_round():

    winner = st.session_state.round_winner

    round_points = {}

    for player in st.session_state.game_night["players"]:

        if player == winner:
            round_points[player] = 0

        else:
            round_points[player] = st.session_state[f"points_{player}"]

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

    st.button("Runde speichern", on_click=save_round)
    
st.subheader("Gespeicherte Runden")

for index, round_data in enumerate(st.session_state.game_night["rounds"], start=1):

    st.markdown(f"### Runde {index}")

    st.write(f"🏆 Gewinner: {round_data['winner']}")

    for player, points in round_data["points"].items():
        st.write(f"• {player}: {points} Punkte")
    
    if st.button("Runde löschen", key=f"delete_round_{index}"):
        st.session_state.game_night["rounds"].pop(index - 1)
        st.rerun()

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

    for place, (player, points) in enumerate(sorted_total_points, start=1):
        st.write(f"{place}. {player}: {points} Punkte | Siege: {win_counter[player]}")

    if total_points:
        winner = min(total_points, key=lambda player: total_points[player])
        st.success(f"Aktueller Gewinner: {winner}")