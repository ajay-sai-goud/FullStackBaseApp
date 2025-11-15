# Full Stack Audio Application

This document provides a comprehensive guide to setting up the project, understanding its architecture, and using its features.

## 1. Local Development Setup

These steps will guide you through setting up and running the application locally using Docker.

### Prerequisites

-   **Docker and Docker Compose**: For building and running the containerized application.

### Step 1: Create and Configure the `.env` File

The project uses a `.env` file to manage environment variables.

1.  **Create the `.env` file**:
    Copy the example file to create your local configuration file.

    ```bash
    cp .env.example .env
    ```

2.  **Generate and Add RSA Keys for JWT**:
    The application uses RS256 for secure JWT signing, which requires a private/public key pair.

    -   Run the key generation script:
        ```bash
        python backend_fastapi/scripts/generate_rsa_keys.py
        ```
    -   This creates `private_key.pem` and `public_key.pem` in `backend_fastapi/keys/`.
    -   Next, format these keys to be used as environment variables:
        ```bash
        python backend_fastapi/scripts/format_keys_for_env.py
        ```
    -   Copy the output and paste it into your `.env` file for the `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY` variables.

3.  **Configure AWS S3 Credentials**:
    For file upload functionality, add your AWS credentials and S3 bucket details to the `.env` file:
    ```env
    AWS_ACCESS_KEY_ID=<your_access_key>
    AWS_SECRET_ACCESS_KEY=<your_secret_key>
    S3_BUCKET_NAME=<your_bucket_name>
    AWS_REGION=<your_bucket_region>
    ```

### Step 2: Build and Run the Application

With the configuration in place, use Docker Compose to build the images and start the containers.

```bash
docker-compose up --build
```

-   The `--build` flag tells Docker Compose to build the images from the Dockerfiles.
-   This command will start the backend, frontend, and MongoDB services.

### Step 3: Access the Application

Once the containers are running, you can access the application:

-   **Frontend**: [http://localhost:3000](http://localhost:3000)
-   **Backend API**: [http://localhost:8000](http://localhost:8000)
-   **API Docs (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

The default admin user is created on startup with the credentials from your `.env` file. The defaults are:
-   **Email**: `admin@example.com`
-   **Password**: `Admin@password123`

## 2. Key Features

### User Management
-   **Authentication**: Secure login with JWT (RS256).
-   **Permissions**: Role-based access control for different API endpoints.
-   **Admin User**: A default admin user is created on startup, with a deterministic ID to prevent duplicates in a multi-worker environment.

### Audio File Management
-   **Shared File System**: All audio files are stored in a shared pool, accessible to any authenticated user with `read:audio` permission. Files are not tied to individual users.
-   **Cloud Storage**: Files are uploaded to AWS S3, with only metadata stored in the database.
-   **S3 Path**: The S3 object key is structured as `{file_id}/{filename}` for direct mapping to the database record.

## 3. Architectural & Folder Structure Rationale

The project is structured to be scalable, maintainable, and easy to navigate, following industry best practices.

### Backend (FastAPI)

The backend follows principles from **Domain-Driven Design (DDD)** and enforces **SOLID principles** to ensure a clean and decoupled architecture.

```
/app
├── api/          # Entrypoint Layer: Routes and request handling
├── core/         # Core Application: DB, dependencies, configuration
├── schemas/      # Data Contracts: Pydantic models for validation
├── services/     # Business Logic Layer
└── utils/        # Shared Utilities
```

-   **`api/`**: Defines API endpoints, receives requests, and delegates work to services. Contains no business logic.
-   **`services/`**: The heart of the application's business logic. Services are decoupled from the database and other services by depending on **interfaces (Protocols)**.
-   **`core/`**: Contains the application's core infrastructure, including database connection, dependency injection, and application startup/shutdown logic (`lifespan.py`).
-   **`schemas/`**: Pydantic models for request/response validation.
-   **`utils/`**: Shared, stateless utility functions (e.g., password hashing, deterministic ID generation).

**Why this structure?**
This layered architecture makes the application easier to test, maintain, and scale. The database can be swapped with minimal changes to the service or API layers.

### Frontend (React)

The frontend is structured for component reusability and separation of concerns.

```
/src
├── components/   # Small, reusable UI components
├── contexts/     # Global state management (e.g., Authentication)
├── hooks/        # Custom, reusable React hooks
├── pages/        # Top-level page components
├── services/     # API communication layer
└── styles/       # Global and shared styles
```

-   **`pages/`**: Full-page components that compose smaller components.
-   **`components/`**: Smaller, reusable components used across multiple pages (e.g., `Button`, `AudioPlayer`).
-   **`services/`**: Centralized API communication layer, decoupling UI components from the API.
-   **`contexts/`**: Global state management for authentication and JWT.
-   **`hooks/`**: Reusable logic encapsulated in custom React hooks.
-   **`styles/`**: Centralized global and shared styles.

**Why this structure?**
This component-based structure makes the codebase easy to understand and scale, leading to a more efficient development process.
