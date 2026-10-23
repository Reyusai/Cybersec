"""
Password Strength Checker (educational project)
===============================================
A small Flask website that estimates how strong a password is.

Privacy rules followed by this program:
  * The password is read from a POST form (so it is never placed in the URL).
  * It is processed only in memory to build the immediate response.
  * It is never saved, logged, printed, sent to another service, or put in a database.
  * The password is never written back into the page (the box is always empty).

Run with:  python app.py   then open  http://127.0.0.1:5000
"""

import re

from flask import Flask, render_template_string, request

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
MAX_LENGTH = 128  # Refuse very long input so the page stays fast and simple.

# A tiny sample of very common passwords. Real checkers use lists with millions.
COMMON_PASSWORDS = {
    "password", "123456", "12345678", "123456789", "1234567890", "qwerty",
    "qwerty123", "abc123", "letmein", "welcome", "admin", "iloveyou",
    "monkey", "dragon", "football", "baseball", "sunshine", "princess",
    "login", "master", "hello", "freedom", "whatever", "trustno1",
    "111111", "000000", "123123", "password1", "starwars", "superman",
    "shadow", "michael", "jennifer", "charlie", "computer",
}

# Attackers know that people swap letters for look-alike symbols ("p@ssw0rd").
# This table converts those symbols back to letters before we check the list.
LEET_TABLE = str.maketrans({
    "@": "a", "4": "a", "0": "o", "1": "i",
    "3": "e", "$": "s", "5": "s", "7": "t", "!": "i",
})

# Straight-line runs that are easy to guess (forwards or backwards).
SEQUENCES = [
    "abcdefghijklmnopqrstuvwxyz",
    "0123456789",
    "qwertyuiop",   # keyboard rows
    "asdfghjkl",
    "zxcvbnm",
]


# ---------------------------------------------------------------------------
# Helper functions (each one checks a single idea, so they are easy to explain)
# ---------------------------------------------------------------------------
def has_sequence(text):
    """True if text contains 3+ characters in a row like 'abc', '321' or 'qwe'."""
    text = text.lower()
    for seq in SEQUENCES:
        for version in (seq, seq[::-1]):          # forwards and backwards
            for i in range(len(version) - 2):
                if version[i:i + 3] in text:
                    return True
    return False


def has_repeats(text):
    """True if the same character appears 3+ times in a row, like 'aaa'."""
    return re.search(r"(.)\1{2,}", text) is not None


def is_common_password(lowered, normalized):
    """True if the whole password is on the common-password list."""
    return lowered in COMMON_PASSWORDS or normalized in COMMON_PASSWORDS


def contains_common_word(lowered, normalized):
    """True if the password contains a common password/word (4+ characters)."""
    for word in COMMON_PASSWORDS:
        if len(word) >= 4 and (word in lowered or word in normalized):
            return True
    return False


def rating_for(score):
    """Convert a 0-100 score into a label and a CSS colour class."""
    if score < 20:
        return "Very Weak", "very-weak"
    if score < 40:
        return "Weak", "weak"
    if score < 60:
        return "Moderate", "moderate"
    if score < 80:
        return "Strong", "strong"
    return "Very Strong", "very-strong"


