# Main game class/function
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageSequence
from config import numbers, colors
from ui.leaderboard import show_leaderboard


class RouletteGUIGame:
    def __init__(self, user, db):
        self.user = user
        self.db = db
        self.balance = user['balance']
        self.user_id = user['id']
        self.spinning = False

        # The below creates th tkinter user interfaces
        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window.title("Roulette 💲🤑🎰🤑💲 ")

        tk.Label(self.window, text="Roulette 💲🤑🎰🤑💲", font=("Arial", 16)).pack(pady=5)
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

        tk.Button(
            self.window,
            text="View Leaderboard",
            command=lambda: show_leaderboard(self.window, self.db)
        ).pack(pady=5)

        tk.Button(self.window, text="Close", command=self.safe_close).pack(pady=5)

        self.load_gif("roulette_spin.gif")
        self.window.mainloop()

    def safe_close(self):
        if self.spinning:
            return
        messagebox.showinfo("Goodbye", f"Thank you for playing! \nYou finished with ${self.balance}")
        self.db.end_session(self.user_id, self.balance)
        self.window.destroy()

    def load_gif(self, path):
        try:
            gif = Image.open(path)
            self.frames = [ImageTk.PhotoImage(frame.copy()) for frame in ImageSequence.Iterator(gif)]
            self.frame_count = len(self.frames)
        except FileNotFoundError:
            #if the gifs not found, it skips the animation so the game can still be played
            self.frames = []
            self.frame_count = 0
            print(f"Warning: {path} not found. Animation will be skipped.")

    def hide_gif(self):
        self.gif_label.config(image="")

    def on_close(self):
        messagebox.showinfo("Goodbye", f"Thank you for playing!\nYou finished with ${self.balance}")
        self.db.end_session(self.user_id, self.balance)
        self.window.destroy()

    def start_spin(self):
        if self.spinning:
            return

        # Validates inputs first
        try:
            bet_type = self.bet_type.get()
            bet_value_input = self.bet_value.get().strip()
            bet_amount_input = self.bet_amount.get().strip()

            # Checks if fields are empty
            if not bet_value_input:
                messagebox.showerror("Invalid Input", "Please enter a bet value")
                return

            if not bet_amount_input:
                messagebox.showerror("Invalid Input", "Please enter a bet amount")
                return

            bet_value = bet_value_input.lower()
            bet_amount = int(bet_amount_input)

            # Validates bet amount
            if bet_amount <= 0:
                messagebox.showerror("Invalid Bet", "Bet amount must be greater than 0")
                return

            if bet_amount > self.balance:
                messagebox.showerror("Insufficient Funds",
                                     f"Bet amount (${bet_amount}) exceeds your balance (${self.balance})")
                return

            #Validates the bet value based on bet type
            if bet_type == "number":
                bet_value = int(bet_value)
                if not 0 <= bet_value <= 36:
                    messagebox.showerror("Invalid Number",
                                         f"Number must be between 0 and 36\nYou entered: {bet_value}")
                    return

            elif bet_type == "color":
                if bet_value not in ["red", "black"]:
                    messagebox.showerror("Invalid Color",
                                         f"Color must be 'red' or 'black'\nYou entered: {bet_value}")
                    return

            elif bet_type == "odd_even":
                if bet_value not in ["odd", "even"]:
                    messagebox.showerror("Invalid Choice",
                                         f"Choice must be 'odd' or 'even'\nYou entered: {bet_value}")
                    return

            elif bet_type == "high_low":
                if bet_value not in ["high", "low"]:
                    messagebox.showerror("Invalid Choice",
                                         f"Choice must be 'high' or 'low'\nYou entered: {bet_value}")
                    return

        except ValueError as e:
            # Handle conversion errors (e.g., non-numeric input for number/amount)
            messagebox.showerror("Invalid Input",
                                 f"Please check your input:\n{str(e)}")
            return

        # start of the spinning process
        self.bet = {"type": bet_type, "value": bet_value, "amount": bet_amount}

        # Deducts the bet from the users balance immediately
        self.balance -= bet_amount
        self.balance_label.config(text=f"Balance: ${self.balance}")

        self.spinning = True
        self.spin_button.config(state=tk.DISABLED)
        self.result_label.config(text="Spinning...")

        # Show the GIF after all validations finish
        if self.frame_count > 0:
            self.gif_label.config(image=self.frames[0])
            self.animate(0)
        else:
            self.finish_spin()

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

        winnings = 0
        if payout > 0:
            #Calculates the total winnings (includes the original bet)
            winnings = self.bet["amount"] * payout
            # adds the winnings to users balance
            self.balance += winnings
            messagebox.showinfo(
                "Result",
                f"Result: {result} ({result_color})\n"
                f"You WON ${winnings}! 🥳\n"
                f"New balance: ${self.balance}"
            )
        else:
            # shiws the loss message, doesnt delete anything as deduction already taken place
            messagebox.showinfo(
                "Result",
                f"Result: {result} ({result_color})\n"
                f"You LOST ${self.bet['amount']}\n"
                f"New balance: ${self.balance}"
            )

        self.db.log_bet(
            self.user['session_id'],
            self.bet['type'],  # bet_type
            str(self.bet['value']),  # bet_value (converted to a string)
            self.bet['amount'],
            "Win" if payout > 0 else "Lose",
            winnings if payout > 0 else 0  # payout
        )

        win = payout > 0
        self.db.update_leaderboard(self.user_id, win)

        # Updates the users balance in the database
        self.db.update_user_balance(self.user_id, self.balance)
        self.balance_label.config(text=f"Balance: ${self.balance}")

        #hides the GIF after result
        self.hide_gif()

        self.spinning = False
        self.spin_button.config(state=tk.NORMAL)

        # Deleets the bet inputs for the next spin
        self.bet_value.delete(0, tk.END)
        self.bet_amount.delete(0, tk.END)

        # Check if they have the money to play again
        if self.balance <= 0:
            messagebox.showinfo("Game Over", "You're out of money!")
            self.db.end_session(self.user_id, self.balance)
            self.window.destroy()

    def check_win(self, bet, result):
        result_color = "green" if result == 0 else colors[result]

        if bet["type"] == "number" and bet["value"] == result:
            return 35

        if bet["type"] == "color" and bet["value"] == result_color:
            return 2

        if bet["type"] == "odd_even" and result != 0:
            is_even_result = (result % 2 == 0)
            is_even_bet = (bet["value"] == "even")
            if is_even_result == is_even_bet:
                return 2
            else:
                return 0

        if bet["type"] == "high_low":
            if result == 0:
                return 0
            is_high = result >= 19
            is_low = 1 <= result <= 18
            if (bet["value"] == "high" and is_high) or (bet["value"] == "low" and is_low):
                return 2
            else:
                return 0

        return 0