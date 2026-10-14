"""Vlerësimi lokal i fuqisë së fjalëkalimeve dhe sugjerimet në shqip."""

from __future__ import annotations

import math
import re
from collections.abc import Sequence
from typing import Any

from core.common_data import COMMON_PASSWORDS, DICTIONARY_WORDS, KEYBOARD_SEQUENCES

_LEET_TRANSLATION = str.maketrans({"@": "a", "0": "o", "1": "l", "3": "e", "$": "s", "5": "s", "7": "t"})
_LEVELS = (
    (20, "Shumë i dobët"),
    (40, "I dobët"),
    (60, "Mesatar"),
    (80, "I fortë"),
    (100, "Shumë i fortë"),
)


def _format_duration(seconds: float) -> str:
    """Formato sekondat në njësi të kuptueshme për përdoruesin."""
    if not math.isfinite(seconds):
        return "miliarda vjet"
    if seconds < 1:
        return "më pak se 1 sekondë"
    units: Sequence[tuple[float, str]] = (
        (60 * 60 * 24 * 365.25 * 1_000_000_000, "miliarda vjet"),
        (60 * 60 * 24 * 365.25 * 100, "shekuj"),
        (60 * 60 * 24 * 365.25, "vite"),
        (60 * 60 * 24, "ditë"),
        (60 * 60, "orë"),
        (60, "minuta"),
        (1, "sekonda"),
    )
    for threshold, label in units:
        if seconds >= threshold:
            quantity = seconds / threshold
            if label == "sekonda":
                return f"{quantity:.0f} sekonda"
            return f"{quantity:.1f} {label}"
    return "më pak se 1 sekondë"


def _contains_sequence(value: str) -> list[str]:
    """Kthe nënvargjet alfabetike ose numerike me hapa të njëpasnjëshëm."""
    found: list[str] = []
    for index in range(len(value) - 2):
        part = value[index : index + 3]
        if not (part.isalnum() and (part.isdigit() or part.isalpha())):
            continue
        normalized = part.lower()
        if ord(normalized[1]) - ord(normalized[0]) == ord(normalized[2]) - ord(normalized[1]) in (1, -1):
            found.append(part)
    return found


