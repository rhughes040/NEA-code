import random
import sqlite3
import tkinter as tk
from tkinter import messagebox
import os
import hashlib, os
from PIL import Image, ImageTk, ImageSequence
import itertools

#numbers/colours
numbers = list(range(0, 37))
colors = {
   0: 'green', 1: 'red', 2: 'black', 3: 'red', 4: 'black',
   5: 'red', 6: 'black', 7: 'red', 8: 'black', 9: 'red',
   10: 'black', 11: 'black', 12: 'red', 13: 'black',
   14: 'red', 15: 'black', 16: 'red', 17: 'black',
   18: 'red', 19: 'black', 20: 'red', 21: 'black',
   22: 'red', 23: 'black', 24: 'red', 25: 'black',
   26: 'red', 27: 'black', 28: 'red', 29: 'black',
   30: 'red', 31: 'black', 32: 'red', 33: 'black',
   34: 'red', 35: 'black', 36: 'red'
}
current_user = {}

#betting function
def place_bet():


   print("\nChoose a type of bet:")
   print("1. Bet on a number (0-36)")
   print("2. Bet on Red or Black")
   print("3. Bet on Odd or Even")
   print("4. Bet on High (19-36) or Low (1-18)")


   bet_type = input("\nEnter the number of the bet you want to place: ")
   while bet_type not in ['1', '2', '3', '4']:
       bet_type = input("Invalid option. Enter the number of the bet you want to place: ")
   if bet_type == '1':
       number = int(input("\nEnter a number between 0 and 36: "))
       while number not in numbers:
           number = int(input("\nInvalid number. Enter a number between 0 and 36: "))
       return {'type': 'number', 'value': number}
   elif bet_type == '2':
       color = input("\nDo you want to bet on Red or Black? ").lower()
       while color not in ['red', 'black']:
           color = input("Invalid input. Do you want to bet on Red or Black? ").lower()
       return {'type': 'color', 'value': color}
   elif bet_type == '3':
       odd_or_even = input("\nDo you want to bet on Odd or Even? ").lower()
       while odd_or_even not in ['odd', 'even']:
           odd_or_even = input("Invalid input. Do you want to bet on Odd or Even? ").lower()
       return {'type': 'odd_even', 'value': odd_or_even}
   elif bet_type == '4':
       high_or_low = input("\nDo you want to bet on High (19-36) or Low (1-18)? ").lower()
       while high_or_low not in ['high', 'low']:
           high_or_low = input("\nInvalid input. Do you want to bet on High (19-36) or Low (1-18)? ").lower()
       return {'type': 'high_low', 'value': high_or_low}
   else:
       print("Invalid option!")
       return place_bet()


   return place_bet()

#main game class/function
class RouletteGame:
  def __init__(self, user):
      self.user = user
      self.balance = user['balance']
      self.user_id = user['id']
      self.score = 0

      print("\n--------------------")
      print("Welcome to Roulette!")
      print("--------------------")
      self.play()

  def spin_wheel(self):
      return random.choice(numbers)

  def check_win(self, bet, result):
      result_color = 'green' if result == 0 else colors[result]
      print(f"\nRoulette result:\033[34m {result} ({result_color})\033[0m")
      if bet['type'] == 'number' and bet['value'] == result:
          self.score += 1
          return True, 35

      if bet['type'] == 'color' and bet['value'] == result_color:
          self.score += 1
          return True, 2

      if bet['type'] == 'odd_even' and result != 0:
          if (result % 2 == 0 and bet['value'] == 'even') or \
             (result % 2 != 0 and bet['value'] == 'odd'):
              self.score += 1
              return True, 2

      if bet['type'] == 'high_low':
          if (bet['value'] == 'high' and result > 18) or \
             (bet['value'] == 'low' and result <= 18):
              self.score += 1
              return True, 2
      self.score = 0
      return False, 0

  def play(self):
      print(f"Your starting balance is: ${self.balance}")
      while True:
          if self.balance <= 0:
              print("You're out of money!")
              break
          print(f"\nCurrent balance: ${self.balance}")

          bet = place_bet()
          while True:
              try:
                  bet_amount = int(input(f"\nBet amount: You have ${self.balance} "))
                  if 0 < bet_amount <= self.balance:
                      break
              except ValueError:
                  pass

          result = self.spin_wheel()
          win, payout = self.check_win(bet, result)

          if win:
              winnings = bet_amount * payout
              self.balance += winnings
              print(f"\nYou win ${winnings}")
          else:
              self.balance -= bet_amount
              print(f"\nYou lose ${bet_amount}")

          self.db.update_user_balance(self.user_id, self.balance)

          if input("\nPlay again? (y/n): ").lower() != 'y':
              print(f"\nThank you for playing! Your final balance was ${self.balance}")
              break

