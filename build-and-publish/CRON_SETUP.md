# Automated Build Setup with Cron

This guide explains how to set up a cron job to automatically build and publish the Docker image every Thursday at 2:00 AM.

## Quick Setup

### 1. Create the Credentials File

Create a secure credentials file at `~/.dockerhub-creds`:

```bash
echo "your-dockerhub-username:your-pat-or-password" > ~/.dockerhub-creds
chmod 600 ~/.dockerhub-creds
```

The file should contain a single line with the format:
```
USERNAME:PASSWORD_OR_PAT
```

### 2. Make the Wrapper Script Executable

```bash
chmod +x build-and-publish/cron-wrapper.sh
chmod +x build-and-publish/go
chmod +x build-and-publish/ingest-locally
```

### 3. Add the Cron Job

Edit your crontab:

```bash
crontab -e
```

Add the following line (adjust the path to your project directory):

```
0 2 * * 4 /path/to/roblox-engine-api-docs-mcp/build-and-publish/cron-wrapper.sh
```

The schedule `0 2 * * 4` means:
- `0` = minute 0
- `2` = hour 2 (2:00 AM)
- `*` = any day of month
- `*` = any month
- `4` = Thursday (0=Sunday, 1=Monday, ..., 6=Saturday)

### 4. Verify the Cron Job

List your cron jobs:

```bash
crontab -l
```

## Testing the Setup

To test the cron job without waiting for Thursday:

```bash
# Run the wrapper script manually
/path/to/roblox-engine-api-docs-mcp/build-and-publish/cron-wrapper.sh
```

Check the log file:

```bash
tail -f /tmp/roblox-mcp-build-*.log
```

## Monitoring

### Check Recent Logs

```bash
# Find and view the most recent log
ls -lt /tmp/roblox-mcp-build-*.log | head -1
```

### Check if Cron Job is Running

```bash
# Check cron service status
sudo systemctl status cron

# Check cron logs (Ubuntu/Debian)
grep CRON /var/log/syslog | tail -20
```

## Security Notes

- The credentials file (`~/.dockerhub-creds`) should have restrictive permissions (`chmod 600`)
- Store a Docker Hub Personal Access Token (PAT) instead of your password
- The logs may contain sensitive information - review and secure them appropriately

## Troubleshooting

### Cron Job Not Running

1. Check cron service is running:
   ```bash
   sudo systemctl status cron
   ```

2. Check for cron errors in syslog:
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

3. Ensure the script paths are absolute in the crontab

### Docker Login Fails

1. Verify credentials file format:
   ```bash
   cat ~/.dockerhub-creds
   ```

2. Test Docker login manually:
   ```bash
   cat ~/.dockerhub-creds | cut -d':' -f2- | docker login --username $(cat ~/.dockerhub-creds | cut -d':' -f1) --password-stdin
   ```

### Build Fails

1. Check the log file for errors:
   ```bash
   cat /tmp/roblox-mcp-build-*.log
   ```

2. Run the build script manually to debug:
   ```bash
   cd /path/to/roblox-engine-api-docs-mcp
   ./build-and-publish/go <username> <pat>
   ```
