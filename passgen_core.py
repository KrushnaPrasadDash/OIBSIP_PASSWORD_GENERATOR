import secrets
import string

LOWERCASE = string.ascii_lowercase
UPPERCASE = string.ascii_uppercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{}|;:,.<>?"

AMBIGUOUS = "0O1lI|`'\"\\"


def build_charset(use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous=False):
    parts = []
    if use_lower:
        parts.append(LOWERCASE)
    if use_upper:
        parts.append(UPPERCASE)
    if use_digits:
        parts.append(DIGITS)
    if use_symbols:
        parts.append(SYMBOLS)

    if not parts:
        return ""

    pool = "".join(parts)
    if exclude_ambiguous:
        pool = "".join(c for c in pool if c not in AMBIGUOUS)
    return pool


def active_sets(use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous=False):
    sets = []
    if use_lower:
        s = LOWERCASE
        if exclude_ambiguous:
            s = "".join(c for c in s if c not in AMBIGUOUS)
        if s:
            sets.append(s)
    if use_upper:
        s = UPPERCASE
        if exclude_ambiguous:
            s = "".join(c for c in s if c not in AMBIGUOUS)
        if s:
            sets.append(s)
    if use_digits:
        s = DIGITS
        if exclude_ambiguous:
            s = "".join(c for c in s if c not in AMBIGUOUS)
        if s:
            sets.append(s)
    if use_symbols:
        s = SYMBOLS
        if exclude_ambiguous:
            s = "".join(c for c in s if c not in AMBIGUOUS)
        if s:
            sets.append(s)
    return sets


def generate_password(length, use_lower=True, use_upper=True, use_digits=True,
                      use_symbols=False, exclude_ambiguous=False,
                      require_each_type=True, no_adjacent_repeat=False):
    if length < 1:
        raise ValueError("length must be at least 1")

    charset = build_charset(use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous)
    if not charset:
        raise ValueError("pick at least one character type")

    sets = active_sets(use_lower, use_upper, use_digits, use_symbols, exclude_ambiguous)
    if require_each_type and length < len(sets):
        raise ValueError("length too short for the selected character types")

    chars = []
    if require_each_type:
        for s in sets:
            chars.append(secrets.choice(s))

    while len(chars) < length:
        pick = secrets.choice(charset)
        if no_adjacent_repeat and chars and pick == chars[-1]:
            continue
        chars.append(pick)

    secrets.SystemRandom().shuffle(chars)
    return "".join(chars)


def score_password(password, use_lower, use_upper, use_digits, use_symbols):
    if not password:
        return 0, "empty"

    score = 0
    score += min(len(password) * 4, 40)

    if use_lower and any(c in LOWERCASE for c in password):
        score += 10
    if use_upper and any(c in UPPERCASE for c in password):
        score += 10
    if use_digits and any(c in DIGITS for c in password):
        score += 10
    if use_symbols and any(c in SYMBOLS for c in password):
        score += 15

    unique_ratio = len(set(password)) / len(password)
    score += int(unique_ratio * 15)

    if score < 35:
        label = "weak"
    elif score < 60:
        label = "fair"
    elif score < 80:
        label = "good"
    else:
        label = "strong"

    return min(score, 100), label
