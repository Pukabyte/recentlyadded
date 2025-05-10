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
  <p>Recently Added Media Discord Notifier for Plex.</p>
</div>

# Recently Added

A Python application that monitors your Plex server for recently added media and sends summary notifications to Discord via webhooks. An unobtrusive way to alert users of recently added content.

## Features

- Monitors multiple Plex libraries (Movies, TV Shows, Kids content, Anime, 4K, etc.)
- Configurable lookback period for media additions
- Discord webhook notifications with rich embeds
- Support for different media types and quality categories
- Multi-platform Docker support (amd64, arm64, arm/v7)

## Prerequisites

- Plex Media Server
- Discord webhook URL
- Docker (optional, for containerized deployment)

## Configuration

Create a `config.yml` file in the same directory as `main.py` with the following structure:

```yaml
plex:
  url: "http://your-plex-server:32400"
  token: "your-plex-token"
  libraries:
    movies: Movies
    shows: TV
    kids_movies: Movies - Kids
    kids_shows: TV - Kids
    anime_movies: Movies - Anime
    anime_shows: TV - Anime
    uhd_movies: Movies - 4K
    uhd_shows: TV - 4K
    mux_movies: Movies - Remux
    mux_shows: TV - Remux

plex_discord_media_updates:
  webhook: "your-discord-webhook-url"
  lookback_period: "4h"  # Format: number + unit (m/h/d/w)
  testing_mode: false
  skip_libraries:
    movies: false
    shows: false
    kids_movies: false
    kids_shows: false
    anime_movies: false
    anime_shows: false
    uhd_movies: false
    uhd_shows: false
    mux_movies: false
    mux_shows: false
  show_total_episode_count: true
  show_episode_count_per_show: true
  message_options:
    titles:
      default: "Recently Added Media"
  embed_options:
    thumbnail: "your-thumbnail-url"
    bullet: "•"
    movies_colour: 0xFB8800
    shows_colour: 0xDE4501
    kids_movies_colour: 0xFB8800
    kids_shows_colour: 0xDE4501
    anime_movies_colour: 0xFB8800
    anime_shows_colour: 0xDE4501
    uhd_movies_colour: 0xFB8800
    uhd_shows_colour: 0xDE4501
    mux_movies_colour: 0xFB8800
    mux_shows_colour: 0xDE4501
    movies_emote: ":clapper:"
    shows_emote: ":tv:"
    kids_movies_emote: ":clapper:"
    kids_shows_emote: ":tv:"
    anime_movies_emote: ":clapper:"
    anime_shows_emote: ":tv:"
    uhd_movies_emote: ":clapper:"
    uhd_shows_emote: ":tv:"
    mux_movies_emote: ":clapper:"
    mux_shows_emote: ":tv:"
  overflow_footer: "and more... check out the library for the rest!"
  library_groups:
    default:
      libraries:
        - movies
        - shows
        - kids_movies
        - kids_shows
        - anime_movies
        - anime_shows
        - uhd_movies
        - uhd_shows
        - mux_movies
        - mux_shows
```

## Docker Deployment

1. Pull the latest image:
```bash
git clone https://github.com/Pukabyte/recentlyadded.git
```
2. cd into the directory

3. Create a copy of the config-example.yml` and edit the file with your settings
```bash
cp config-example.yml config.yml
nano config.yml
```

4. Run the container:
```bash
docker compose up -d
```

## Logging

Logs are stored in the `/app/logs` directory inside the container. The log format includes:
- Timestamp
- Log level
- Message

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 