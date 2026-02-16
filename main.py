
# The Main entry point for my Roulette Game.

#This NEA project demonstrates:
#- Object-oriented programming
#- Database integration with SQLite
#- GUI development with Tkinter
#- Security (password hashing)
#- Input validation
#- Modular code structure


#all the imports needed
import tkinter as tk
from tkinter import messagebox
import sqlite3

from models.database import Database
from utils.security import (hash_password, verify_password)
from utils.validation import validate_username, validate_password, ValidationError
from ui.leaderboard import show_leaderboard
from game.gui_game import RouletteGUIGame


class LoginWindow:
    # main login/registration window

    def __init__(self):
        self.database = Database()
        self.current_user = None

        # Creates main window
        self.root = tk.Tk()
        self.root.title("Roulette - Login")
        self.root.geometry("350x250")
        self.root.resizable(False, False)

        self._create_widgets()

    def _create_widgets(self):
        # handles all the tkinter for the user interface
        title = tk.Label(
            self.root,
            text=" Roulette Game ",
            font=("Arial", 18, "bold"),
            fg="#D4AF37"
        )
        title.grid(row=0, column=0, columnspan=2, pady=20)

        tk.Label(self.root, text="Username:", font=("Arial", 11)).grid(
            row=1, column=0, sticky=tk.E, padx=10, pady=10
        )
        self.username_entry = tk.Entry(self.root, font=("Arial", 11), width=20)
        self.username_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Password:", font=("Arial", 11)).grid(
            row=2, column=0, sticky=tk.E, padx=10, pady=10
        )
        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 11), width=20)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10)

        # pressable buttons
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=3, column=0, columnspan=2, pady=15)

        tk.Button(
            button_frame,
            text="Login",
            command=self.login,
            font=("Arial", 11),
            width=10,
            bg="#4CAF50",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Register",
            command=self.register,
            font=("Arial", 11),
            width=10,
            bg="#2196F3",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        bottom_frame = tk.Frame(self.root)
        bottom_frame.grid(row=4, column=0, columnspan=2, pady=5)

        tk.Button(
            bottom_frame,
            text="View Leaderboard",
            command=self.show_leaderboard,
            font=("Arial", 10),
            width=15
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            bottom_frame,
            text="Exit",
            command=self.root.quit,
            font=("Arial", 10),
            width=10
        ).pack(side=tk.LEFT, padx=5)

        # Binds the Enter key to login
        self.root.bind('<Return>', lambda e: self.login())

    def login(self):
        # handles login attempts
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        user = self.database.get_user(username)

        if user and verify_password(password, user[2], user[3]):
            self.current_user = {
                'id': user[0],
                'username': user[1],
                'balance': user[4]
            }

            # Starts the session
            session_id = self.database.start_session(
                self.current_user['id'],
                self.current_user['balance']
            )
            self.current_user['session_id'] = session_id

            # Closes the login window and starts the game
            self.root.destroy()
            RouletteGUIGame(self.current_user, self.database)
        else:
            messagebox.showerror("Login Failed", "Incorrect username or password")
            self.password_entry.delete(0, tk.END)

    def register(self):
        # Handles the registration attempts
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            # validates inputs
            username = validate_username(username)
            password = validate_password(password)

            # Hashes password
            password_hash, salt = hash_password(password)

            # Create users
            self.database.create_user(username, password_hash, salt)

            messagebox.showinfo(
                "Success",
                f"Account created successfully!\nWelcome, {username}!\n\nYou start with $1000."
            )

            # clears fields
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)

        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def show_leaderboard(self):
        #shows the leaderboard window
        show_leaderboard(self.root, self.database)

    def run(self):
        #starts the actual app/game
        self.root.mainloop()


def main():
    # main entry point of the game
    app = LoginWindow()
    app.run()


# starts the game
if __name__ == "__main__":
    main()