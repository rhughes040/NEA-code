
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Tuple
from config import starting_balance
from config import db_name



class Database:
    #manages all database operations for the roulette game.

    def __init__(self, db_name: str = db_name):
        #initializes the database
        self.db_name = db_name
        self.setup_database()

    def setup_database(self):
    #create all necessary tables if they don't exist.
        with self.get_connection() as conn:
            cursor = conn.cursor()

        #users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    balance INTEGER DEFAULT 1000 NOT NULL,
                    created_at TEXT NOT NULL,
                    CONSTRAINT username_length CHECK(LENGTH(username) <= 30)
                )
            """,)


            #sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                        session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        start_balance INTEGER NOT NULL,
                        end_balance INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
            """)

            #bets tbale
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bets (
                        bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER NOT NULL,
                        bet_type TEXT NOT NULL,
                        bet_value TEXT NOT NULL,
                        amount INTEGER NOT NULL,
                        result TEXT NOT NULL,
                        payout INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (session_id) REFERENCES sessions (session_id) ON DELETE CASCADE
                    )
                """)

            #leaderboard table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS leaderboard (
                        user_id INTEGER PRIMARY KEY,
                        games_won INTEGER DEFAULT 0 NOT NULL,
                        total_games INTEGER DEFAULT 0 NOT NULL,
                        win_rate REAL DEFAULT 0.0 NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                    )
                """)

            #creates index for better/faster performance when searching
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_bets_session ON bets(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leaderboard_winrate ON leaderboard(win_rate DESC)")

    #user management
    def create_user(self, username: str, password_hash: str, salt: str) -> int:

        #creates new user

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users ( username, password_hash, salt, balance, created_at) VALUES (?, ?, ?, ?, ?)",
                (username, password_hash, salt, starting_balance, datetime.now().isoformat())
            )
            conn.commit
            return cursor.lastrowid

    def get_user(self, username: str) -> Optional[Tuple]:
        #retrieves user by username

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username,  password_hash, salt,  balance FROM users WHERE username=?",
                (username,)
            )
            return cursor.fetchone()

    def update_user_balance(self, user_id: int, balance: int):
        #updates balance

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users  SET balance=? WHERE id=?",
                (balance, user_id)
            )
            conn.commit()


        # Session Management
    def start_session(self, user_id: int, start_balance: int) -> int:
        #starts a new session

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (user_id, start_time, start_balance) VALUES (?, ?, ?)",
                (user_id, datetime.now().isoformat(), start_balance)
            )
            conn.commit()
            return cursor.lastrowid

    def end_session(self, user_id: int, end_balance: int):

        #ends the current gaming session.


        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT session_id
                           FROM sessions
                           WHERE user_id = ?
                             AND end_time IS NULL
                           ORDER BY session_id DESC LIMIT 1
                           """, (user_id,))

            result = cursor.fetchone()
            if result:
                session_id = result[0]
                # Updates that specific session through the use of session_id
                cursor.execute("""
                               UPDATE sessions
                               SET end_time    = ?,
                                   end_balance = ?
                               WHERE session_id = ?
                               """, (datetime.now().isoformat(), end_balance, session_id))
                conn.commit()

            # logs the bets
    def log_bet(self, session_id: int, bet_type: str, bet_value: str,
                amount: int, result: str, payout: int):
        #logs a bet to the database

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bets (session_id, bet_type, bet_value, amount, result, payout, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,(session_id, bet_type, bet_value, amount, result, payout, datetime.now().isoformat()))
            conn.commit()

    #leaderboard management
    def update_leaderboard(self, user_id: int, won: bool):

        #updates the leaderboard

        with self.get_connection() as conn:
            cursor = conn.cursor()

            #checks the user exists
            cursor.execute(
                "INSERT OR IGNORE INTO leaderboard (user_id) VALUES (?)",
                (user_id,)
            )

            # updates the statistics/actual leaderboard
            cursor.execute(
                "UPDATE leaderboard SET total_games = total_games + 1 WHERE user_id = ?",
                (user_id,)
            )

            if won:
                cursor.execute(
                    "UPDATE leaderboard SET games_won = games_won + 1 WHERE user_id = ?",
                    (user_id,)
                )

            # calculates win rate
            cursor.execute(
                "SELECT games_won, total_games FROM leaderboard WHERE user_id = ?",
                (user_id,)
            )
            games_won, total_games = cursor.fetchone()
            win_rate = (games_won / total_games * 100) if total_games > 0 else 0.0

            cursor.execute(
                "UPDATE leaderboard SET win_rate = ? WHERE user_id = ?",
                (win_rate, user_id)
            )
            conn.commit()

    def get_leaderboard(self, limit: int = 10) -> List[Tuple[str, int, int, float]]:
        #gets the top 10 users from the leaderboard
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT users.username,
                                  leaderboard.games_won,
                                  leaderboard.total_games,
                                  leaderboard.win_rate
                           FROM leaderboard
                                    JOIN users ON leaderboard.user_id = users.id
                           WHERE leaderboard.total_games > 0
                           ORDER BY leaderboard.win_rate DESC, leaderboard.games_won DESC LIMIT ?
                           """, (limit,))
            return cursor.fetchall()

    def get_connection(self):
        return sqlite3.connect(self.db_name)
