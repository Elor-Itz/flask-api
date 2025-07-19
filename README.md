# Flask Expression Evaluator API

This project is a Flask-based API for evaluating mathematical expressions asynchronously. It uses a background processing stream and stores results in a PostgreSQL database.

## Features

- Submit mathematical expressions for evaluation via a REST API
- Asynchronous processing using a background thread (Stream)
- Poll for results using a unique request ID
- Results are stored in PostgreSQL
- Simple web front end for user interaction

## Requirements

- Python 3.8+
- PostgreSQL
- pip packages (see `requirements.txt`)

## Setup

1. **Clone the repository**

2. **Create and activate a virtual environment**
   ```
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**
   - Ensure PostgreSQL is running.
   - Create a database (e.g., `flaskapi`).

5. **Configure environment variables**
   - Create a `.env` file in the project root:
     ```
     DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/flaskapi
     ```

6. **Run the app**
   ```
   python app.py
   ```

7. **Open your browser**
   - Go to [http://localhost:5000](http://localhost:5000)

## Usage

- Enter a mathematical expression in the web interface and submit.
- The API will return a `request_id`.
- The front end will poll for the result and display it when ready.

## Project Structure

```
flask-api/
│
├── app.py
├── requirements.txt
├── .env
├── utils/
│   ├── __init__.py
│   ├── parser.py
│   └── stream.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
└── README.md
```