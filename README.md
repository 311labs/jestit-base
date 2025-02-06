# Jestit Project

Jestit is an open-source Django-based web framework focused on providing a comprehensive suite for building REST APIs, authentication systems, and more. It comes with utilities, services, and examples for using Django models, middleware, testing, and custom decorators.

## Features

- **REST API Capabilities**: Easily create REST APIs using custom decorators to handle URL routing and request parsing.
- **Authentication**: Utilizes JWT-based authentication out of the box.
- **Model Enhancements**: Custom model base class to simplify CRUD operations.
- **Middleware**: JWT Authentication Middleware for secure HTTP request processing.
- **Testing Suite**: Built-in testing framework (Testit) to validate REST APIs.
- **Task Scheduling**: Taskit provides decorators and utilities for cron-like scheduled task execution.
- **Logging and Helpers**: Comprehensive logging utilities and helpers for simplifying Django project structure.
- **Example Apps**: Model examples for Todo and Note applications with REST API endpoints.
- **Dynamic Settings Loader**: Simplifies managing and accessing project settings across different apps.

## Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd jestit-base
   ```

2. **Install Dependencies**
   Ensure you have Python 3.8+ and `pip` installed. Run:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Project**
   The configuration files are located in `jestit-base/config`. Adjust settings according to your execution environment.

4. **Database Migrations**
   Run migrations to set up the database schema:

   ```bash
   python manage.py migrate
   ```

5. **Running the Development Server**
   Start the Django development server:

   ```bash
   python manage.py runserver
   ```

## Usage

### Running Business Logic and API
- **Default Modules and APIs** are located in `jestit-base/apps/jestit`.
- **Example Usage**: Access your new endpoints like `/api/example/todo` for the included todo application.

### Using the Test Framework
- **Running Tests**: Execute all tests with:

  ```bash
  python manage.py test
  ```

- **Available Tests**: Example tests are located under `jestit-base/apps/tests`.

### API Endpoints

1. **Todo API**
   - POST `/api/example/todo` - Create a new todo item.
   - GET `/api/example/todo/{id}` - Retrieve details of a todo item.
   - PUT `/api/example/todo/{id}` - Update a todo item.
   - DELETE `/api/example/todo/{id}` - Delete a todo item.

2. **Note API**
   - POST `/api/example/note` - Create a new note (authentication required).
   - GET `/api/example/note/{id}` - Retrieve details of a note.
   - PUT `/api/example/note/{id}` - Update a note.
   - DELETE `/api/example/note/{id}` - Delete a note.

### Authentication
- **JWT Authentication** is implemented. All protected resources require a valid JWT Token in the `Authorization` header.

## Project Structure Overview

- **`jestit`**: Core framework housing models, decorators, serializers, and utilities.
- **`authit`**: Authentication and user management components.
- **`taskit`**: Modules for handling asynchronous tasks and scheduled jobs.
- **`testit`**: Built-in testing utilities and REST Client.
- **`examples`**: Sample applications to demonstrate Jestit functionalities.

## Logging

Logging is enabled across different modules using custom utilities provided in `jestit.helpers.logit`.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