def _detect_repeated(password: str) -> list[str]:
    """Zbulo grupe të përsëritura, përfshirë shabllone ciklike."""
    findings: list[str] = []
    repeated_chars = re.search(r"(.)\1{2,}", password)
    if repeated_chars:
        findings.append(f"Karakteri '{repeated_chars.group(1)}' përsëritet {len(repeated_chars.group(0))} herë")
    for width in range(1, min(5, len(password) // 2 + 1)):
        if len(password) >= width * 2 and len(password) % width == 0:
            chunk = password[:width]
            if chunk * (len(password) // width) == password:
                findings.append(f"Shablloni '{chunk}' përsëritet")
                break
    return findings


def _has_date_pattern(password: str) -> bool:
    """Kontrollo data të zakonshme në fillim ose në fund."""
    return bool(
        re.search(r"(?:19|20)\d{2}$|^(?:19|20)\d{2}", password)
        or re.search(r"(?:\d{2}[/.-]?){2}(?:19|20)?\d{2}$", password)
        or re.search(r"^\d{2}[/.-]?\d{2}(?:19|20)?\d{2}", password)
    )


def _find_dictionary_word(normalized: str) -> str | None:
    """Gjej fjalë të zakonshme të plota brenda fjalëkalimit."""
    for word in sorted(DICTIONARY_WORDS, key=len, reverse=True):
        if len(word) >= 4 and word in normalized:
            return word
    return None


def analyze(password: str, user_inputs: Sequence[str] | None = None) -> dict[str, Any]:
    """Analizo fjalëkalimin dhe kthe rezultat me pikë, sinjale dhe këshilla.

    Analiza bëhet vetëm në procesin lokal të thirrësit; fjalëkalimi nuk ruhet
    dhe nuk regjistrohet. ``user_inputs`` mund të përmbajë emër ose email.
    """
    if not isinstance(password, str):
        raise ValueError("Fjalëkalimi duhet të jetë tekst.")
    if user_inputs is None:
        user_inputs = ()
    if isinstance(user_inputs, str) or not isinstance(user_inputs, Sequence) or any(
        not isinstance(item, str) for item in user_inputs
    ):
        raise ValueError("user_inputs duhet të jetë listë vlerash tekstuale.")

    length = len(password)
    has_lower = any(char.islower() for char in password)
    has_upper = any(char.isupper() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_symbol = any(not char.isalnum() for char in password)
    other_unicode = sum(not (char.isascii() and (char.isalpha() or char.isdigit() or not char.isalnum()))
                        for char in password)
    # Standard pool estimates follow the requested 26/26/10/33 model.
    charset_size = (26 if has_lower else 0) + (26 if has_upper else 0) + (10 if has_digit else 0)
    if has_symbol:
        charset_size += 33
    charset_size += other_unicode
    entropy = length * math.log2(charset_size) if charset_size > 1 else 0.0
    effective_entropy = entropy
    score = min(100, int(round(entropy * 1.15)))
    checks = {
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "length_ok": length >= 12,
    }
    penalties: list[dict[str, Any]] = []
    suggestions: list[str] = []

    def penalize(kind: str, detail: str, points: int, entropy_bits: float = 0.0) -> None:
        """Regjistro penalizim duke kufizuar rezultatin dhe entropinë."""
        nonlocal score, effective_entropy
        penalties.append({"type": kind, "detail": detail, "points": -points})
        score -= points
        effective_entropy = max(0.0, effective_entropy - entropy_bits)

    normalized = password.casefold()
    leet_normalized = password.lower().translate(_LEET_TRANSLATION)
    common_match = normalized in COMMON_PASSWORDS
    leet_match = leet_normalized in COMMON_PASSWORDS
    if common_match or leet_match:
        match = normalized if common_match else leet_normalized
        penalize("common", f"Fjalëkalim i zakonshëm ose variant leet: '{match}'", 95, entropy)
        suggestions.append("Mos përdor fjalëkalime të zakonshme si 'password' ose variante të tyre.")
        score = min(score, 5)
        effective_entropy = min(effective_entropy, math.log2(100))

    sequences = _contains_sequence(password)
    if sequences:
        penalize("sequence", f"Sekuencë e njëpasnjëshme: '{sequences[0]}'", min(24, 8 * len(sequences)), 4.0 * len(sequences))
        suggestions.append(f"Shmang sekuencën '{sequences[0]}'.")
    keyboard_match = next((sequence for sequence in KEYBOARD_SEQUENCES if sequence in normalized), None)
    if keyboard_match:
        penalize("keyboard", f"Sekuencë tastiere: '{keyboard_match}'", 20, 10.0)
        suggestions.append(f"Shmang modelin e tastierës '{keyboard_match}'.")

    repeated = _detect_repeated(password)
    for detail in repeated:
        penalize("repetition", detail, 12 if "Shablloni" in detail else 10, 8.0)
        suggestions.append("Shmang përsëritjen e të njëjtit karakter ose shabllon.")
    if _has_date_pattern(password):
        penalize("date", "Përmban një model të mundshëm date në fillim ose në fund", 15, 10.0)
        suggestions.append("Mos përdor data personale ose vite të dukshme.")

    dictionary_word = _find_dictionary_word(leet_normalized)
    if dictionary_word and not (common_match or leet_match):
        penalize("dictionary", f"Përmban fjalën e zakonshme '{dictionary_word}'", 12, 8.0)
        suggestions.append("Shmang fjalët e plota; përdor një frazë të rastësishme me disa fjalë.")

    if length < 8:
        penalize("short", "Më pak se 8 karaktere", 25, 12.0)
        suggestions.append("Shto të paktën 4 karaktere; syno 16 ose më shumë.")
    elif length < 12:
        penalize("short", "Më pak se 12 karaktere", 12, 5.0)
        suggestions.append("Zgjate fjalëkalimin në të paktën 12 karaktere.")
    if has_lower and not (has_upper or has_digit or has_symbol):
        penalize("single_charset", "Përmban vetëm shkronja të vogla", 12, 5.0)
        suggestions.append("Përziej shkronja, numra dhe simbole ose përdor një frazë të gjatë.")
    elif has_digit and not (has_lower or has_upper or has_symbol):
        penalize("single_charset", "Përmban vetëm shifra", 18, 8.0)
        suggestions.append("Mos përdor vetëm shifra.")
    elif (has_lower or has_upper) and not (has_digit or has_symbol):
        penalize("letters_only", "Përmban vetëm shkronja", 10, 4.0)
        suggestions.append("Shto numra ose simbole, ose përdor një frazë më të gjatë.")

    lowered_for_user = leet_normalized.casefold()
    for item in user_inputs:
        candidate = item.strip().casefold()
        candidates = [candidate]
        if "@" in candidate:
            candidates.extend(candidate.split("@", 1))
        if any(part and len(part) >= 3 and part in lowered_for_user for part in candidates):
            penalize("user_input", "Përmban emrin ose emailin e dhënë", 25, 15.0)
            suggestions.append("Mos përfshi emrin ose emailin tënd në fjalëkalim.")
            break

    unique_ratio = len(set(password)) / length if length else 0.0
    if length > 16:
        bonus = min(12, (length - 16) * 0.7)
        score += bonus
    if length > 24:
        score += min(8, (length - 24) * 0.4)
    if all((has_lower, has_upper, has_digit, has_symbol)):
        score += 8
    score += max(0.0, (unique_ratio - 0.5) * 20)
    score = max(0, min(100, int(round(score))))
    if common_match or leet_match:
        score = min(score, 5)

    if not suggestions:
        suggestions.append("Mos e ripërdor këtë fjalëkalim dhe ruaje në një menaxher fjalëkalimesh.")
    # Keep suggestions unique while preserving the order of discovered issues.
    suggestions = list(dict.fromkeys(suggestions))
    level = next(label for threshold, label in _LEVELS if score <= threshold)
    guesses = 2 ** max(0.0, effective_entropy - 1)
    rates = {
        "online_throttled": 100 / 3600,
        "online_fast": 10_000,
        "offline_slow_hash": 10_000,
        "offline_fast_hash": 100_000_000_000,
    }
    crack_time = {scenario: _format_duration(guesses / rate) for scenario, rate in rates.items()}
    return {
        "score": score,
        "level": level,
        "entropy_bits": round(entropy, 2),
        "length": length,
        "charset_size": charset_size,
        "crack_time": crack_time,
        "checks": checks,
        "penalties": penalties,
        "suggestions": suggestions,
    }
