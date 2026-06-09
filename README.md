# AI RoadMap Project

A Flask-based AI roadmap generator with MongoDB for user login and roadmap storage.

## Requirements

- Python 3.11+ (or compatible)
- MongoDB running locally on `localhost:27017`
- `pip` available

## Setup

1. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Run

```powershell
python app.py
```

Open the app in your browser at:

```text
http://127.0.0.1:5000
```

## Notes

- The app stores users in MongoDB.
- Make sure MongoDB is running before starting the Flask server.
- Set `GROQ_API_KEY` before running the app.
- The `app.py` file currently uses a hard-coded Flask secret key; update it for production.
