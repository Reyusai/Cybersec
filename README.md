# Password Strength Checker

A beginner-friendly Flask website that estimates how strong a password is. It
checks length, character variety, repeated characters, easy sequences and
common passwords, then shows a rating (Very Weak to Very Strong), a score out
of 100 and plain-English feedback.

> **Educational estimate only.** This tool does not guarantee that any password
> is secure. Do not type real passwords into websites you do not trust. Use
> example passwords for testing.

## Privacy

- The password is sent with a POST form, so it never appears in the URL.
- It is processed in memory only to produce the response.
- It is not saved, logged, sent to another service, or stored in a database.
- There is no JavaScript, analytics or external service.

## Prerequisites

- Python 3.9 or newer (check with `python --version`)
- pip (included with Python)
- Any modern web browser

## Setup

1. Open a terminal in the project folder (the one containing `app.py`).

2. Create a virtual environment (recommended):

   ```
   python -m venv venv
   ```

3. Activate it:

   - Windows (Command Prompt): `venv\Scripts\activate`
   - Windows (PowerShell): `venv\Scripts\Activate.ps1`
   - macOS / Linux: `source venv/bin/activate`

4. Install the dependency:

   ```
   pip install -r requirements.txt
   ```

## Run the website

```
python app.py
```

(On some macOS/Linux systems, use `python3 app.py`.)

## Open it in a browser

Go to **http://127.0.0.1:5000** after the terminal shows that the server is running.

## Stop the server

Click the terminal window and press **Ctrl + C**. To leave the virtual
environment, run `deactivate`.

## Troubleshooting

- **Port already in use:** close the other program using port 5000, or change
  `port=5000` at the bottom of `app.py` and open the new port in your browser.
- **`No module named flask`:** activate the virtual environment and run
  `pip install -r requirements.txt` again.

## Project files

| File | Purpose |
|------|---------|
| `app.py` | Whole application: scoring logic, routes and inline HTML/CSS page |
| `requirements.txt` | Python dependency list (Flask) |
| `README.md` | Setup and usage instructions |
| `project_report.md` | College-style project report |