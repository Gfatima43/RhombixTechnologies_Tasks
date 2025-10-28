"""
Flask Hangman (text-based game in a web UI)

This Flask application implements a simple Hangman game using a predefined
word list. It demonstrates:
- How to start and manage a game session (using Flask sessions).
- How to validate and process letter guesses.
- How to render the game's state (ASCII hangman, revealed letters).
- Step-by-step comments explain each part of the flow.

How it works:
1. User visits the home page (/), selects a difficulty level, and clicks "Start Game".
2. /start initializes a new game and stores the state in `session`.
3. /game shows the current game state and a form to submit a letter guess.
4. /guess processes the submitted letter, updates the session state, and
   redirects back to /game to show the updated state.
5. The game ends when the user guesses all letters (win) or uses up the
   allowed wrong attempts (loss). A Play Again button lets the user restart.

To run:
1. pip install -r requirements.txt
2. export FLASK_APP=app.py    # or set FLASK_APP on Windows
3. flask run
4. Open http://127.0.0.1:5000

Author: Example with detailed comments for learning and extension.
"""

import random
import string
from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)

# NOTE: Replace this with a random, secret value in production.
app.secret_key = "change_this_to_a_random_secret_in_production"

# -----------------------
# Predefined word list
# -----------------------
# Keep the words lowercase to simplify comparisons.
WORDS = [
    "python", "hangman", "challenging", "programming", "algorithm", "function", "variable",
    "development", "automation", "computer", "flask", "keyboard", "internet", "database",
    "debugging", "package", "repository", "syntax", "condition", "iteration", "recursion", "string"
]

# -----------------------
# Hangman ASCII art stages
# -----------------------
# Visual feedback for wrong guesses.
HANGMAN_PICS = [
    """
     +---+
     |   |
         |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
         |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
     |   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|   |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
         |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    /    |
         |
    =========""",
    """
     +---+
     |   |
     O   |
    /|\\  |
    / \\  |
         |
    ========="""
]


# -----------------------
# Utility functions
# -----------------------
def choose_word(word_list):
    """
    Choose a random word and return a word from word_list.
    The returned word is lowercase.
    """
    return random.choice(word_list).lower()


def init_game(difficulty='normal'):
    """
    Initialize a new game and store its state in the Flask session.
    We store simple serializable structures (strings and lists) so session
    (which uses signed cookies by default) can persist them.
    
    Difficulty levels:
    - easy: 8 wrong attempts
    - normal: 6 wrong attempts
    - hard: 4 wrong attempts
    """
    secret_word = choose_word(WORDS)
    session['secret_word'] = secret_word
    # Lists are used here because sets are not JSON-serializable by default.
    session['correct_letters'] = []  # letters guessed that are in the word
    session['wrong_letters'] = []    # letters guessed that are not in the word
    
    # Set max wrong attempts based on difficulty
    if difficulty == 'easy':
        session['max_wrong'] = 8
    elif difficulty == 'hard':
        session['max_wrong'] = 4
    else:  # normal
        session['max_wrong'] = 6
    
    session['difficulty'] = difficulty
    session.modified = True  # ensure Flask knows we've changed session
    # Useful for debugging during development:
    app.logger.debug(f"New game started with secret_word='{secret_word}' and difficulty='{difficulty}'")


def display_progress(secret_word, correct_letters):
    """
    Return a string with underscores for unknown letters and revealed letters
    for those guessed correctly. E.g. "p _ t h _ n"
    """
    return " ".join([ch if ch in correct_letters else "_" for ch in secret_word])


def current_stage(wrong_letters):
    """
    Return the ASCII art for the current number of wrong attempts.
    """
    idx = min(len(wrong_letters), len(HANGMAN_PICS) - 1)
    return HANGMAN_PICS[idx]


def game_over_condition(secret_word, correct_letters, wrong_letters, max_wrong):
    """
    Return a tuple (finished: bool, result: "win"|"lose"|None)
    """
    # Win: all unique letters in secret_word are guessed
    if set(secret_word) <= set(correct_letters):
        return True, "win"
    # Lose: too many wrong guesses
    if len(wrong_letters) >= max_wrong:
        return True, "lose"
    return False, None


def get_available_letters(correct_letters, wrong_letters):
    """
    Return a dictionary mapping each letter to its state: 
    'correct', 'wrong', or 'available'
    """
    all_guessed = set(correct_letters + wrong_letters)
    letters_status = {}
    
    for letter in string.ascii_lowercase:
        if letter in correct_letters:
            letters_status[letter] = 'correct'
        elif letter in wrong_letters:
            letters_status[letter] = 'wrong'
        else:
            letters_status[letter] = 'available'
    
    return letters_status


