```markdown
# Flask Hangman

A simple web-based Hangman game implemented with Flask. This project demonstrates:
- Managing game state using Flask sessions.
- Validating user input and updating game state on the server.
- Rendering a text-based (ASCII) Hangman representation in a web UI.

Files:
- app.py - main Flask application (detailed comments and step-by-step logic included)
- requirements.txt - dependencies
- templates/ - Jinja2 templates (base.html, index.html, game.html)
- static/style.css - simple styling for the UI

Quick start:
1. (Optional) Create and activate a virtual environment:
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate      # Windows

2. Install dependencies:
   pip install -r requirements.txt

3. Run the app (development):
   export FLASK_APP=app.py
   flask run

4. Open http://127.0.0.1:5000 in your browser.

Notes and next enhancements:
- The session stores the secret word and guessed letters; the secret word is stored server-side in the session cookie (signed).
- For production: change app.secret_key and consider server-side session storage (Redis, database).
- Possible extensions: upload a larger word list, add difficulty levels, add a hint system, persistent scoreboard, or convert to an SPA with live updates via WebSockets.
```