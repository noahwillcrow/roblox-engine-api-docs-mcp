# Automated Build Setup with Cron

This guide explains how to set up a cron job to automatically build and publish the Docker image every Thursday at 2:00 AM.

## Prerequisites

- Docker installed on your server
- Docker Hub account with a Personal Access Token (PAT)
- Logged into Docker Hub on the host (`docker login`)

## Quick Setup

### 1. Log into Docker Hub

Run this once on your server:

```bash
docker login --username your-dockerhub-username
# Enter your Personal Access Token when prompted
```

### 2. Make Scripts Executable

```bash
chmod +x build-and-publish/cron-wrapper-docker.sh
```

### 3. Test the Setup

Run the wrapper manually to verify:

```bash
# Pass username as argument
./build-and-publish/cron-wrapper-docker.sh your-dockerhub-username

# Or set environment variable
DOCKERHUB_USERNAME=your-dockerhub-username ./build-and-publish/cron-wrapper-docker.sh
```

### 4. Add the Cron Job

Edit your crontab:

```bash
crontab -e
```

Add this line (adjust path and username):

```
0 2 * * 4 DOCKERHUB_USERNAME=yourusername /path/to/roblox-engine-api-docs-mcp/build-and-publish/cron-wrapper-docker.sh
```

## Cron Schedule Format

The schedule `0 2 * * 4` means:
- `0` = minute 0
- `2` = hour 2 (2:00 AM)
- `*` = any day of month
- `*` = any month
- `4` = Thursday (0=Sunday, 1=Monday, ..., 6=Saturday)

To change the schedule:
- Every day at 2 AM: `0 2 * * *`
- Every Sunday at 2 AM: `0 2 * * 0`
- First of every month at 2 AM: `0 2 1 * *`

Use [crontab.guru](https://crontab.guru/) to verify your schedule.

## How It Works

1. **Docker Login Check**: Verifies you're logged into Docker Hub
2. **Builder Image**: Builds a Docker image with Python, Poetry, and dependencies
3. **Run Build**: Runs a container that:
   - Mounts the host Docker socket (to build/push images)
   - Mounts the host Docker config (to use your login credentials)
   - Mounts the project directory
   - Runs the `go` script to build and push the MCP server image
4. **Logging**: All output is saved to `/tmp/roblox-mcp-build-YYYYMMDD-HHMMSS.log`

## Monitoring

### Check Cron Job is Configured

```bash
crontab -l
```

### Check Recent Logs

```bash
# Find the most recent log
ls -lt /tmp/roblox-mcp-build-*.log | head -1

# View it
tail -f /tmp/roblox-mcp-build-*.log
```

### Check if Cron is Running

```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
grep CRON /var/log/syslog | tail -20
```

## Security Notes

- Use a Docker Hub Personal Access Token (PAT) with limited scope (read, write, delete for repos)
- The PAT is stored in Docker's config.json (`~/.docker/config.json`)
- Keep your server secure since the Docker credentials are stored there
- Review and rotate your PAT regularly

## Troubleshooting

### "Not logged into Docker Hub"

Run `docker login` manually and verify:
```bash
docker info | grep Username
```

### "Cannot connect to Docker daemon"

Ensure your user is in the `docker` group:
```bash
sudo usermod -aG docker $USER
# Log out and back in
```

### Build Fails

Check the log file:
```bash
cat /tmp/roblox-mcp-build-*.log
```

### Out of Disk Space

Clean up Docker periodically:
```bash
docker system prune -f
```

### Docker Login Expired

If your Docker login expires, just run `docker login` again on the host.

## Notes

- The wrapper script keeps the last 10 log files and removes older ones automatically
- The builder image is rebuilt each time to ensure dependencies are up to date
- The `qdrant_data` directory must exist before running (run `./build-and-publish/ingest-locally` first)
