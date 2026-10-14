"""Gjenerim i sigurt i fjalëkalimeve të rastësishme."""

from __future__ import annotations

import math
import secrets
from collections.abc import Mapping
from typing import Any

from core.charsets import (
    AMBIGUOUS_CHARACTERS,
    CHARACTER_GROUPS,
    SIMILAR_CHARACTERS,
)
from core.wordlist import WORDLIST

_MAX_ATTEMPTS = 1000


def _as_bool(value: Any, name: str) -> bool:
    """Valido dhe kthe një vlerë boolean të parametrizuar."""
    if not isinstance(value, bool):
        raise ValueError(f"Parametri '{name}' duhet të jetë true ose false.")
    return value


def _as_nonnegative_int(value: Any, name: str) -> int:
    """Valido një numër të plotë jo-negativ, duke refuzuar boolean."""
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Parametri '{name}' duhet të jetë numër i plotë jo-negativ.")
    return value


def _has_sequence(password: str) -> bool:
    """Kontrollo për tri ose më shumë karaktere alfanumerike radhazi."""
    for index in range(len(password) - 2):
        first, second, third = password[index : index + 3]
        if not (first.isalnum() and second.isalnum() and third.isalnum()):
            continue
        if ord(second.lower()) - ord(first.lower()) == ord(third.lower()) - ord(second.lower()) in (1, -1):
            return True
    return False


def _rules_satisfied(
    password: str,
    *,
    no_consecutive_repeat: bool,
    no_sequences: bool,
    first_char_letter: bool,
    starts_with: str,
    ends_with: str,
) -> bool:
    """Kontrollo rregullat e fjalëkalimit që varen nga renditja."""
    if no_consecutive_repeat and any(a == b for a, b in zip(password, password[1:])):
        return False
    if no_sequences and _has_sequence(password):
        return False
    if first_char_letter and not password[0].isalpha():
        return False
    if starts_with and not password.startswith(starts_with):
        return False
    if ends_with and not password.endswith(ends_with):
        return False
    return True


