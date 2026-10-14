"""Teste për gjeneratorin Random."""

import pytest

from core.generator import generate_random


def test_exact_length_and_entropy():
    result = generate_random(length=24)
    assert len(result["password"]) == 24
    assert result["entropy_bits"] > 0


def test_defaults_include_each_character_group():
    password = generate_random()["password"]
    assert any(char.islower() for char in password)
    assert any(char.isupper() for char in password)
    assert any(char.isdigit() for char in password)
    assert any(not char.isalnum() for char in password)


def test_custom_minimums_are_met():
    result = generate_random(length=20, min_lower=3, min_upper=2, min_digits=4, min_symbols=2)
    password = result["password"]
    assert sum(char.islower() for char in password) >= 3
    assert sum(char.isupper() for char in password) >= 2
    assert sum(char.isdigit() for char in password) >= 4
    assert sum(not char.isalnum() for char in password) >= 2


def test_exclude_similar_characters():
    password = generate_random(length=64, exclude_similar=True)["password"]
    assert not set(password) & set("il1LoO0")


def test_exclude_ambiguous_characters():
    password = generate_random(length=64, exclude_ambiguous=True)["password"]
    assert not set(password) & set("{}[]()/\\'\"~,;:.<>")


def test_custom_excluded_characters_are_absent():
    password = generate_random(length=64, exclude_chars="aZ7!")["password"]
    assert not set(password) & set("aZ7!")


def test_no_repeat():
    password = generate_random(length=30, no_repeat=True)["password"]
    assert len(set(password)) == len(password)


def test_no_consecutive_repeat():
    password = generate_random(length=64, no_consecutive_repeat=True)["password"]
    assert all(first != second for first, second in zip(password, password[1:]))


def test_no_sequences():
    password = generate_random(length=128, no_sequences=True)["password"]
    lowered = password.lower()
    assert all(not (a.isalnum() and b.isalnum() and c.isalnum() and
                    ord(b) - ord(a) == ord(c) - ord(b) in (1, -1))
               for a, b, c in zip(lowered, lowered[1:], lowered[2:]))


def test_first_character_is_letter():
    password = generate_random(length=32, first_char_letter=True)["password"]
    assert password[0].isalpha()


def test_starts_and_ends_with():
    result = generate_random(length=20, starts_with="Ab", ends_with="9!")
    assert result["password"].startswith("Ab")
    assert result["password"].endswith("9!")


def test_minimum_length_boundary():
    result = generate_random(length=4, use_lower=True, use_upper=True, use_digits=True,
                             use_symbols=True, min_lower=1, min_upper=1, min_digits=1, min_symbols=1)
    assert len(result["password"]) == 4


def test_maximum_length_boundary():
    assert len(generate_random(length=128)["password"]) == 128


def test_rejects_length_outside_range():
    with pytest.raises(ValueError, match="Gjatësia"):
        generate_random(length=3)
    with pytest.raises(ValueError, match="Gjatësia"):
        generate_random(length=129)


def test_rejects_minimums_that_exceed_length():
    with pytest.raises(ValueError, match="më e vogël"):
        generate_random(length=4, min_lower=2, min_upper=2, min_digits=1, min_symbols=1)


def test_rejects_empty_active_group_after_exclusions():
    with pytest.raises(ValueError, match="është bosh"):
        generate_random(use_lower=True, use_upper=False, use_digits=False, use_symbols=False,
                        exclude_chars="abcdefghijklmnopqrstuvwxyz")


def test_rejects_no_repeat_capacity_conflict():
    with pytest.raises(ValueError, match="më shumë karaktere unike"):
        generate_random(length=20, use_lower=True, use_upper=False, use_digits=False,
                        use_symbols=False, no_repeat=True)


def test_must_include_is_honored():
    password = generate_random(length=16, must_include="@x7")["password"]
    assert all(char in password for char in "@x7")


def test_rejects_unknown_options():
    with pytest.raises(ValueError, match="Parametër i panjohur"):
        generate_random(length=16, typo=True)


def test_disabled_character_groups_are_not_used():
    password = generate_random(length=32, use_lower=True, use_upper=False,
                               use_digits=False, use_symbols=False)["password"]
    assert password.islower()
