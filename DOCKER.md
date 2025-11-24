# Docker Deployment Guide for Endless Library

This guide explains how to deploy the Endless Library FastAPI application using Docker, including specific instructions for Unraid.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, but recommended)
- `config.json` and `users.json` files configured

## Configuration Files

Before running the container, you need to create two configuration files:

### 1. config.json

Create a `config.json` file with your email settings:

```json
{
    "mode": "download",
    "email_sender": "your-email@gmail.com",
    "email_receiver": "your-kindle@kindle.com",
    "email_password": "your-app-specific-password"
}
```

**Note:** For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### 2. users.json

Create a `users.json` file mapping user names to their Kindle email addresses:

```json
{
    "brian": "brianbrown2002@kindle.com",
    "alice": "alice@kindle.com"
}
```

## Quick Start with Docker Compose

1. Clone the repository and navigate to the project directory
2. Create your `config.json` and `users.json` files
3. Run:

```bash
docker-compose up -d
```

The API will be available at `http://localhost:38100`

## Manual Docker Build and Run

### Build the Image

```bash
docker build -t endless-library .
```

### Run the Container

```bash
docker run -d \
  --name endless-library-api \
  -p 38100:38100 \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $(pwd)/users.json:/app/users.json:ro \
  -v $(pwd)/downloads:/app/downloads \
  endless-library
```

## Unraid Deployment

### Option 1: Using Docker Compose Manager

1. Install the **Docker Compose Manager** plugin from Community Applications
2. Place your project files in a share (e.g., `/mnt/user/appdata/endless-library/`)
3. Create your `config.json` and `users.json` in that directory
4. Add the docker-compose.yml file
5. Start the stack from the Docker Compose Manager UI

### Option 2: Using Unraid Docker Template

1. Go to **Docker** tab in Unraid
2. Click **Add Container**
3. Configure with these settings:

**Basic Settings:**
- **Name:** `endless-library-api`
- **Repository:** Build your image first and use the tag, or use a registry
- **Network Type:** `Bridge`

**Port Mappings:**
- **Container Port:** `38100`
- **Host Port:** `38100` (or any available port)
- **Connection Type:** `TCP`

**Path Mappings:**
- **Config Path 1:**
  - Container Path: `/app/config.json`
  - Host Path: `/mnt/user/appdata/endless-library/config.json`
  - Access Mode: `Read Only`

- **Config Path 2:**
  - Container Path: `/app/users.json`
  - Host Path: `/mnt/user/appdata/endless-library/users.json`
  - Access Mode: `Read Only`

- **Downloads Path:**
  - Container Path: `/app/downloads`
  - Host Path: `/mnt/user/appdata/endless-library/downloads`
  - Access Mode: `Read/Write`

**Environment Variables:**
- **TZ:** Your timezone (e.g., `America/New_York`)

4. Click **Apply**

### Building the Image on Unraid

Since Unraid doesn't have a built-in image builder in the UI, you have two options:

#### Option A: Build on Unraid via Terminal

1. SSH into your Unraid server
2. Navigate to your project directory:
   ```bash
   cd /mnt/user/appdata/endless-library
   ```
3. Build the image:
   ```bash
   docker build -t endless-library .
   ```
4. Use `endless-library` as your repository name in the Docker template

#### Option B: Use Docker Hub or GitHub Container Registry

1. Build the image on your local machine
2. Push to Docker Hub or GHCR
3. Use that registry URL in Unraid's Docker template

## Accessing the API

Once the container is running, you can access:

- **API Documentation:** `http://your-server-ip:38100/docs`
- **Alternative Docs:** `http://your-server-ip:38100/redoc`

## API Endpoints

- `POST /search` - Search for books
- `GET /next/{session_id}` - Get next book in search results
- `GET /download/{session_id}?user=username` - Download and send book to Kindle

## Volume Mounts Explained

- **config.json** (read-only): Email configuration for sending books to Kindle
- **users.json** (read-only): User to Kindle email mappings
- **downloads/**: Temporary storage for downloaded books before sending to Kindle

## Troubleshooting

### Container won't start

Check the logs:
```bash
docker logs endless-library-api
```

### Can't access the API

- Verify the port mapping is correct
- Check if port 38100 is already in use
- Ensure firewall allows the port

### Email sending fails

- Verify `config.json` has correct email settings
- Ensure you're using an App Password for Gmail
- Check that the user exists in `users.json`

### Permission issues

If you encounter permission issues with the downloads directory:
```bash
chmod -R 777 downloads/
```

## Health Check

The container includes a health check that pings the `/docs` endpoint every 30 seconds. You can check the health status with:

```bash
docker ps
```

Look for the health status in the STATUS column.

## Stopping the Container

Using Docker Compose:
```bash
docker-compose down
```

Using Docker directly:
```bash
docker stop endless-library-api
docker rm endless-library-api
```

## Updating

To update to a new version:

1. Pull the latest code
2. Rebuild the image:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

Or with Docker directly:
```bash
docker stop endless-library-api
docker rm endless-library-api
docker build -t endless-library .
docker run -d [... same run parameters as before ...]
```