def generate_random(**options: Any) -> dict[str, Any]:
    """Gjenero një fjalëkalim Random dhe entropinë e tij.

    Pranon opsionet Random të specifikimit. Kthen fjalëkalimin dhe entropinë
    në bit; gabimet e parametrave raportohen me ``ValueError`` në shqip.
    """
    allowed = {
        "length", "use_lower", "use_upper", "use_digits", "use_symbols",
        "custom_symbols", "exclude_similar", "exclude_ambiguous", "exclude_chars",
        "must_include", "min_lower", "min_upper", "min_digits", "min_symbols",
        "no_repeat", "no_consecutive_repeat", "no_sequences", "first_char_letter",
        "starts_with", "ends_with",
    }
    unknown = set(options) - allowed
    if unknown:
        raise ValueError(f"Parametër i panjohur: {sorted(unknown)[0]}.")

    length = options.get("length", 16)
    if isinstance(length, bool) or not isinstance(length, int) or not 4 <= length <= 128:
        raise ValueError("Gjatësia duhet të jetë numër i plotë nga 4 deri në 128.")

    enabled = {
        "lower": _as_bool(options.get("use_lower", True), "use_lower"),
        "upper": _as_bool(options.get("use_upper", True), "use_upper"),
        "digits": _as_bool(options.get("use_digits", True), "use_digits"),
        "symbols": _as_bool(options.get("use_symbols", True), "use_symbols"),
    }
    custom_symbols = options.get("custom_symbols")
    if custom_symbols is not None and not isinstance(custom_symbols, str):
        raise ValueError("Parametri 'custom_symbols' duhet të jetë tekst.")

    exclude_chars = options.get("exclude_chars", "")
    must_include = options.get("must_include", "")
    starts_with = options.get("starts_with", "")
    ends_with = options.get("ends_with", "")
    for name, value in (("exclude_chars", exclude_chars), ("must_include", must_include),
                        ("starts_with", starts_with), ("ends_with", ends_with)):
        if not isinstance(value, str):
            raise ValueError(f"Parametri '{name}' duhet të jetë tekst.")

    excluded = set(exclude_chars)
    if _as_bool(options.get("exclude_similar", False), "exclude_similar"):
        excluded.update(SIMILAR_CHARACTERS)
    if _as_bool(options.get("exclude_ambiguous", False), "exclude_ambiguous"):
        excluded.update(AMBIGUOUS_CHARACTERS)

    sets = dict(CHARACTER_GROUPS)
    if custom_symbols is not None:
        sets["symbols"] = custom_symbols
    groups = {name: "".join(char for char in sets[name] if char not in excluded)
              for name, active in enabled.items() if active}
    if not groups:
        raise ValueError("Aktivizo të paktën një grup karakteresh.")
    for name, chars in groups.items():
        if not chars:
            raise ValueError(f"Grupi i karaktereve '{name}' është bosh pas përjashtimeve.")

    minima = {
        name: _as_nonnegative_int(options.get(f"min_{name}", 1), f"min_{name}")
        for name in groups
    }
    required_count = sum(minima.values()) + len(must_include)
    if length < required_count:
        raise ValueError("Gjatësia është më e vogël se shuma e karaktereve të detyrueshme.")

    no_repeat = _as_bool(options.get("no_repeat", False), "no_repeat")
    no_consecutive_repeat = _as_bool(options.get("no_consecutive_repeat", False), "no_consecutive_repeat")
    no_sequences = _as_bool(options.get("no_sequences", False), "no_sequences")
    first_char_letter = _as_bool(options.get("first_char_letter", False), "first_char_letter")
    alphabet = "".join(dict.fromkeys("".join(groups.values())))
    if no_repeat and length > len(alphabet):
        raise ValueError("Gjatësia kërkon më shumë karaktere unike sesa janë në dispozicion.")
    if any(char not in alphabet for char in must_include + starts_with + ends_with):
        raise ValueError("Karakteret e detyrueshme ose prefiksi/sufiksi nuk gjenden në grupet aktive.")
    if len(starts_with) + len(ends_with) > length:
        raise ValueError("Prefiksi dhe sufiksi janë më të gjatë se fjalëkalimi.")
    if starts_with and ends_with and len(starts_with) + len(ends_with) > length:
        raise ValueError("Prefiksi dhe sufiksi mbivendosen jashtë gjatësisë së lejuar.")

    required: list[str] = list(starts_with + ends_with)
    for name, minimum in minima.items():
        group_chars = groups[name]
        already = sum(char in group_chars for char in required)
        if already < minimum:
            required.extend(secrets.choice(group_chars) for _ in range(minimum - already))
    required.extend(must_include)
    if len(required) > length:
        raise ValueError("Karakteret e detyrueshme janë më shumë se gjatësia e kërkuar.")
    if no_repeat and len(set(required)) != len(required):
        raise ValueError("Rregulli pa përsëritje bie ndesh me karakteret e detyrueshme.")

    pool = alphabet
    for _ in range(_MAX_ATTEMPTS):
        chars = list(required)
        while len(chars) < length:
            available = pool
            if no_repeat:
                available = "".join(char for char in available if char not in chars)
            if not available:
                break
            chars.append(secrets.choice(available))
        if len(chars) != length:
            break
        # Fisher-Yates via the CSPRNG, preserving fixed prefix/suffix positions.
        middle_end = length - len(ends_with) if ends_with else length
        middle_start = len(starts_with)
        middle = chars[middle_start:middle_end]
        for index in range(len(middle) - 1, 0, -1):
            swap_index = secrets.randbelow(index + 1)
            middle[index], middle[swap_index] = middle[swap_index], middle[index]
        candidate = starts_with + "".join(middle) + ends_with
        if no_repeat and len(set(candidate)) != length:
            continue
        if any(sum(char in group for char in candidate) < minimum for name, minimum in minima.items()
                 for group in (groups[name],)):
            continue
        if not _rules_satisfied(candidate, no_consecutive_repeat=no_consecutive_repeat,
                                no_sequences=no_sequences, first_char_letter=first_char_letter,
                                starts_with=starts_with, ends_with=ends_with):
            continue
        if must_include and not all(char in candidate for char in must_include):
            continue
        entropy = length * math.log2(len(alphabet))
        return {"password": candidate, "entropy_bits": round(entropy, 2)}
    raise ValueError("Nuk u gjet fjalëkalim që plotëson rregullat pas 1000 tentativash.")


def generate_random_from_options(options: Mapping[str, Any]) -> dict[str, Any]:
    """Ndërfaqe e përshtatshme që merr parametrat si mapping."""
    return generate_random(**dict(options))


def generate_passphrase(
    words: int = 4,
    separator: str = "-",
    capitalize: str = "none",
    add_number: bool = False,
    add_symbol: bool = False,
) -> dict[str, Any]:
    """Gjenero passphrase me fjalë të zgjedhura nga CSPRNG."""
    if isinstance(words, bool) or not isinstance(words, int) or not 3 <= words <= 10:
        raise ValueError("Numri i fjalëve duhet të jetë nga 3 deri në 10.")
    separators = {"space": " ", "dot": ".", ".": ".", "_": "_", "-": "-"}
    if separator == "random":
        actual_separator = secrets.choice(("-", " ", ".", "_"))
    elif separator in separators:
        actual_separator = separators[separator]
    else:
        raise ValueError("Separatori duhet të jetë '-', 'space', '.', '_', ose 'random'.")
    if capitalize not in {"none", "first", "all", "random"}:
        raise ValueError("Kapitalizimi duhet të jetë none, first, all ose random.")
    if not isinstance(add_number, bool) or not isinstance(add_symbol, bool):
        raise ValueError("Opsionet add_number dhe add_symbol duhet të jenë true ose false.")

    selected = [secrets.choice(WORDLIST) for _ in range(words)]
    if capitalize == "first":
        selected[0] = selected[0].capitalize()
    elif capitalize == "all":
        selected = [word.capitalize() for word in selected]
    elif capitalize == "random":
        selected = [word.capitalize() if secrets.randbelow(2) else word for word in selected]
    phrase = actual_separator.join(selected)
    entropy = words * math.log2(len(WORDLIST))
    if add_number:
        number = str(secrets.randbelow(100))
        entropy += math.log2(100)
        if secrets.randbelow(2):
            phrase += number
        else:
            insertion = secrets.randbelow(len(phrase) + 1)
            phrase = phrase[:insertion] + number + phrase[insertion:]
    if add_symbol:
        symbol = secrets.choice("!@#$%^&*()-_=+[]{};:,.<>?/")
        entropy += math.log2(len("!@#$%^&*()-_=+[]{};:,.<>?/"))
        if secrets.randbelow(2):
            phrase += symbol
        else:
            insertion = secrets.randbelow(len(phrase) + 1)
            phrase = phrase[:insertion] + symbol + phrase[insertion:]
    return {"password": phrase, "entropy_bits": round(entropy, 2)}


