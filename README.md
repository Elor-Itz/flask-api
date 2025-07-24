# Expression Evaluator API

This project is a Flask-based microservice API for evaluating mathematical expressions asynchronously. It uses a background processing stream, stores results in a PostgreSQL database, and supports Docker-based deployment and automated testing.

## Features

- Submit mathematical expressions for evaluation via a REST API
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
   - Create a database (e.g., `expression_evaluator`).

5. **Configure environment variables**
   - Create a `.env` file in the project root:
     ```
     DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/expression_evaluator
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
     POSTGRES_DB=expression_evaluator
     POSTGRES_USER=postgres
     POSTGRES_PASSWORD=yourpassword
     DATABASE_URL=postgresql://postgres:yourpassword@db:5432/expression_evaluator
     ```

2. **Build and run the containers**
   ```
   docker-compose up --build
   ```

3. **Access the app**
   - Go to [http://localhost:5000](http://localhost:5000)

## Usage

- **Standard expressions:** Enter a mathematical expression (e.g., `2+3*4`) in the web interface and submit.
- **Variable expressions:** Enter a variable math expression (e.g., `x*2` or `x^2 + 2*x + 1`) and provide a value for `x` in the Variable value field.
- The API will return a `request_id`. The front end will poll for the result and display it when ready.
- **Successful evaluations are saved to history. Errors are displayed immediately but not stored.**
- All inputs are validated for safety before processing.

## API Endpoints

- `POST /evaluation/expression` — Submit a standard mathematical expression.
- `POST /evaluation/variable` — Submit a variable math expression and a value.
- `GET /evaluation/result/<request_id>` — Poll for the result of an evaluation.
- `GET /health` — Health check endpoint.

## Testing

- Automated tests cover validation, error handling, and asynchronous processing.
- Test coverage is measured with `pytest-cov`.
- To run tests and view coverage:
  ```
  pytest --cov
  ```

## Project Structure

```
expression-evaluator/
│
├── app.py                # Main Flask application setup and entry point
├── api.py                # API namespaces and Swagger models
├── requirements.txt      # Python package dependencies
├── .env                  # Environment variables for local/dev setup
├── Dockerfile            # Docker image build instructions
├── docker-compose.yml    # Multi-container Docker orchestration
├── .dockerignore         # Files/folders to exclude from Docker builds
│
├── models.py             # SQLAlchemy database models
├── routes.py             # API endpoints and background processing logic
│
├── utils/                # Utility modules
│   ├── parser.py         # Expression parsing and evaluation logic
│   ├── stream.py         # Asynchronous stream/background worker
│   └── validation.py     # Input validation functions
│
├── templates/            # HTML templates for the web frontend
│   └── index.html        # Main web interface
│
├── static/               # Static files (CSS, JS, images)
│   └── style.css         # Stylesheet for the frontend
│
├── tests/                # Automated tests
│   └── test_api.py       # API and integration tests
│
└── README.md             # Project documentation
```