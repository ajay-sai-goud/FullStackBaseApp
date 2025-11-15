# Environment Variables Reference

This document lists all environment variables required for the FastAPI application.

## Required Environment Variables

### Application Configuration
```bash
APP_NAME=FastAPI
```

### Logging Configuration
```bash
LOG_LEVEL=INFO                    # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGURU_JSON_LOGS=false           # Set to true for JSON formatted logs
```

### OpenTelemetry Configuration
```bash
OTEL_SERVICE_NAME=fastapi
OTEL_EXPORTER_OTLP_ENDPOINT=      # Optional: OTLP endpoint URL
OTEL_DEBUG_LOG_SPANS=false        # Set to true to log spans to console
```

### CORS Configuration
```bash
ALLOWED_ORIGINS=http://localhost:3000    # Comma-separated list of allowed origins
ALLOWED_METHODS=*                        # Comma-separated list or * for all
ALLOWED_HEADERS=*                        # Comma-separated list or * for all
```

### Database Configuration (MongoDB)
```bash
MONGO_URI=mongodb://devadmin:devadminpass@localhost:27017/app_db
MONGO_DB_NAME=app_db
```

**Your MongoDB URI format:**
- **Host**: localhost
- **Port**: 27017
- **Username**: devadmin
- **Password**: devadminpass
- **Database**: app_db (included in URI path for authentication)
- **Full URI**: `mongodb://devadmin:devadminpass@localhost:27017/app_db`

**Important:** 
- The database name in the URI path (`/app_db`) tells MongoDB to authenticate against that database
- The `MONGO_DB_NAME` should match the database in the URI
- This is the simplest configuration for single-database applications

**Create MongoDB User in app_db:**
```bash
mongosh
use app_db
db.createUser({
  user: "devadmin",
  pwd: "devadminpass",
  roles: [
    { role: "readWrite", db: "app_db" },
    { role: "dbAdmin", db: "app_db" }
  ]
})
```

### JWT Configuration (RS256)
```bash
JWT_ALGORITHM=RS256
JWT_EXPIRATION_HOURS=24

# JWT Issuer (iss) - identifies who issued the token
# Example: https://vagent-prod.us.auth0.com/ or https://app.example.com/
JWT_ISSUER=https://app.example.com/

# JWT Audience (aud) - comma-separated list of intended recipients
# Example: https://app.in.cloudbuilders.io/,https://vagent-prod.us.auth0.com/userinfo
# Or single value: https://app.example.com/
JWT_AUDIENCE=https://app.example.com/

# RSA Private Key - Choose ONE option:
# Option 1: File path (recommended)
JWT_PRIVATE_KEY_PATH=keys/private_key.pem
# Option 2: Direct key content (leave empty if using file path)
JWT_PRIVATE_KEY=

# RSA Public Key - Choose ONE option:
# Option 1: File path (recommended)
JWT_PUBLIC_KEY_PATH=keys/public_key.pem
# Option 2: Direct key content (leave empty if using file path)
JWT_PUBLIC_KEY=
```

**Note**: Generate RSA keys using:
```bash
python scripts/generate_rsa_keys.py
```

### AWS S3 Configuration
```bash
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=your_bucket_name
AWS_REGION=us-east-1
```

## Example .env File

```bash
# Application
APP_NAME=FastAPI

# Logging
LOG_LEVEL=INFO
LOGURU_JSON_LOGS=false

# OpenTelemetry
OTEL_SERVICE_NAME=fastapi
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_DEBUG_LOG_SPANS=false

# CORS
ALLOWED_ORIGINS=http://localhost:3000
ALLOWED_METHODS=*
ALLOWED_HEADERS=*

# Database
MONGO_URI=mongodb://devadmin:devadminpass@localhost:27017/app_db
MONGO_DB_NAME=app_db

# JWT
JWT_ALGORITHM=RS256
JWT_EXPIRATION_HOURS=24
JWT_PRIVATE_KEY_PATH=keys/private_key.pem
JWT_PUBLIC_KEY_PATH=keys/public_key.pem

# AWS S3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
AWS_REGION=us-east-1

# Default Admin User
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=adminpassword
```

## Quick Setup

1. **Copy the example file** (if it exists):
   ```bash
   cp .env.example .env
   ```

2. **Create MongoDB user in app_db database**:
   ```bash
   mongosh
   use app_db
   db.createUser({
     user: "devadmin",
     pwd: "devadminpass",
     roles: [{ role: "readWrite", db: "app_db" }, { role: "dbAdmin", db: "app_db" }]
   })
   ```

3. **Update your .env file** with the MongoDB URI:
   ```bash
   MONGO_URI=mongodb://devadmin:devadminpass@localhost:27017/app_db
   ```

4. **Generate RSA keys** for JWT:
   ```bash
   python scripts/generate_rsa_keys.py
   ```

5. **Configure AWS S3** (if using cloud storage):
   - Set `AWS_ACCESS_KEY_ID`
   - Set `AWS_SECRET_ACCESS_KEY`
   - Set `S3_BUCKET_NAME`
   - Set `AWS_REGION` (default: us-east-1)

## Important Notes

- The `.env` file is in `.gitignore` and should not be committed to version control
- All variables have default values in `app/core/config.py` except for:
  - **MongoDB**: You must create a user in the `app_db` database and provide `MONGO_URI` with `authSource=app_db`
  - **JWT Keys**: You must generate RSA keys or provide them
  - **AWS S3**: Required only if uploading files to S3

## Database Collections

Your application will use the following collections in the `app_db` database:

- **users** - User accounts (id, email, hashed_password, first_name, last_name, created_at, updated_at)
- **files** - Audio file metadata (id, user_id, file_name, file_url, file_type, file_metadata, created_at, updated_at)

Collections are created automatically when you first insert data. Indexes are created on startup (see `app/core/lifespan.py`).

