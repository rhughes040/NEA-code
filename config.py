#the configeration constants for my program

# Game Constants
numbers = list(range(0, 37))

colors = {
    0: 'green',
    1: 'red', 2: 'black', 3: 'red', 4: 'black',
    5: 'red', 6: 'black', 7: 'red', 8: 'black', 9: 'red',
    10: 'black', 11: 'black', 12: 'red', 13: 'black',
    14: 'red', 15: 'black', 16: 'red', 17: 'black',
    18: 'red', 19: 'red', 20: 'black', 21: 'red',
    22: 'black', 23: 'red', 24: 'black', 25: 'red',
    26: 'black', 27: 'red', 28: 'black', 29: 'black',
    30: 'red', 31: 'black', 32: 'red', 33: 'black',
    34: 'red', 35: 'black', 36: 'red'
}

# Betting
starting_balance = 1000
min_bet = 1
number_bet_payout = 35
color_bet_payout = 2
odd_even_payout = 2
high_low_payout = 2

# Security
salt_length = 32  # the length of the salt added to the hashed password
hash_iterations = 600000  # the amount of iterations used when hashing
hash_algorithm = 'sha256'  # the specific hash function

# Database
db_name = "roulette.db"

# user interface
window_title = "Roulette Game"
gif_animation_delay = 50  # milliseconds, cuts out any errors caused by simultaneous spinning
gif_path = "assets/roulette_spin.gif"

# Input Validation
max_username_length = 30
min_password_length = 4
max_password_length = 128