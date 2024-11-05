# Questionnaire-Webtool

A tool for the setup of a questionnaire and the deployment of NLP-models (including transformers) for the automatic scoring of the tasks in open response format.

This code is highly experimental and "researchy" stuff - nothing to be deployed yet!

## Setup
- Install [pre-commit](https://pre-commit.com/) hooks via `pre-commit init` when planning to contribute.
- Setup the Python environment, e.g., using [Poetry](https://python-poetry.org/) via the provided `pyproject.toml` via `poetry install`.
- Run the Flask development server via `.venv/bin/flask run --debug` or similar.

## ToDo's

Many... Following soon...

- Currently the Tool is set up for a specific questionnaire but can (and should) be abstracted similarly to and under the usage of [`questionnaire-tools`](https://github.com/JannisZeller/questionnaire-tools).
- To be clear: The abstraction of the code *should* happen by integrating the [`questionnaire-tools`](https://github.com/JannisZeller/questionnaire-tools) into this project.
- The `/models` folder containing the models for actually grading the questionnaire responses and creating reports is currently excluded via `.gitignore` for data-privacy reasons. For development, there should at least be dummy models in this directory.
- A proper frontend.

## Necessary Config (2024-11-05)

Needs the following keys to be specified in `/env/config.jsonc`:
```jsonc
{
    // --- Base ---
    "API_INTERFACE_COMMUNICATION": "functional", // "request" or "functional"
    "JWT_COOKIE_KEY": "x-access-token",
    "CONSENT_COOKIE_KEY": "x-consent",
    "SESSION_COOKIE_SAMESITE": "Lax",

    // Get added for total valid duration
    "JWT_VALID_MINUTES": 30,
    "JWT_VALID_SECONDS": 0,

    // --- Interface ---
    "ENABLE_RECAPTCHA": false, // true or false (must be false for MS-devtonnels development hosting)

    // --- API ---
    "DIMSCORES_MODE": "summation", // "regression" or "summation"
    "PRELOAD_MODELS": false
}
```

Needs the following keys to be specified in `/env/secret_config.jsonc`:
```jsonc
{
    "SQLALCHEMY_DATABASE_URI": "",
    "SECRET_KEY": "",

    // Optional
    "RECAPTCHA_PUBLIC_KEY": "",
    "RECAPTCHA_PRIVATE_KEY": "",
    "RECAPTCHA_VERIFY_URL": "",
    "TEST_RECIEVER_ADDRESS": "",
    "GMAIL_ADDRESS": "",
    "GMAIL_PW": "",
}
```