#main game class/function
class RouletteGIFGame:
   def __init__(self, user, db):
       self.user = user
       self.db = db
       self.balance = user['balance']
       self.user_id = user['id']
       self.spinning = False

       self.window = tk.Tk()
       self.window.protocol("WM_DELETE_WINDOW", self.on_close)
       self.window.title("Roulette")

       tk.Label(self.window, text="Roulette", font=("Arial", 16)).pack(pady=5)
       self.balance_label = tk.Label(self.window, text=f"Balance: ${self.balance}")
       self.balance_label.pack()

       tk.Label(self.window, text="Bet Type").pack()
       self.bet_type = tk.StringVar(value="number")
       tk.OptionMenu(self.window, self.bet_type, "number", "color", "odd_even", "high_low").pack()

       tk.Label(self.window, text="Bet Value").pack()
       self.bet_value = tk.Entry(self.window)
       self.bet_value.pack()

       tk.Label(self.window, text="Bet Amount").pack()
       self.bet_amount = tk.Entry(self.window)
       self.bet_amount.pack()

       self.gif_label = tk.Label(self.window)
       self.gif_label.pack(pady=10)

       self.result_label = tk.Label(self.window, text="")
       self.result_label.pack()

       self.spin_button = tk.Button(self.window, text="SPIN", command=self.start_spin)
       self.spin_button.pack(pady=10)
       tk.Button(self.window, text="View Leaderboard", command=view_leaderboard).pack(pady=5)
       tk.Button(self.window, text="Close", command=self.safe_close).pack(pady=5)
       self.load_gif("roulette_spin.gif")
       self.window.mainloop()

   def safe_close(self):
       if self.spinning:
           return
       messagebox.showinfo("Goodbye", f"Thank you for playing! \nYou finished with ${self.balance}")
       self.window.destroy()
       self.db.end_session(self.user_id, self.balance)

   def load_gif(self, path):
       gif = Image.open(path)
       self.frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]
       self.frame_count = len(self.frames)

   def hide_gif(self):
       self.gif_label.config(image="")

   def on_close(self):
       messagebox.showinfo("Goodbye", f"Thank you for playing!\nYou finished with ${self.balance}")
       self.window.destroy()
       self.db.end_session(self.user_id, self.balance)

   def start_spin(self):
       if self.spinning:
           return

       self.gif_label.config(image=self.frames[0])

       try:
           bet_type = self.bet_type.get()
           bet_value = self.bet_value.get().lower()
           bet_amount = int(self.bet_amount.get())

            #error handling, ensures only correct inputs work
           if bet_amount <= 0 or bet_amount > self.balance:
               raise ValueError("Invalid bet amount")

           if bet_type == "number":
               bet_value = int(bet_value)
               if not 0 <= bet_value <= 36:
                   raise ValueError("Number must be 0–36")
           elif bet_type == "color" and bet_value not in ["red", "black"]:
               raise ValueError("Color must be red or black")
           elif bet_type == "odd_even" and bet_value not in ["odd", "even"]:
               raise ValueError("Must be odd or even")
           elif bet_type == "high_low" and bet_value not in ["high", "low"]:
               raise ValueError("Must be high or low")


       except ValueError as e:
           self.result_label.config(text=str(e))
           return

       self.bet = {"type": bet_type, "value": bet_value, "amount": bet_amount}
       self.spinning = True
       self.spin_button.config(state=tk.DISABLED)
       self.result_label.config(text="Spinning...")
       self.animate(0)


   def animate(self, frame):
       if frame < self.frame_count:
           self.gif_label.config(image=self.frames[frame])
           self.window.after(50, self.animate, frame + 1)
       else:
           self.finish_spin()


   def finish_spin(self):
       result = random.choice(numbers)
       result_color = "green" if result == 0 else colors[result]

       payout = self.check_win(self.bet, result)

       #calculatyes payout and creates a pop up saying if they won and how much etc
       winnings = 0
       if payout > 0:
           winnings = self.bet["amount"] * payout
           self.balance += winnings
           messagebox.showinfo(
               "Result",
               f"Result: {result} ({result_color})\n"
               f"You WON ${winnings}\n"
               f"New balance: ${self.balance}"
           )
       else:
           self.balance -= self.bet["amount"]
           messagebox.showinfo(
               "Result",
               f"Result: {result} ({result_color})\n"
               f"You LOST ${self.bet['amount']}\n"
               f"New balance: ${self.balance}"
           )

       self.db.log_bet(
           self.user['session_id'],
           f"{self.bet['type']}:{self.bet['value']}",
           self.bet['amount'],
           "Win" if payout > 0 else "Lose",
           winnings if payout > 0 else 0
       )
       win = payout > 0
       self.db.update_leaderboard(self.user_id, win)

       #updates the users balance in the databse
       self.db.update_user_balance(self.user_id, self.balance)
       self.balance_label.config(text=f"Balance: ${self.balance}")

       # hides the GIF after result
       self.hide_gif()

       self.spinning = False
       self.spin_button.config(state=tk.NORMAL)

       # clear bet inputs for the next spin
       self.bet_value.delete(0, tk.END)
       self.bet_amount.delete(0, tk.END)

       # check if they have the money to play again
       if self.balance <= 0:
           messagebox.showinfo("Game Over", "You're out of money!")
           self.window.destroy()


   def play_again_prompt(self):
       if self.balance <= 0:
           messagebox.showinfo("Game Over", "You're out of money!")
           self.window.destroy()
           return

       # asks if the user wants to play again
       if messagebox.askyesno("Play Again?", "Do you want to play again?"):
           self.bet_value.delete(0, tk.END)
           self.bet_amount.delete(0, tk.END)
       else:
           self.window.destroy()

   def check_win(self, bet, result):
       result_color = "green" if result == 0 else colors[result]


       if bet["type"] == "number" and bet["value"] == result:
           return 35
       if bet["type"] == "color" and bet["value"] == result_color:
           return 2
       if bet["type"] == "odd_even" and result != 0:
           return 2 if (result % 2 == 0) == (bet["value"] == "even") else 0
       if bet["type"] == "high_low":
           return 2 if (bet["value"] == "high" and result > 18) or \
                        (bet["value"] == "low" and result <= 18) else 0
       return 0


