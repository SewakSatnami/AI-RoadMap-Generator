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

1. Create a `.env` file in the project root with the following values:
   ```env
   GROQ_API_KEY=your_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

2. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Run the app:
   ```powershell
   python app.py
   ```

Open the app in your browser at:

```text
http://127.0.0.1:5000
```

## Notes

- The app stores users in MongoDB.
- Environment variables are loaded from `.env`.
- The `.env` file is ignored by git, so keep secrets out of source control.
- Update `FLASK_SECRET_KEY` with a secure value for production.
