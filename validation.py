# validates user inputs

from config import (
    max_username_length, min_password_length, max_password_length,
    numbers, min_bet
)


class ValidationError(Exception):
    #Custom exception for validation errors."""
    pass

def validate_username(username: str) -> str:
    #validate username format.
    username = username.strip()
    if not username:
        raise ValidationError("Username cannot be empty")
    if len(username) > max_username_length:
        raise ValidationError(f"Username must be {max_username_length} characters or less")
    if not username.replace('_', '').replace('-', '').isalnum():
        raise ValidationError("Username can only contain letters, numbers, hyphens, and underscores")
    return username


def validate_password(password: str) -> str:
    #validates password formula
    if len(password) < min_password_length:
        raise ValidationError(f"Password must be at least {min_password_length} characters")
    if len(password) > max_password_length:
        raise ValidationError(f"Password must be {max_password_length} characters or less")
    return password


def validate_bet_amount(amount: int, balance: int) -> int:
    #Validate bet amount.
    if amount < min_bet:
        raise ValidationError(f"Minimum bet is ${min_bet}")
    if amount > balance:
        raise ValidationError(f"Insufficient funds. Your balance is ${balance} you brokeboy")
    return amount


def validate_number_bet(number: int) -> int:
    #validates a bet on a number
    if number not in numbers:
        raise ValidationError(f"Number must be between 0 and 36")
    return number


def validate_color_bet(color: str) -> str:
    #validstes a bet on a color
    color = color.lower().strip()
    if color not in ['red', 'black']:
        raise ValidationError("Color must be 'red' or 'black'")
    return color


def validate_odd_even_bet(choice: str) -> str:
    #Validates an odd/even bet.
    choice = choice.lower().strip()
    if choice not in ['odd', 'even']:
        raise ValidationError("Choice must be 'odd' or 'even'")
    return choice

def validate_high_low_bet(choice: str) -> str:
    #Validate a high/low bet.
    choice = choice.lower().strip()
    if choice not in ['high', 'low']:
        raise ValidationError("Choice must be 'high' or 'low'")
    return choice