# ---------------------------------------------------------------------------
# Main scoring logic
# ---------------------------------------------------------------------------
def evaluate_password(password):
    """
    Score a password from 0 to 100 using simple, explainable rules.

    POINTS YOU CAN EARN (maximum 100)
      Length ............ 2 points per character, up to 20 characters  -> 40
      Lowercase letters . 10 points if present                         -> 10
      Uppercase letters . 10 points if present                         -> 10
      Digits ............ 10 points if present                         -> 10
      Symbols ........... 10 points if present                         -> 10
      Unique characters . 2 points per different character, up to 10  -> 20

    PENALTIES
      Contains a common password/word ........ -20
      Same character 3+ times in a row ....... -10
      Sequence such as abc, 123, qwe ......... -15
      Only one type of character ............. -10

    HARD LIMITS (applied last)
      Password is on the common list .... score cannot exceed 10
      Shorter than 8 characters ......... score cannot exceed 35
    """
    breakdown = []   # (rule, points) rows shown in the results table
    strengths = []   # things the password does well
    tips = []        # suggestions for improvement
    score = 0

    lowered = password.lower()
    normalized = lowered.translate(LEET_TABLE)
    length = len(password)

    # --- 1. Length -------------------------------------------------------
    length_points = min(length, 20) * 2
    score += length_points
    breakdown.append((f"Length ({length} characters)", f"+{length_points}"))
    if length >= 12:
        strengths.append("Good length: 12 or more characters.")
    else:
        tips.append("Use at least 12 characters. A passphrase of several unrelated words works well.")

    # --- 2. Character variety -------------------------------------------
    has_lower = any(ch.islower() for ch in password)
    has_upper = any(ch.isupper() for ch in password)
    has_digit = any(ch.isdigit() for ch in password)
    has_symbol = any(not ch.isalnum() for ch in password)  # spaces count too

    variety_rules = [
        (has_lower, "Lowercase letters", "Add lowercase letters (a-z)."),
        (has_upper, "Uppercase letters", "Add uppercase letters (A-Z)."),
        (has_digit, "Digits", "Add some digits (0-9)."),
        (has_symbol, "Symbols", "Add a symbol such as ! ? # % or a space."),
    ]
    classes_used = 0
    for present, label, advice in variety_rules:
        if present:
            score += 10
            classes_used += 1
            breakdown.append((label, "+10"))
            strengths.append(f"Contains {label.lower()}.")
        else:
            breakdown.append((label, "0"))
            tips.append(advice)

    # --- 3. Unique characters -------------------------------------------
    unique_points = min(len(set(password)), 10) * 2
    score += unique_points
    breakdown.append((f"Different characters ({len(set(password))})", f"+{unique_points}"))
    if unique_points < 20:
        tips.append("Use more different characters; repeating the same ones weakens a password.")

    # --- 4. Penalties ----------------------------------------------------
    if contains_common_word(lowered, normalized):
        score -= 20
        breakdown.append(("Contains a common password or word", "-20"))
        tips.append("Avoid common words and passwords, even with swaps like @ for a.")

    if has_repeats(password):
        score -= 10
        breakdown.append(("Repeated characters in a row", "-10"))
        tips.append("Avoid repeating the same character three or more times (like 'aaa').")

    if has_sequence(password):
        score -= 15
        breakdown.append(("Easy sequence (abc, 123, qwe...)", "-15"))
        tips.append("Avoid sequences such as 'abc', '123' or keyboard runs like 'qwerty'.")

    if classes_used == 1:
        score -= 10
        breakdown.append(("Only one type of character", "-10"))

    # --- 5. Hard limits --------------------------------------------------
    if is_common_password(lowered, normalized):
        score = min(score, 10)
        breakdown.append(("Very common password: score limited", "max 10"))
        tips.insert(0, "This is a very common password. Attackers try these first.")
    elif length < 8:
        score = min(score, 35)
        breakdown.append(("Shorter than 8 characters: score limited", "max 35"))

    # Keep the score between 0 and 100.
    score = max(0, min(100, score))
    label, css_class = rating_for(score)

    return {
        "score": score,
        "label": label,
        "css_class": css_class,
        "strengths": strengths,
        "tips": tips,
        "breakdown": breakdown,
    }


