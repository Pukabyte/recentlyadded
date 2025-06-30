<div align="center">
  <a href="https://github.com/Pukabyte/recentlyadded">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="screenshots/recentlyadded.png" width="400">
      <img alt="recentlyadded" src="screenshots/recentlyadded.png" width="400">
    </picture>
  </a>
</div>

<div align="center">
  <a href="https://github.com/Pukabyte/recentlyadded/stargazers"><img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/Pukabyte/recentlyadded?label=Recently%20Added"></a>
  <a href="https://github.com/Pukabyte/recentlyadded/issues"><img alt="Issues" src="https://img.shields.io/github/issues/Pukabyte/recentlyadded" /></a>
  <a href="https://github.com/Pukabyte/recentlyadded/blob/main/LICENSE"><img alt="License" src="https://img.shields.io/github/license/Pukabyte/recentlyadded"></a>
  <a href="https://github.com/Pukabyte/recentlyadded/graphs/contributors"><img alt="Contributors" src="https://img.shields.io/github/contributors/Pukabyte/recentlyadded" /></a>
  <a href="https://discord.gg/vMSnNcd7m5"><img alt="Discord" src="https://img.shields.io/badge/Join%20discord-8A2BE2" /></a>
</div>

<div align="center">
  <p>Recently Added Media Discord Notifier for Plex and Jellyfin.</p>
</div>

# Recently Added

A Python application that monitors your Plex or Jellyfin server for recently added media and sends summary notifications to Discord via webhooks. An unobtrusive way to alert users of recently added content.

## Features

- **Multi-Platform Support**: Works with both Plex and Jellyfin servers
- Monitors multiple libraries (Movies, TV Shows, Kids content, Anime, 4K, etc.)
- Configurable lookback period for media additions
- Discord webhook notifications with rich embeds
- Support for different media types and quality categories
- Multi-platform Docker support (amd64, arm64, arm/v7)

## Prerequisites

- Plex Media Server **OR** Jellyfin Media Server
- Discord webhook URL
- Docker (optional, for containerized deployment)

## Platform Setup

### For Plex Users

1. Get your Plex token from [plex.tv](https://www.plex.tv/claim/)
2. Use the existing configuration format with `platform: "plex"`

### For Jellyfin Users

1. Get your Jellyfin API key:
   - Log into your Jellyfin web interface
   - Go to **Dashboard** → **Advanced** → **API Keys**
   - Click **New API Key**
   - Give it a name (e.g., "Discord Notifications")
   - Copy the generated API key

2. Find your library IDs by running:
   ```bash
   python find_jellyfin_libraries.py
   ```

3. Use the configuration format with `platform: "jellyfin"`

## Configuration

Create a `config.yml` file in the same directory as `main.py`. Use `config-unified-example.yml` as a template.

### Key Configuration Options

```yaml
# Platform selection: "plex" or "jellyfin"
platform: "plex"

# For Plex
plex:
    url: "http://plex:32400"
    token: "{your_plex_token}"
    libraries:
        movies: Movies
        shows: TV
        # ... other libraries

# For Jellyfin
jellyfin:
    url: "http://jellyfin:8096"
    api_key: "{your_jellyfin_api_key}"
    libraries:
        movies: "your_movies_library_id"
        shows: "your_tv_library_id"
        # ... other libraries

# Discord webhook configuration
plex_discord_media_updates:  # or jellyfin_discord_media_updates
    webhook: "https://discord.com/api/webhooks/your_webhook_url"
    lookback_period: "4h"
    # ... other settings
```

## Installation

### Manual Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Copy the example configuration:
```bash
cp config-unified-example.yml config.yml
```

3. Edit the configuration file with your settings:
```bash
nano config.yml
```

4. Run the script:
```bash
python main.py
```

### Docker Deployment

1. Create a `docker-compose.yml` file:
```yaml
version: '3'

services:
  recentlyadded:
    image: ghcr.io/pukabyte/recentlyadded:latest
    container_name: recentlyadded
    restart: unless-stopped
    volumes:
      - ./config.yml:/app/config.yml
    environment:
      - TZ=UTC 
    networks:
      - your_network

networks:
  your_network:
    external: true
```

2. Run the container:
```bash
docker compose up -d
```

## Logging

Logs are stored in the `/app/logs` directory inside the container. The log format includes:
- Timestamp
- Log level
- Message

## Troubleshooting

### Common Issues

1. **"Failed to get libraries" error**
   - Check your server URL and authentication credentials
   - Ensure your server is accessible
   - Verify API keys/tokens have the necessary permissions

2. **"Library not found" errors**
   - For Plex: Check library names match exactly
   - For Jellyfin: Use the helper script to get correct library IDs

3. **No media found**
   - Check your lookback period setting
   - Verify that media was actually added within the specified time period
   - Check that library configurations are correct

### Getting Help

If you encounter issues:
1. Check the logs in `/app/logs/app.log`
2. Verify your configuration settings
3. Test your server connection using the helper scripts

## Differences Between Platforms

| Feature | Plex | Jellyfin |
|---------|------|----------|
| Authentication | Token | API Key |
| Library Reference | Names | IDs |
| Date Filtering | Plex format | ISO date format |
| API | PlexAPI library | REST API calls |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 