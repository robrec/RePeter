# Docker Setup for PubKeySearcher

This document describes how to use the Ed25519 PubKeySearcher with Docker.

## Prerequisites

- Docker installed ([Docker Desktop](https://www.docker.com/products/docker-desktop) for Windows/Mac or Docker Engine for Linux)
- Docker Compose (usually included with Docker Desktop)

## Quick Start

### 1. Build Docker Image

```bash
docker-compose build
```

### 2. Start Container

```bash
docker-compose up
```

or in background:

```bash
docker-compose up -d
```

### 3. View Logs (when running in background)

```bash
docker-compose logs -f
```

### 4. Stop Container

```bash
docker-compose down
```

or with `Ctrl+C` when running in foreground.

## Manual Docker Commands (without docker-compose)

### Build Image

```bash
docker build -t pubkey-searcher .
```

### Run Container

```bash
docker run -it --rm \
  -v "$(pwd)/found_keys:/app/found_keys" \
  -v "$(pwd)/searchFor.txt:/app/searchFor.txt:ro" \
  pubkey-searcher
```

**Windows PowerShell:**
```powershell
docker run -it --rm `
  -v "${PWD}/found_keys:/app/found_keys" `
  -v "${PWD}/searchFor.txt:/app/searchFor.txt:ro" `
  pubkey-searcher
```

## Adjust Configuration

### Change Patterns

Edit `searchFor.txt` on the host system. Changes are automatically applied (with active volume mount).

### Use Custom Pattern File

**Method 1: Environment Variable**

Edit `docker-compose.yml`:

```yaml
environment:
  - PATTERNS_FILE=myPatterns.txt
volumes:
  - ./found_keys:/app/found_keys
  - ./myPatterns.txt:/app/myPatterns.txt:ro  # Mount your custom file
```

**Method 2: Replace searchFor.txt**

Simply replace the content of `searchFor.txt` or create a symbolic link.

### CPU Limitation

Edit `docker-compose.yml` and adjust the `cpus` value:

```yaml
cpus: "4.0"  # Limit to 4 CPU cores
```

### Memory Limitation

Add to `docker-compose.yml`:

```yaml
mem_limit: 2g  # Limit to 2GB RAM
```

## Volumes

The Docker setup uses two volumes:

1. **`./found_keys`** - Persistent storage for found keys
2. **`./searchFor.txt`** - Pattern list (read-only)

**Note:** When using a custom pattern file via `PATTERNS_FILE` environment variable, make sure to also mount that file as a volume.

All found keys are saved directly on the host system.

## Performance

The Docker container uses all available CPU cores by default. Performance should be comparable to native execution.

**Tip for maximum performance:**
- Ensure Docker Desktop has enough CPU cores and RAM allocated (Settings → Resources)
- Recommended: All CPU cores and at least 2GB RAM

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs

# Check container status
docker-compose ps
```

### No keys are found

This is normal and depends on the patterns. Check the logs for progress updates.

### Volume Problems on Windows

Make sure that:
- Docker Desktop has permission to access the directory
- The path is correctly shared in Docker settings (File Sharing)

### Permission Errors

On Linux, permission problems may occur:

```bash
# Adjust permissions
chmod -R 777 found_keys/
```

## Best Practices

1. **Regular Backups**: Backup the `found_keys/` folder regularly
2. **Pattern Optimization**: Use realistic pattern lengths (4-6 characters)
3. **Monitoring**: Check the logs regularly for found keys
4. **Resources**: Run the container on a dedicated system for best performance

## Running Container in Background

For long-term search:

```bash
# Start with automatic restart
docker-compose up -d --restart unless-stopped

# Check status
docker-compose ps

# View logs live
docker-compose logs -f

# Stop
docker-compose stop
```

## Multi-Container Setup (Optional)

For parallel search with different pattern lists:

```yaml
version: '3.8'

services:
  searcher-1:
    build: .
    volumes:
      - ./found_keys:/app/found_keys
      - ./searchFor.txt:/app/searchFor.txt:ro
    cpus: "2.0"
    
  searcher-2:
    build: .
    volumes:
      - ./found_keys:/app/found_keys
      - ./searchFor_long.txt:/app/searchFor.txt:ro
    cpus: "2.0"
```

## Security

- ⚠️ **Private Keys**: The `found_keys/` folder contains Private Keys! Store securely!
- 🔒 **Encrypt Backups**: Use encrypted backups for found keys
- 🚫 **Don't Expose**: Don't unnecessarily expose the container on the network

## Support

If you have problems, check:
1. Docker version: `docker --version`
2. Docker Compose version: `docker-compose --version`
3. Logs: `docker-compose logs`
4. System resources in Docker Desktop settings
