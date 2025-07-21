# Implementation Guidelines for the Roblox API RAG Project

These guidelines are intended to ensure consistency, maintainability, and quality throughout the project.

## 1. Code Style and Formatting

*   **Python**: All Python code should adhere to the [PEP 8 style guide](https://www.python.org/dev/peps/pep-0008/).
*   **Formatting**: Use a code formatter like `black` to ensure consistent formatting.
*   **Linting**: Use a linter like `flake8` or `pylint` to catch common errors and style issues.

## 2. Modularity and Separation of Concerns

*   **Services**: Each service (scraper, API, MCP server) should be self-contained and have a single responsibility.
*   **Modules**: Within each service, code should be organized into modules with clear and specific purposes (e.g., `roblox_api.py`, `chunking.py`, `vector_db.py`).
*   **Functions**: Functions should be small, focused, and have a single responsibility.

## 3. Asynchronous Programming

*   **`asyncio`**: Use `asyncio` for all I/O-bound operations to ensure the services are non-blocking and can handle concurrent requests efficiently.
*   **`httpx`**: Use the `httpx` library for asynchronous HTTP requests.
*   **Synchronous Code**: When it is necessary to use a synchronous library (like Scrapy's `CrawlerProcess`), use `asyncio.to_thread` or a library like `crochet` to run it in a separate thread and avoid blocking the main event loop.

## 4. Error Handling and Logging

*   **Error Handling**: Use `try...except` blocks to handle potential exceptions gracefully.
*   **HTTP Exceptions**: In the FastAPI application, use `HTTPException` to return meaningful HTTP status codes and error messages.
*   **Logging**: Implement structured logging in all services to provide visibility into the application's behavior. Log important events, errors, and debugging information.

## 5. Configuration and Environment Variables

*   **`.env` file**: Use a `.env` file to store sensitive information and environment-specific configurations.
*   **`.env.example`**: Always maintain an `.env.example` file with placeholder values to document the required environment variables.
*   **`os.getenv`**: Use `os.getenv` to access environment variables within the application, providing default values where appropriate.

## 6. Dependency Management

*   **Poetry**: Use Poetry for dependency management to ensure a consistent and reproducible environment.
*   **`pyproject.toml`**: Clearly define all project dependencies in the `pyproject.toml` file.
*   **`poetry.lock`**: Keep the `poetry.lock` file up to date and committed to version control.

## 7. Testing

*   **Unit Tests**: Write unit tests for individual functions and modules to ensure they work as expected.
*   **Integration Tests**: Write integration tests to verify that the different services and components work together correctly.
*   **End-to-End Tests**: Perform end-to-end testing to validate the entire system, from scraping to retrieval.

By following these guidelines, we can build a robust, maintainable, and high-quality system.