#database and security functions
class Database:
    def __init__(self, db_name="fresh.db"):
        self.db_name = db_name
        self.setup_database()

    def start_session(self, user_id):
        conn = self.connect()
        c = conn.cursor()
        from datetime import datetime
        start = datetime.now().isoformat()

        c.execute("INSERT INTO sessions (user_id, start_time) VALUES (?, ?)", (user_id, start))
        conn.commit()

        session_id = c.lastrowid
        conn.close()
        return session_id

    def end_session(self, user_id, end_balance):
        conn = self.connect()
        c = conn.cursor()
        from datetime import datetime
        end = datetime.now().isoformat()

        c.execute("""
                  UPDATE sessions
                  SET end_time=?,
                      end_balance=?
                  WHERE user_id = ?
                    AND end_time IS NULL
                  """, (end, end_balance, user_id))

        conn.commit()
        conn.close()

    def log_bet(self, session_id, bet, amount, result, payout):
        conn = self.connect()
        c = conn.cursor()

        c.execute("""
                  INSERT INTO bets (session_id, bet, amount, result, payout)
                  VALUES (?, ?, ?, ?, ?)
                  """, (session_id, bet, amount, result, payout))

        conn.commit()
        conn.close()

    def update_leaderboard(self, user_id, win):
        conn = self.connect()
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO leaderboard (user_id) VALUES (?)", (user_id,))
        if win:
            c.execute("UPDATE leaderboard SET games_won = games_won + 1 WHERE user_id=?", (user_id,))
        c.execute("SELECT games_won FROM leaderboard WHERE user_id=?", (user_id,))
        games_won = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM bets WHERE session_id IN (SELECT session_id FROM sessions WHERE user_id=?)",
                  (user_id,))
        total_games = c.fetchone()[0]
        win_rate = (games_won / total_games) * 100 if total_games > 0 else 0
        c.execute("UPDATE leaderboard SET win_rate=? WHERE user_id=?", (win_rate, user_id))

        conn.commit()
        conn.close()

