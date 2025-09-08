import sqlite3

DB_FILE = 'database/stats.db'


def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            draws INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()


def register_user(user_id, username):

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if a user with the given user_id exists
    cursor.execute("SELECT 1 FROM players WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    if result is None:
        # User doesn't exist: insert a new row
        cursor.execute(
            "INSERT INTO players (user_id, username, wins, losses, draws) VALUES (?, ?, 0, 0, 0)",
            (user_id, username)
        )
        conn.commit()
        conn.close()
        return True

    # User exists: update the username
    cursor.execute(
        "UPDATE players SET username = ? WHERE user_id = ?",
        (username, user_id)
    )
    conn.commit()
    conn.close()
    return False


def get_user_stats(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT wins, losses, draws FROM players WHERE user_id = ?
    ''', (user_id,))

    wins, losses, draws = cursor.fetchone()
    conn.close()

    return wins, losses, draws


def update_user_stats(user_id, result):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if result == 0:
        cursor.execute(
            "UPDATE players SET losses = losses + 1 WHERE user_id = ?", (user_id,))
    elif result == 1:
        cursor.execute(
            "UPDATE players SET wins = wins + 1 WHERE user_id = ?", (user_id,))
    elif result == 2:
        cursor.execute(
            "UPDATE players SET draws = draws + 1 WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()


def get_username(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username FROM players WHERE user_id = ?
    ''', (user_id,))
    username = cursor.fetchone()[0]
    conn.close()

    return username


def get_top_players():
    """Returns a list of up to 3 usernames with the highest (wins - losses)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username FROM players
        ORDER BY (wins - losses) DESC
        LIMIT 3
    ''')
    top_players = [row[0] for row in cursor.fetchall()]
    conn.close()

    return top_players
