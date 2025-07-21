# Flask Expression Evaluator API

This project is a Flask-based microservice API for evaluating mathematical and lambda expressions asynchronously. It uses a background processing stream, stores results in a PostgreSQL database, and supports Docker-based deployment and automated testing.

## Features

- Submit mathematical or lambda expressions for evaluation via a REST API
- Asynchronous processing using a background thread (Stream)
- Poll for results using a unique request ID
- Results are stored in PostgreSQL
- Simple web front end for user interaction
- Docker and Docker Compose support for easy deployment
- Automated tests with pytest and pytest-flask

## Requirements

- Python 3.8+
- PostgreSQL
- Docker (optional, for containerized deployment)
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

## Docker Deployment

1. **Configure environment variables for Docker Compose**
   - Create a `.env` file in the project root:
     ```
     POSTGRES_DB=flaskapi
     POSTGRES_USER=postgres
     POSTGRES_PASSWORD=yourpassword
     DATABASE_URL=postgresql://postgres:yourpassword@db:5432/flaskapi
     ```

2. **Build and run the containers**
   ```
   docker-compose up --build
   ```

3. **Access the app**
   - Go to [http://localhost:5000](http://localhost:5000)

## Usage

- **Standard expressions:** Enter a mathematical expression (e.g., `2+3*4`) in the web interface and submit.
- **Lambda expressions:** Enter a lambda expression (e.g., `lambda x: x*2`) and provide a value for `x` in the Lambda value field.
- The API will return a `request_id`. The front end will poll for the result and display it when ready.

## API Endpoints

- `POST /evaluate` — Submit a standard mathematical expression.
- `POST /evaluate-lambda` — Submit a lambda expression and a value.
- `GET /result/<request_id>` — Poll for the result of an evaluation.

## Testing

- Automated tests are provided using pytest and pytest-flask.
- To run tests:
  ```
  pytest
  ```

## Project Structure

```
flask-api/
│
├── app.py
├── requirements.txt
├── .env
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── utils/
│   ├── __init__.py
│   ├── parser.py
│   └── stream.py
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── tests/
│   └── test_api.py
└── README.md
```