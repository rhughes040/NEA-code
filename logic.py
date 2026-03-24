# core game logic

import secrets
from typing import Dict, Tuple
from config import (
    numbers, colours,
    number_bet_payout, colour_bet_payout,
    odd_even_payout, high_low_payout
)


class RouletteLogic:
    # main game class

    def __init__(self):
        self.numbers = numbers
        self.colours = colours

    def spin_wheel(self) -> int:
        # spins the wheel and generates a random number
        return secrets.choice(self.numbers)

    def get_number_colour(self, number: int) -> str:
        # gets the colour of the result
        return self.colours.get(number, 'green')

    def check_win(self, bet: Dict, result: int) -> Tuple[bool, int]:
        # checks if the bet was won and calculates the payout
        result_colour = self.get_number_colour(result)
        bet_type = bet['type']
        bet_value = bet['value']

        # single number bet (35:1 payout)
        if bet_type == 'number':
            if bet_value == result:
                return True, number_bet_payout
            return False, 0

        # colour bet (2:1 payout)
        if bet_type == 'colour':
            if bet_value == result_colour:
                return True, colour_bet_payout
            return False, 0

        # odd and even bet (2:1 payout, 0 loses for 0)
        if bet_type == 'odd_even':
            if result == 0:  # Zero loses
                return False, 0

            is_even = (result % 2 == 0)
            if (bet_value == 'even' and is_even) or (bet_value == 'odd' and not is_even):
                return True, odd_even_payout
            return False, 0

        # high/low bet (2:1 payout, 0 loses)
        if bet_type == 'high_low':
            if result == 0:  # Zero loses
                return False, 0

            if bet_value == 'high' and result >= 19:
                return True, high_low_payout
            elif bet_value == 'low' and 1 <= result <= 18:
                return True, high_low_payout
            return False, 0

        return False, 0

    def format_result(self, result: int) -> str:
        # creates a output display for the result
        colour = self.get_number_colour(result)
        return f"{result} ({colour})"