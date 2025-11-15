# Developer Setup and Design Rationale

This document provides a comprehensive guide to setting up the project and explains the reasoning behind its architectural and folder structure choices.

## 1. Local Development Setup

These steps will guide you through setting up and running the application locally using Docker. This guide assumes you have already cloned the repository.

### Prerequisites

-   **Docker and Docker Compose**: For building and running the containerized application.

### Step 1: Create and Configure the `.env` File

The project uses a `.env` file to manage environment variables. A template is provided to make this process easier.

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

3.  **Configure AWS S3 Credentials (Optional)**:
    If you plan to use the file upload functionality, add your AWS credentials and S3 bucket details to the `.env` file:
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

The default admin user credentials (if not changed in `.env`) are:
-   **Email**: `admin@example.com`
-   **Password**: `Admin@password123`

## 2. Architectural & Folder Structure Rationale

The project is structured to be scalable, maintainable, and easy to navigate, following industry best practices for both backend and frontend development.

### Backend (FastAPI)

The backend follows principles from **Domain-Driven Design (DDD)** and enforces **SOLID principles** to ensure a clean and decoupled architecture. The structure separates concerns into distinct layers.

```
/app
├── api/          # Entrypoint Layer: Routes and request handling
├── core/         # Core Application: DB, dependencies, configuration
├── schemas/      # Data Contracts: Pydantic models for validation
├── services/     # Business Logic Layer
└── utils/        # Shared Utilities
```

-   **`api/`**: This is the presentation layer. Its only responsibility is to define API endpoints, receive HTTP requests, and delegate the work to the appropriate service. It contains no business logic. This adheres to the **Single Responsibility Principle (SRP)**.

-   **`services/`**: This is the heart of the application's business logic. Each service (e.g., `UserService`, `AudioService`) encapsulates the logic for a specific domain. Services are decoupled from the database implementation and other services by depending on **interfaces (Protocols)**, which follows the **Dependency Inversion Principle (DIP)**.

-   **`core/`**: This directory contains the application's core infrastructure.
    -   `database/`: Manages the database connection and data access layer (e.g., `UserManager`). This isolates data access logic from the rest of the application.
    -   `dependencies.py`: Centralizes dependency injection, making it easy to manage and swap implementations (**OCP** and **DIP**).
    -   `lifespan.py`: Handles application startup and shutdown events.

-   **`schemas/`**: Contains all Pydantic models used for request/response validation and serialization. These act as the data contracts for the API, ensuring that all data entering and leaving the system is valid and well-defined.

-   **`utils/`**: A collection of pure, stateless utility functions (e.g., password hashing, ID generation) that can be used anywhere in the application without creating dependencies.

**Why this structure?**
This layered architecture makes the application easier to test, maintain, and scale. For example, the database can be swapped out by simply changing the implementation in `core/database/` and updating `dependencies.py`, with no changes needed in the service or API layers.

### Frontend (React)

The frontend is structured to promote component reusability, separation of concerns, and a scalable development workflow.

```
/src
├── components/   # Small, reusable UI components
├── contexts/     # Global state management (e.g., Authentication)
├── hooks/        # Custom, reusable React hooks
├── pages/        # Top-level page components
├── services/     # API communication layer
└── styles/       # Global and shared styles
```

-   **`pages/`**: Each file in this directory represents a full page or screen in the application (e.g., `Login.tsx`, `AudioList.tsx`). These components are responsible for the layout of the page and composing smaller components together.

-   **`components/`**: This directory contains smaller, reusable components that are used across multiple pages (e.g., `Button.tsx`, `AudioPlayer.tsx`). This approach keeps the code DRY (Don't Repeat Yourself) and ensures a consistent UI.

-   **`services/`**: This layer is responsible for all communication with the backend API. All `axios` or `fetch` calls are centralized here. This decouples the UI components from the specifics of the API, making it easy to update API endpoints without changing the components.

-   **`contexts/`**: For managing global state that needs to be accessed by many components (like the user's authentication status and JWT). This avoids "prop drilling" and provides a clean way to share state across the application.

-   **`hooks/`**: Contains custom React hooks that encapsulate reusable logic (e.g., managing the auth token from local storage). This helps keep components clean and focused on rendering the UI.

-   **`styles/`**: Centralizes global styles, CSS variables, and shared stylesheets, ensuring a consistent look and feel across the application.

**Why this structure?**
This component-based and feature-oriented structure makes the codebase easy to understand and scale. When working on a feature, a developer can easily locate the relevant page, components, and API services, leading to a more efficient development process.
