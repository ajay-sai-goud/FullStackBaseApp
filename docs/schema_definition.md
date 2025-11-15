# Database Schema Definition

This document outlines the schema for the MongoDB collections used in the application.

## `users` Collection

Stores user information, credentials, and permissions.

| Field | Type | Description | Example |
| --- | --- | --- | --- |
| `id` | `String (Primary Key)` | Custom unique identifier (`user_...`), serves as the `_id`. | `"user_1a2b3c4d"` |
| `first_name` | `String` | User's first name. | `"Admin"` |
| `last_name` | `String` | User's last name. | `"User"` |
| `email` | `String` | User's email address. Must be unique. | `"admin@example.com"` |
| `hashed_password` | `String` | User's password, hashed using a secure algorithm. | `"$2b$12$..."` |
| `permissions` | `Array<String>` | List of permissions assigned to the user. | `["admin", "read:user"]` |
| `created_at` | `DateTime` | Timestamp when the user was created. | `ISODate("2025-01-01T00:00:00Z")` |
| `updated_at` | `DateTime` | Timestamp when the user was last updated. | `ISODate("2025-01-01T00:00:00Z")` |

### Indexes

- A unique index on the `email` field to prevent duplicate accounts.
- An index on `created_at` for sorting and querying by creation date.

## `files` Collection

Stores metadata for audio files uploaded by users. The actual files are stored in AWS S3.

| Field | Type | Description | Example |
| --- | --- | --- | --- |
| `id` | `String (Primary Key)` | Custom unique identifier (`file_...`), serves as the `_id`. | `"file_5e6f7g8h"` |
| `user_id` | `String` | The `id` of the user who owns the file. | `"user_1a2b3c4d"` |
| `file_name` | `String` | The original name of the uploaded file. | `"my-audio.mp3"` |
| `file_url` | `String` | The URL of the file in the cloud storage (e.g., S3 URL). | `"https://<bucket>.s3.amazonaws.com/..."` |
| `file_type` | `String` | The MIME type of the file. | `"audio/mpeg"` |
| `file_metadata` | `Object` | Metadata about the file. | `{ "size_bytes": 5242880, "content_type": "audio/mpeg" }` |
| `created_at` | `DateTime` | Timestamp when the file was uploaded. | `ISODate("2025-01-02T10:30:00Z")` |
| `updated_at` | `DateTime` | Timestamp when the file metadata was last updated. | `ISODate("2025-01-02T10:30:00Z")` |

### Indexes

- An index on `user_id` to efficiently query files by user.
- A compound index on `(user_id, created_at)` for sorting a user's files by date.
