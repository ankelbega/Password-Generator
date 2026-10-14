"""Grupe karakteresh dhe konstante për gjenerimin e fjalëkalimeve."""

LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS = "0123456789"
STANDARD_SYMBOLS = "!@#$%^&*()-_=+[]{};:,.<>?/"

SIMILAR_CHARACTERS = "il1LoO0"
AMBIGUOUS_CHARACTERS = "{}[]()/\\'\"~,;:.<>"

CHARACTER_GROUPS = {
    "lower": LOWERCASE,
    "upper": UPPERCASE,
    "digits": DIGITS,
    "symbols": STANDARD_SYMBOLS,
}