# -----------------------
# Routes (web endpoints)
# -----------------------
@app.route("/")
def index():
    """
    Home page that explains the game and has a Start Game button.
    """
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():
    """
    Start a new game and redirect to the game screen.
    Uses POST so starting a game is an intentional action.
    """
    difficulty = request.form.get('difficulty', 'normal')
    init_game(difficulty)
    flash(f"New {difficulty} game started! Good luck.", "info")
    return redirect(url_for("game"))


@app.route("/game", methods=["GET"])
def game():
    """
    Main game page that shows the hangman ASCII art, the partially revealed
    word, wrong guesses, and a form to submit a single-letter guess.
    """
    # If a game has not been started, redirect to index with a message.
    if 'secret_word' not in session:
        flash("No active game. Click Start Game to begin.", "warning")
        return redirect(url_for("index"))

    secret_word = session.get('secret_word')
    correct_letters = session.get('correct_letters', [])
    wrong_letters = session.get('wrong_letters', [])
    max_wrong = session.get('max_wrong', 6)
    difficulty = session.get('difficulty', 'normal')

    finished, result = game_over_condition(secret_word, correct_letters, wrong_letters, max_wrong)
    
    # Get the status of all letters for display
    letters_status = get_available_letters(correct_letters, wrong_letters)

    return render_template(
        "game.html",
        hangman_ascii=current_stage(wrong_letters),
        wrong_letters=wrong_letters,
        progress=display_progress(secret_word, correct_letters),
        finished=finished,
        result=result,
        secret_word=secret_word if finished else None,  # reveal only when game finished
        remaining=max_wrong - len(wrong_letters),
        difficulty=difficulty,
        letters_status=letters_status
    )


@app.route("/guess", methods=["POST"])
def guess():
    """
    Process a user's letter guess submitted from the game form.

    Steps:
    1. Validate input (single alphabetic character).
    2. Check if the letter was already guessed.
    3. Update correct_letters or wrong_letters in session.
    4. Flash a message to inform the user what happened.
    5. Redirect back to /game to show updated state.
    """
    if 'secret_word' not in session:
        flash("No active game. Start a new game first.", "warning")
        return redirect(url_for("index"))

    raw_guess = request.form.get("guess", "").strip().lower()

    # Input validation
    if len(raw_guess) != 1 or not raw_guess.isalpha():
        flash("Please enter a single letter (a-z).", "error")
        return redirect(url_for("game"))

    guess_letter = raw_guess

    # Retrieve current state from session
    correct_letters = session.get('correct_letters', [])
    wrong_letters = session.get('wrong_letters', [])
    secret_word = session.get('secret_word')
    max_wrong = session.get('max_wrong', len(HANGMAN_PICS) - 1)

    # Check if already guessed
    if guess_letter in correct_letters or guess_letter in wrong_letters:
        flash(f"You already guessed '{guess_letter}'. Try a different letter.", "warning")
        return redirect(url_for("game"))

    # Update state
    if guess_letter in secret_word:
        correct_letters.append(guess_letter)
        session['correct_letters'] = correct_letters
        flash(f"Good guess: '{guess_letter}' is in the word.", "success")
    else:
        wrong_letters.append(guess_letter)
        session['wrong_letters'] = wrong_letters
        remaining = max_wrong - len(wrong_letters)
        flash(f"Sorry: '{guess_letter}' is NOT in the word. {remaining} wrong attempt(s) left.", "error")

    session.modified = True

    # After updating, check if game finished and flash a message if so.
    finished, result = game_over_condition(secret_word, correct_letters, wrong_letters, max_wrong)
    if finished:
        if result == "win":
            flash(f"Congratulations 👏🎉🎉— You guessed the word '{secret_word}'!", "success")
        else:
            flash(f"Game over 💀💀💀. The word was '{secret_word}'.", "error")

    return redirect(url_for("game"))


@app.route("/reset", methods=["POST"])
def reset():
    """
    Clear the session game state and redirect to home. This is useful for
    starting fresh or clearing any incomplete games.
    """
    session.pop('secret_word', None)
    session.pop('correct_letters', None)
    session.pop('wrong_letters', None)
    session.pop('max_wrong', None)
    session.pop('difficulty', None)
    flash("Game reset. Start a new game when you're ready.", "info")
    return redirect(url_for("index"))


# -----------------------
# Run the app (development)
# -----------------------
if __name__ == "__main__":
    # For learning/demo purposes we run with debug=True. Do not use this in production.
    app.run(debug=True)
