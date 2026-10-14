"""Teste për analizën e forcës së fjalëkalimeve."""

import pytest

from core.common_data import COMMON_PASSWORDS
from core.strength import analyze


def test_common_password_has_low_score():
    assert analyze("password")["score"] <= 5


def test_common_list_has_at_least_200_entries():
    assert len(COMMON_PASSWORDS) >= 200


def test_long_random_style_password_has_high_score():
    result = analyze("aZ8!kQ2@vN5#xR9$Lm4%pT7^")
    assert result["score"] >= 80
    assert result["level"] == "Shumë i fortë"


def test_leet_password_is_detected_as_common():
    result = analyze("p@ssw0rd")
    assert result["score"] <= 5
    assert any(item["type"] == "common" for item in result["penalties"])


def test_sequence_is_penalized():
    result = analyze("abcdX!9z")
    assert any(item["type"] == "sequence" for item in result["penalties"])


def test_repeated_characters_are_penalized():
    result = analyze("aaaaB7!x")
    assert any(item["type"] == "repetition" for item in result["penalties"])


def test_repeated_template_is_penalized():
    result = analyze("abcabc")
    assert any(item["type"] == "repetition" and "Shablloni" in item["detail"]
               for item in result["penalties"])


def test_keyboard_sequence_is_detected():
    result = analyze("qwertyX7!")
    assert any(item["type"] == "keyboard" for item in result["penalties"])


def test_dictionary_word_inside_password_is_detected():
    result = analyze("monkey2024!")
    assert any(item["type"] == "dictionary" for item in result["penalties"])


def test_date_pattern_is_detected():
    result = analyze("Strong!2024")
    assert any(item["type"] == "date" for item in result["penalties"])


def test_user_input_is_detected():
    result = analyze("Alice-Strong-91!", user_inputs=["alice@example.com"])
    assert any(item["type"] == "user_input" for item in result["penalties"])


def test_result_has_required_shape():
    result = analyze("OnlyLetters")
    assert set(result) == {"score", "level", "entropy_bits", "length", "charset_size",
                           "crack_time", "checks", "penalties", "suggestions"}
    assert set(result["crack_time"]) == {"online_throttled", "online_fast",
                                          "offline_slow_hash", "offline_fast_hash"}


def test_empty_password_is_supported_safely():
    result = analyze("")
    assert result["score"] == 0
    assert result["length"] == 0


def test_rejects_non_string_password():
    with pytest.raises(ValueError, match="duhet të jetë tekst"):
        analyze(123)  # type: ignore[arg-type]


def test_rejects_invalid_user_inputs():
    with pytest.raises(ValueError, match="user_inputs"):
        analyze("valid", user_inputs="name")
