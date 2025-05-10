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
pplex:
    url: "http://plex:32400"
    token: "{plex_token}"
    # These library names must exactly match the library names in Plex.
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
    # OPTIONALLY add push-monitoring URLs for services like Uptime Kuma or Healthchecks.io
    uptime_status: ""
    
    # The discord webhook URL that will be used if not in testing mode (i.e. if testing_mode is set to False)
    webhook: "https://discord.com/api/webhooks/1053465321685655602/{webhook_token}"
    
    # Media added since this long ago will be listed. 
    # FORMAT: "1m", "1h", "1d", "1w" respectively correspond to 1 minute, 1 hour, 1 day, 1 week.
    lookback_period: "4h"
    
    # Skipped libraries will not be scanned or included in the webhook message
    skip_libraries:
        movies: False
        shows: False
        kids_movies: False
        kids_shows: False
        anime_movies: False
        anime_shows: False
        uhd_movies: False
        uhd_shows: False
        mux_movies: True
        mux_shows: True
    
    # Choose whether to show the total number of new episodes in the TV Show embed title
    show_total_episode_count: True
    
    # Choose whether to show the number of new episodes for each individual show in the TV Show embed title.
    show_episode_count_per_show: True
    
    message_options:
        # Group-specific titles for webhook messages
        titles:
            standard: "Recently Added to HD Libraries in the last"
            kids: "Recently Added to Kids Libraries in the last"
            anime: "Recently Added to Anime Libraries in the last"
            uhd: "Recently Added to 4K Libraries in the last"
            mux: "Recently Added to Remux Libraries in the last"

    embed_options:
        # Optional thumbnail that will go in all embeds. Set to an empty string ("") to disable it or set to a direct image url string to enable it.
        thumbnail: "" 
        
        # The symbol to denote each new entry in the lists in the embeds. Can be replaced with emotes (e.g. :point_right:).
        bullet: "•"
        
        # Keep the "0x" and change the last 6 characters to the hex codes of your preferred colours.
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
        
        # Optional emotes to be used in the title for each embed. Must be in quotes.
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

    # The message that will display if a list is too long and needs to be cut short. Should be less than 90 characters. Will be bolded and appended with two newlines to the end of the list.
    overflow_footer: "and more... check out the library for the rest!"

    # Library groups configuration
    library_groups:
        standard:
            libraries:
                - movies
                - shows
        kids:
            libraries:
                - kids_movies
                - kids_shows
        anime:
            libraries:
                - anime_movies
                - anime_shows
        uhd:
            libraries:
                - uhd_movies
                - uhd_shows
        mux:
            libraries:
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