#def view_leaderboard():


    def get_leaderboard(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
                  SELECT fresh.username, leaderboard.games_won, leaderboard.win_rate
                  FROM leaderboard
                           JOIN fresh ON leaderboard.user_id = fresh.id
                  ORDER BY leaderboard.win_rate DESC
                  """)
        rows = c.fetchall()
        conn.close()
        return rows

    def connect(self):
        return sqlite3.connect(self.db_name)

    #creates the 4 databses, fresh is users it just glitched when it was calles uers
    def setup_database(self):
        conn = self.connect()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS fresh (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                balance INTEGER DEFAULT 1000
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                end_balance INTEGER,
                FOREIGN KEY (user_id) REFERENCES fresh (id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,    
                bet TEXT NOT NULL,
                amount INTEGER NOT NULL,
                result TEXT NOT NULL,
                payout INTEGER NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                leaderboard_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                games_won INTEGER DEFAULT NULL,
                win_rate REAL DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES fresh (id)
            )
        """)

        conn.commit()
        conn.close()

    def get_user(self, username):
        conn = self.connect()
        c = conn.cursor()
        c.execute(
            "SELECT id, username, password_hash, salt, balance FROM fresh WHERE username=?",
            (username,)
        )
        user = c.fetchone()
        conn.close()
        return user

    def create_user(self, username, password_hash, salt):
        conn = self.connect()
        conn.execute(
            "INSERT INTO fresh VALUES (NULL, ?, ?, ?, 1000)",
            (username, password_hash, salt)
        )
        conn.commit()
        conn.close()

    def update_user_balance(self, user_id, balance):
        conn = self.connect()
        conn.execute(
            "UPDATE fresh SET balance=? WHERE id=?",
            (balance, user_id)
        )
        conn.commit()
        conn.close()

def view_leaderboard():
    data = db.get_leaderboard()
    leaderboard_window = tk.Toplevel()
    leaderboard_window.title("Leaderboard")
    tk.Label(leaderboard_window, text="User | Wins | Win Rate", font=("Arial", 12, "bold")).pack(pady=5)
    for row in data:
        username, wins, win_rate = row
        tk.Label(
            leaderboard_window,
            text=f"{username} | {wins} | {win_rate:.2f}%"
        ).pack()

def hash_password(password):
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return hashed.hex(), salt.hex()

def verify_password(password, stored_hash, stored_salt):
    return hashlib.pbkdf2_hmac(
        'sha256', password.encode(), bytes.fromhex(stored_salt), 100000
    ).hex() == stored_hash

db = Database()

#login function
def check_login():
   global current_user
   username = username_entry.get()
   password = password_entry.get()
   user = db.get_user(username)

   if user and verify_password(password, user[2], user[3]):
       current_user = {'id': user[0], 'username': user[1], 'balance': user[4]}
       session_id =db.start_session(current_user['id'])
       current_user['session_id'] = session_id
       root.destroy()
       RouletteGIFGame(current_user, db)
   else:
       messagebox.showerror("Login Failed", "Incorrect login")

#register function
def register_user():
    username = username_entry.get()
    password = password_entry.get()
    h, s = hash_password(password)

    try:
        db.create_user(username, h, s)
        messagebox.showinfo("Registration Successful", "Registered")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "User Already Exists")

#gui creation
root = tk.Tk()
root.title("Login")

tk.Label(root, text="Username").grid(row=0, column=0)
tk.Label(root, text="Password").grid(row=1, column=0)

username_entry = tk.Entry(root)
password_entry = tk.Entry(root, show="*")

username_entry.grid(row=0, column=1)
password_entry.grid(row=1, column=1)

tk.Button(root, text="Login", command=check_login).grid(row=2, column=0)
tk.Button(root, text="Register", command=register_user).grid(row=2, column=1)
tk.Button(root, text="View Leaderboard", command=view_leaderboard).grid(row=4, columnspan=2)
tk.Button(root, text="Close", command=root.destroy).grid(row=3, columnspan=2)

root.mainloop()
