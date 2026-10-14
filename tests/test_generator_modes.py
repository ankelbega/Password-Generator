"""Teste për Passphrase, PIN dhe gjenerimin në grup."""

import pytest

from core.generator import generate_bulk, generate_passphrase, generate_pin
from core.wordlist import WORDLIST


def test_wordlist_has_at_least_300_words():
    assert len(WORDLIST) >= 300


def test_passphrase_has_requested_word_count():
    result = generate_passphrase(words=5, separator="-")
    assert len(result["password"].split("-")) == 5


@pytest.mark.parametrize(("separator", "expected"), [("space", " "), (".", "."), ("_", "_")])
def test_passphrase_separator(separator, expected):
    result = generate_passphrase(words=4, separator=separator)
    assert result["password"].count(expected) == 3


def test_passphrase_first_word_capitalization():
    phrase = generate_passphrase(words=4, capitalize="first")["password"]
    words = phrase.split("-")
    assert words[0][0].isupper()
    assert all(word == word.lower() for word in words[1:])


def test_passphrase_all_words_capitalized():
    phrase = generate_passphrase(words=4, capitalize="all")["password"]
    assert all(word[0].isupper() for word in phrase.split("-"))


def test_passphrase_optional_number_and_symbol_present():
    phrase = generate_passphrase(words=4, add_number=True, add_symbol=True)["password"]
    assert any(char.isdigit() for char in phrase)
    assert any(char in "!@#$%^&*()-_=+[]{};:,.<>?/" for char in phrase)


def test_passphrase_rejects_word_count_out_of_range():
    with pytest.raises(ValueError, match="Numri i fjalëve"):
        generate_passphrase(words=2)


def test_pin_length_and_digits():
    pin = generate_pin(length=8)["password"]
    assert len(pin) == 8
    assert pin.isdigit()


def test_pin_no_repeat():
    pin = generate_pin(length=10, no_repeat=True)["password"]
    assert len(set(pin)) == 10


def test_pin_no_all_same():
    for _ in range(20):
        pin = generate_pin(length=4, no_all_same=True)["password"]
        assert len(set(pin)) > 1


def test_pin_no_sequences():
    for _ in range(20):
        pin = generate_pin(length=8, no_sequences=True)["password"]
        assert not any(int(b) - int(a) == int(c) - int(b) in (1, -1)
                       for a, b, c in zip(pin, pin[1:], pin[2:]))


def test_pin_rejects_invalid_length():
    with pytest.raises(ValueError, match="Gjatësia e PIN-it"):
        generate_pin(length=3)


def test_bulk_passwords_are_unique():
    result = generate_bulk(count=25, mode="random", length=16)
    assert len(result["passwords"]) == 25
    assert len(set(result["passwords"])) == 25


def test_bulk_supports_passphrase():
    result = generate_bulk(count=3, mode="passphrase", words=4)
    assert len(result["passwords"]) == 3
    assert len(set(result["passwords"])) == 3


def test_bulk_rejects_count_out_of_range():
    with pytest.raises(ValueError, match="Numri i fjalëkalimeve"):
        generate_bulk(count=51)
