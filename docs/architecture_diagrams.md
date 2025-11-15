# Architecture & Flow Diagrams

This document provides diagrams illustrating the system architecture and key user flows. The diagrams are created using Mermaid syntax for clarity and version control.

## 1. High-Level System Architecture

This diagram shows the main components of the application and how they interact.

```mermaid
graph TD
    A[User's Browser] -- HTTPS --> B{React Frontend};
    B -- API Calls (HTTPS) --> C{FastAPI Backend};
    C -- CRUD Operations --> D[(MongoDB)];
    C -- File Operations (Upload/Download) --> E[(AWS S3)];

    subgraph "Client"
        A
    end

    subgraph "Application Infrastructure (Docker)"
        B
        C
        D
    end

    subgraph "Cloud Storage"
        E
    end

    style B fill:#61DAFB,stroke:#333,stroke-width:2px
    style C fill:#009688,stroke:#333,stroke-width:2px
    style D fill:#47A248,stroke:#333,stroke-width:2px
    style E fill:#FF9900,stroke:#333,stroke-width:2px
```

## 2. Authentication Flow (JWT)

This sequence diagram illustrates the process of a user logging in and receiving a JWT.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend

    User->>Frontend: Enters email and password
    Frontend->>Backend: POST /api/login with credentials
    Backend->>Backend: Find user by email in DB
    Backend->>Backend: Verify hashed password
    alt Successful Login
        Backend->>Backend: Generate JWT (RS256)
        Backend-->>Frontend: Return JWT Token
        Frontend->>Frontend: Store JWT in local storage/state
        Frontend-->>User: Redirect to dashboard
    else Invalid Credentials
        Backend-->>Frontend: Return 401 Unauthorized error
        Frontend-->>User: Show "Invalid credentials" error
    end
```

## 3. Audio Upload Flow

This diagram shows the steps involved when a user uploads an audio file.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant S3 as AWS S3

    User->>Frontend: Selects an audio file and clicks Upload
    Frontend->>Backend: POST /api/audio/upload (multipart/form-data with JWT)
    Backend->>Backend: Authenticate user via JWT
    Backend->>Backend: Validate file (type, size)
    Backend->>S3: Upload file stream
    S3-->>Backend: Return file URL
    Backend->>Backend: Store file metadata (URL, user_id, etc.) in MongoDB
    Backend-->>Frontend: Return success response with file details
    Frontend-->>User: Show success message and refresh file list
```

## 4. Audio Playback Flow

This diagram explains how a user plays an audio file, using a secure, short-lived signed URL.

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant Backend
    participant S3 as AWS S3

    User->>Frontend: Clicks 'Play' on an audio file
    Frontend->>Backend: GET /api/audio/{id}/play (with JWT)
    Backend->>Backend: Authenticate user via JWT
    Backend->>Backend: Verify file ownership (user can only access their own files)
    Backend->>S3: Request a signed URL for the S3 object
    S3-->>Backend: Generate and return signed URL
    Backend-->>Frontend: Return signed URL with expiration time
    Frontend->>Frontend: Set signed URL as the 'src' of an <audio> tag
    Frontend->>S3: Browser requests the audio file using the signed URL
    S3-->>Frontend: Streams audio data directly to the browser
```