# ---------------------------------------------------------------------------
# Web page (HTML + CSS only, no JavaScript)
# ---------------------------------------------------------------------------
PAGE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Password Strength Checker</title>
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; padding: 16px; font-family: Arial, Helvetica, sans-serif;
           background: #f1f4f9; color: #1f2937; line-height: 1.5; }
    .card { max-width: 640px; margin: 24px auto; background: #fff; padding: 24px;
            border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,.08); }
    h1 { margin-top: 0; font-size: 1.6rem; }
    h2 { font-size: 1.1rem; margin-bottom: 6px; }
    .warning { background: #fff7e0; border-left: 4px solid #f0ad00;
               padding: 10px 14px; border-radius: 6px; font-size: .92rem; }
    label { display: block; margin: 18px 0 6px; font-weight: bold; }
    input[type=password] { width: 100%; padding: 12px; font-size: 1rem;
                           border: 1px solid #b8c0cc; border-radius: 8px; }
    button { margin-top: 12px; padding: 12px 22px; font-size: 1rem; color: #fff;
             background: #2563eb; border: 0; border-radius: 8px; cursor: pointer; }
    button:hover { background: #1d4ed8; }
    .error { margin-top: 16px; padding: 10px 14px; background: #fdecea;
             color: #8a1c14; border-radius: 6px; }
    .result { margin-top: 24px; border-top: 1px solid #e5e7eb; padding-top: 16px; }
    .bar { background: #e5e7eb; border-radius: 999px; height: 18px; overflow: hidden; }
    .fill { height: 100%; }
    .very-weak   { background: #dc2626; }
    .weak        { background: #f97316; }
    .moderate    { background: #eab308; }
    .strong      { background: #84cc16; }
    .very-strong { background: #16a34a; }
    .label { font-size: 1.4rem; font-weight: bold; margin: 8px 0 2px; }
    table { width: 100%; border-collapse: collapse; font-size: .92rem; }
    td { padding: 6px 4px; border-bottom: 1px solid #eee; }
    td.pts { text-align: right; white-space: nowrap; }
    ul { margin-top: 4px; padding-left: 20px; }
    .footer { font-size: .82rem; color: #6b7280; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="card">
    <h1>Password Strength Checker</h1>

    <p class="warning">
      <strong>Educational estimate only.</strong> This tool cannot guarantee that a
      password is secure. Do not enter real passwords into websites you do not
      trust, including this one. Try example passwords instead.
    </p>

    <form method="post" action="/" autocomplete="off">
      <label for="password">Enter a password to evaluate</label>
      <input type="password" id="password" name="password"
             maxlength="{{ max_length }}" autocomplete="off" required>
      <button type="submit">Check strength</button>
    </form>

    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}

    {% if result %}
      <div class="result">
        <div class="label">{{ result.label }} &ndash; {{ result.score }}/100</div>
        <div class="bar">
          <div class="fill {{ result.css_class }}" style="width: {{ result.score }}%"></div>
        </div>

        {% if result.strengths %}
          <h2>What is good</h2>
          <ul>{% for item in result.strengths %}<li>{{ item }}</li>{% endfor %}</ul>
        {% endif %}

        {% if result.tips %}
          <h2>How to improve</h2>
          <ul>{% for item in result.tips %}<li>{{ item }}</li>{% endfor %}</ul>
        {% endif %}

        <h2>Score breakdown</h2>
        <table>
          {% for rule, points in result.breakdown %}
            <tr><td>{{ rule }}</td><td class="pts">{{ points }}</td></tr>
          {% endfor %}
        </table>
      </div>
    {% endif %}

    <p class="footer">
      Your password is checked in memory only. It is not stored, logged or sent
      anywhere. A high score is not a promise of safety.
    </p>
  </div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        password = request.form.get("password", "")

        if password.strip() == "":
            error = "Please enter a password before checking."
        elif len(password) > MAX_LENGTH:
            error = f"Please keep the password to {MAX_LENGTH} characters or fewer."
        else:
            result = evaluate_password(password)
        # 'password' goes out of scope when this function returns.
        # It is never written to a file, a log or a database.

    return render_template_string(PAGE, result=result, error=error,
                                  max_length=MAX_LENGTH)


@app.after_request
def add_safety_headers(response):
    """Ask browsers not to cache the page and block scripts and outside content."""
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = (
        "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'"
    )
    return response


if __name__ == "__main__":
    # Local development server only (not for real deployment).
    app.run(host="127.0.0.1", port=5000, debug=False)