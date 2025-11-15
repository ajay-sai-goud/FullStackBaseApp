# Full Stack Audio Management Application

A full-stack application featuring a FastAPI backend and a React frontend for user authentication, audio file management, and secure cloud storage integration with AWS S3.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React (TypeScript)
- **Database**: MongoDB
- **Cloud Storage**: AWS S3
- **Authentication**: JWT (RS256)
- **Containerization**: Docker & Docker Compose

## Features

- **User Authentication**: Secure user login with JWT tokens.
- **Audio File Management**: Upload, list, play, update, and delete audio files.
- **Cloud Integration**: Files are securely stored in AWS S3.
- **Protected APIs**: All sensitive endpoints are protected using JWT authentication.
- **SOLID Principles**: Backend architecture adheres strictly to SOLID principles for maintainability and scalability.
- **Containerized**: Fully containerized for easy setup and deployment.

## Getting Started

For detailed setup instructions, architecture diagrams, and design rationale, please see the documentation in the `/docs` directory.

- **[Developer Setup and Design Guide](./docs/README.md)**
- **[Database Schema Definition](./docs/schema_definition.md)**
- **[Architecture & Flow Diagrams](./docs/architecture_diagrams.md)**

### Quick Start with Docker

1.  **Configure Environment**: Copy `.env.example` to `.env` and fill in the required values (see the [Developer Setup Guide](./docs/README.md) for details on generating keys).
2.  **Run the Application**:
    ```bash
    docker-compose up --build
    ```
3.  **Access Services**:
    -   **Frontend**: `http://localhost:3000`
    -   **Backend API**: `http://localhost:8000`
    -   **API Docs**: `http://localhost:8000/docs`