def generate_pin(
    length: int = 4,
    no_repeat: bool = False,
    no_sequences: bool = False,
    no_all_same: bool = False,
) -> dict[str, Any]:
    """Gjenero PIN numerik, me refuzim të sekuencave dhe përsëritjeve sipas opsioneve."""
    if isinstance(length, bool) or not isinstance(length, int) or not 4 <= length <= 12:
        raise ValueError("Gjatësia e PIN-it duhet të jetë nga 4 deri në 12.")
    no_repeat = _as_bool(no_repeat, "no_repeat")
    no_sequences = _as_bool(no_sequences, "no_sequences")
    no_all_same = _as_bool(no_all_same, "no_all_same")
    if no_repeat and length > 10:
        raise ValueError("PIN pa përsëritje nuk mund të jetë më i gjatë se 10 shifra.")

    for _ in range(_MAX_ATTEMPTS):
        if no_repeat:
            digits = list("0123456789")
            for index in range(len(digits) - 1, 0, -1):
                swap_index = secrets.randbelow(index + 1)
                digits[index], digits[swap_index] = digits[swap_index], digits[index]
            pin = "".join(digits[:length])
        else:
            pin = "".join(secrets.choice("0123456789") for _ in range(length))
        if no_all_same and len(set(pin)) == 1:
            continue
        if no_sequences and _has_digit_sequence(pin):
            continue
        if _looks_like_date(pin):
            continue
        return {"password": pin, "entropy_bits": round(length * math.log2(10), 2)}
    raise ValueError("Nuk u gjet PIN që plotëson rregullat pas 1000 tentativash.")


def _has_digit_sequence(pin: str) -> bool:
    """Gjej seri shifrash rritëse ose zbritëse me gjatësi të paktën tri."""
    for index in range(len(pin) - 2):
        run = pin[index : index + 3]
        if int(run[1]) - int(run[0]) == int(run[2]) - int(run[1]) in (1, -1):
            return True
    return False


def _looks_like_date(pin: str) -> bool:
    """Refuzo formate të zakonshme datash (DDMM, MMDD, DDMMYY, DDMMYYYY)."""
    if len(pin) not in {4, 6, 8}:
        return False
    candidates: list[tuple[str, str, str]] = []
    if len(pin) == 4:
        candidates.extend(((pin[:2], pin[2:], ""), (pin[2:], pin[:2], "")))
    elif len(pin) == 6:
        candidates.append((pin[:2], pin[2:4], pin[4:]))
        candidates.append((pin[4:], pin[2:4], pin[:2]))
    else:
        candidates.append((pin[:2], pin[2:4], pin[4:]))
        candidates.append((pin[6:], pin[4:6], pin[:4]))
    for day_text, month_text, year_text in candidates:
        day, month = int(day_text), int(month_text)
        if not 1 <= day <= 31 or not 1 <= month <= 12:
            continue
        if not year_text:
            return True
        year = int(year_text)
        if (len(year_text) == 2 and 0 <= year <= 99) or (len(year_text) == 4 and 1900 <= year <= 2099):
            return True
    return False


def generate_bulk(count: int = 1, mode: str = "random", **options: Any) -> dict[str, Any]:
    """Gjenero një grup fjalëkalimesh unike me opsione të përbashkëta."""
    if isinstance(count, bool) or not isinstance(count, int) or not 1 <= count <= 50:
        raise ValueError("Numri i fjalëkalimeve duhet të jetë nga 1 deri në 50.")
    generators = {
        "random": generate_random,
        "passphrase": generate_passphrase,
        "pin": generate_pin,
    }
    if mode not in generators:
        raise ValueError("Mënyra duhet të jetë random, passphrase ose pin.")
    passwords: list[str] = []
    entropy_bits: float | None = None
    attempts = 0
    while len(passwords) < count and attempts < count * _MAX_ATTEMPTS:
        result = generators[mode](**options)
        entropy_bits = result["entropy_bits"]
        if result["password"] not in passwords:
            passwords.append(result["password"])
        attempts += 1
    if len(passwords) != count:
        raise ValueError("Nuk mund të gjenerohen mjaft fjalëkalime unike me këto parametra.")
    return {"passwords": passwords, "entropy_bits": entropy_bits}
