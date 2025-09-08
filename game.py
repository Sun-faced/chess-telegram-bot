import requests
import time


def create_lichess_game(api_token, game_mode):
    url = "https://lichess.org/api/challenge/open"
    headers = {"Authorization": f"Bearer {api_token}"}
    data = {
        "clock.limit": game_mode[0],
        "clock.increment": game_mode[1]
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["id"]
    except Exception as e:
        return f"ERROR: {str(e)}"


def cancel_lichess_challenge(challenge_id, api_token):
    url = f"https://lichess.org/api/challenge/{challenge_id}/cancel"
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return True
    except Exception as e:
        return f"ERROR: {str(e)}"

# Generates full URL from challenge ID


def make_challenge_url(challenge_id):
    return f"https://lichess.org/challenge/{challenge_id}"


def check_if_error(string):
    return isinstance(string, str) and string.startswith("ERROR:")


def has_game_started(challenge_id, api_token):
    url = f"https://lichess.org/api/game/{challenge_id}"
    headers = {"Authorization": f"Bearer {api_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False
        else:
            return f"ERROR: Unexpected status code {response.status_code}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def has_game_ended(game_id, api_token):
    url = f"https://lichess.org/api/game/{game_id}"
    headers = {"Authorization": f"Bearer {api_token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            game_data = response.json()
            status = game_data.get("status", "unknown")
            return status != "started"  # True if the game has ended, False if still ongoing
        elif response.status_code == 404:
            return f"ERROR: Game {game_id} not found"
        else:
            return f"ERROR: Unexpected status code {response.status_code}, Response: {response.text}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def has_player_won(username, winner):
    return 0 if winner == username else 1


def get_game_winner(username, game_id, api_token):
    url = f"https://lichess.org/api/game/{game_id}"
    headers = {"Authorization": f"Bearer {api_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        game_data = response.json()
        winner = game_data.get("winner")
        players = game_data.get("players", {})
        white_player = players.get("white", {}).get("userId", "")
        black_player = players.get("black", {}).get("userId", "")

        if winner == "white":
            return has_player_won(username, white_player)
        elif winner == "black":
            return has_player_won(username, black_player)
        else:
            return 2
    else:
        return -1


def track_session(username, api_token, game_id):

    start = time.time()
    while time.time() - start < 60:
        if has_game_started(game_id, api_token):
            break
        time.sleep(1)
    if not has_game_started(game_id, api_token):
        cancel_lichess_challenge(game_id, api_token)
        return -2

    while not has_game_ended(game_id, api_token):
        time.sleep(3)

    return get_game_winner(username, game_id, api_token)
