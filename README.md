# MediPedia Server

A FastAPI backend application for medicine reviews with OpenFDA and Gemini AI integration.

## Features

-   Medicine information from OpenFDA API
-   User reviews with sentiment analysis using Gemini AI
-   RESTful API endpoints for users, medicines, and reviews
-   SQLite database with Peewee ORM

## Prerequisites

-   Python 3.12 or higher
-   Git

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/JustTrott/MediPedia-server.git
    ```

2. Navigate to the project directory:

    ```bash
    cd MediPedia-server
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    pip install google-generativeai
    ```

4. Create a `.env` file in the root directory with the following content:
    ```plaintext
    DATABASE_URL=sqlite:///./test.db
    GEMINI_API_KEY=your_gemini_api_key
    OPENFDA_API_KEY=your_openfda_api_key
    ```

## Running the Application
pip install -r requirements.txt
Start the development server:

```bash
python -m uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

API documentation (Swagger UI) is available at: http://localhost:8000/docs

## API Endpoints

### Users

-   GET `/api/v1/users/` - List all users
-   GET `/api/v1/users/{user_id}` - Get specific user

### Medicines

-   GET `/api/v1/medicines/` - List all medicines
-   GET `/api/v1/medicines/{medicine_id}` - Get specific medicine

### Reviews

-   GET `/api/v1/reviews/` - List all reviews
-   GET `/api/v1/reviews/{review_id}` - Get specific review
-   GET `/api/v1/reviews/medicine/{medicine_id}` - Get all reviews for a medicine
-   GET `/api/v1/reviews/user/{user_id}` - Get all reviews by a user

### Favourites

-   GET `/api/v1/favourites/` - List all favourite medicines
-   POST `/api/v1/favourites/` - Add a new favourite medicine
-   DELETE `/api/v1/favourites/{favourite_id}` - Remove a favourite medicine


## Testing

Testing is done via pytest and coverage report is made via coverage.py

```bash
python -m coverage run -m pytest
```

And then you can view the report using:

```bash
python -m coverage report
```

or

```bash
python -m coverage html
```

for a more thorough report.

## for active developers

Run this command to enable merging instead of rebasing. (You need to run this only once per project)

```bash
git config pull.rebase false
```

Then, you can just pull and resolve the merge conflicts.

```bash
git pull
```

Don´t forget to check for new dependencies

```bash
pip install -r requirements.txt
```

## License

MIT
