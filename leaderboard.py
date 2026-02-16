#creates the leaderboard gui

import tkinter as tk
from tkinter import ttk


class LeaderboardWindow:
    #class to display the leaderboard

    def __init__(self, parent, database):
        #creates leaderboard window
        self.database = database
        self.window = tk.Toplevel(parent)
        self.window.title("Leaderboard")
        self.window.geometry("500x400")
        self.window.resizable(False, False)

        self._create_widgets()
        self._load_leaderboard()

    def _create_widgets(self):
        #creates widgets/pop ups
        title_label = tk.Label(
            self.window,
            text="🏆 Leaderboard 🏆",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=10)

        # creates frame for treeview and scrollbar
        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # scrollbar
        scrollbar = tk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # treeview for the leaderboard data
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("rank", "username", "wins", "games", "winrate"),
            show="headings",
            yscrollcommand=scrollbar.set,
            height=15
        )

        # configure columns
        self.tree.heading("rank", text="Rank")
        self.tree.heading("username", text="Username")
        self.tree.heading("wins", text="Wins")
        self.tree.heading("games", text="Games")
        self.tree.heading("winrate", text="Win Rate")

        self.tree.column("rank", width=60, anchor=tk.CENTER)
        self.tree.column("username", width=150, anchor=tk.W)
        self.tree.column("wins", width=80, anchor=tk.CENTER)
        self.tree.column("games", width=80, anchor=tk.CENTER)
        self.tree.column("winrate", width=100, anchor=tk.CENTER)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # close button
        close_button = tk.Button(
            self.window,
            text="Close",
            command=self.window.destroy,
            font=("Arial", 11),
            width=15
        )
        close_button.pack(pady=10)

    def _load_leaderboard(self):
        """Load and display leaderboard data."""
        #delets existing data
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Gets leaderboard data
        data = self.database.get_leaderboard(limit=50)

        if not data:
            self.tree.insert("", tk.END, values=("", "No games played yet", "", "", ""))
            return

        # Inserts data with rankings
        for rank, (username, wins, total_games, win_rate) in enumerate(data, start=1):
            # Add medal emoji for top 3
            rank_display = rank
            if rank == 1:
                rank_display = "1: 🥇"
            elif rank == 2:
                rank_display = "2: 🥈"
            elif rank == 3:
                rank_display = "3: 🥉"

            self.tree.insert(
                "",
                tk.END,
                values=(
                    rank_display,
                    username,
                    wins,
                    total_games,
                    f"{win_rate:.1f}%"
                ),
                tags=('top3' if rank <= 3 else 'normal',)
            )

        # creates the top 3
        self.tree.tag_configure('top3', background='#FFD700', font=("Arial", 10, "bold"))
        self.tree.tag_configure('normal', font=("Arial", 10))


def show_leaderboard(parent, database):
    #shows the actual leaderboard window
    LeaderboardWindow(parent, database)