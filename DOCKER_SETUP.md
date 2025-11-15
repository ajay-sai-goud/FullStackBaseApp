# Docker Setup Guide

This guide explains how to set up and run the fullstack application using Docker Compose.

## Prerequisites

- Docker installed
- Docker Compose installed
- AWS S3 credentials (if using cloud storage)

## Quick Start

1. **Create `.env` file** in the root directory (same as `docker-compose.yml`)
2. **Generate RSA keys** and add them to `.env`
3. **Configure environment variables** in `.env`
4. **Run Docker Compose**

## Step-by-Step Setup

### Step 1: Generate RSA Keys

```bash
cd backend_fastapi
python scripts/generate_rsa_keys.py
```

This creates:
- `backend_fastapi/keys/private_key.pem`
- `backend_fastapi/keys/public_key.pem`

### Step 2: Format Keys for .env File

```bash
cd backend_fastapi
python scripts/format_keys_for_env.py
```

This will output the keys formatted for `.env` file. Copy the output.

### Step 3: Create .env File

Create a `.env` file in the root directory (same location as `docker-compose.yml`):

```bash
# Database
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=app_db

# JWT Configuration
JWT_ALGORITHM=RS256
JWT_EXPIRATION_HOURS=24
JWT_ISSUER=https://localhost:8000/
JWT_AUDIENCE=https://localhost:3000/

# RSA Keys (paste output from format_keys_for_env.py)
JWT_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----"

JWT_PUBLIC_KEY="-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...\n-----END PUBLIC KEY-----"

# AWS S3 (optional - required for file uploads)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your_bucket_name
AWS_REGION=us-east-1

# Admin User
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=Admin@password123
```

**Important Notes:**
- Use double quotes around PEM keys
- Replace newlines with `\n` in the key strings
- Keep the `-----BEGIN` and `-----END` lines

### Step 4: Run Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### Step 5: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## Services

### Backend (FastAPI)
- **Port**: 8000
- **Build**: `./backend_fastapi`
- **Environment**: Loaded from `.env` file

### Frontend (React)
- **Port**: 3000
- **Build**: `./frontend_react`
- **API URL**: Configured to `http://localhost:8000`

### MongoDB
- **Port**: 27017
- **Image**: mongo:7
- **Data**: Persisted in `mongodb_data` volume

## Environment Variables

All environment variables are loaded from the `.env` file in the root directory.

### Required Variables

- `JWT_PRIVATE_KEY` - RSA private key (PEM format, use `\n` for newlines)
- `JWT_PUBLIC_KEY` - RSA public key (PEM format, use `\n` for newlines)
- `MONGO_URI` - MongoDB connection string
- `MONGO_DB_NAME` - Database name

### Optional Variables

- `AWS_ACCESS_KEY_ID` - AWS access key (required for S3 uploads)
- `AWS_SECRET_ACCESS_KEY` - AWS secret key (required for S3 uploads)
- `S3_BUCKET_NAME` - S3 bucket name (required for S3 uploads)
- `ADMIN_EMAIL` - Default admin email (default: admin@example.com)
- `ADMIN_PASSWORD` - Default admin password (default: Admin@password123)

## Troubleshooting

### Issue: Keys not loading
- **Solution**: Verify `.env` file is in root directory
- **Solution**: Check that keys use `\n` for newlines and are wrapped in quotes
- **Solution**: Ensure keys include `-----BEGIN` and `-----END` lines

### Issue: MongoDB connection failed
- **Solution**: Wait for MongoDB to fully start (check logs: `docker-compose logs mongodb`)
- **Solution**: Verify `MONGO_URI` uses service name: `mongodb://mongodb:27017`

### Issue: Frontend can't reach backend
- **Solution**: Verify both services are on the same network (`app-network`)
- **Solution**: Check that `REACT_APP_API_BASE_URL=http://localhost:8000` is set

### Issue: Port already in use
- **Solution**: Stop services using those ports
- **Solution**: Or change ports in `docker-compose.yml`

## Useful Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb

# Rebuild services
docker-compose up --build

# Remove volumes (clean MongoDB data)
docker-compose down -v

# Execute command in container
docker-compose exec backend bash
docker-compose exec mongodb mongosh
```

## Security Notes

- **Never commit `.env` file** to version control
- **Keep private keys secure**
- **Use different keys for production**
- **Rotate keys periodically**

## Production Considerations

For production:
1. Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
2. Use environment-specific `.env` files
3. Enable HTTPS/TLS
4. Use proper CORS configuration
5. Set up proper logging and monitoring
6. Use managed database services

