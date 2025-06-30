# -*- coding: utf-8 -*-
import re
import requests
import sys
import time
import yaml
import logging
from collections import Counter
from dhooks import Webhook, Embed
from pathlib import Path
from plexapi.server import PlexServer
import schedule
import threading
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-7s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

'''
------------------------------------------------------------------------------
PURPOSE

This script is meant to check your Plex or Jellyfin server, retrieve lists of
shows and movies that are in the Recently Added sections, count and
format them nicely, and then output to a message via discord webhook.

If the lists of media (one for Movies and one for TV) are longer than
discord's max message length (currently set as 4096 chars but can be changed
in the "USER OPTIONS" section below), they will be cut down to size.

i.e: If the sum of the length of both lists is over the
max length, they will each be trimmed down to half of the max size.

The script is meant to be run on a schedule (e.g. via crontab or unraid
user scripts). By default, it should be run every 24 hours, but if you
prefer to run it at a different interval, be sure to change the
lookback_period variable in the "USER OPTIONS" section below.

To get the script working with minimal configuration, you will need to change
these variables to match your plex/jellyfin/discord info; they're in the
"USER OPTIONS" section below.

NOTE: Do not set the lookback_period variable to be too far back, or the list
of media may be cut off.

------------------------------------------------------------------------------
DEPENDENCIES

This script requires Python 3, along with the Python modules outlined in
the associated "pip_requirements.txt" file. The modules can be installed by
executing the command in the same folder as pip_requirements.txt:

pip install -r pip_requirements.txt
------------------------------------------------------------------------------
CHANGELOG
~ v2.0 - 2024-01-XX
- Added Jellyfin support alongside existing Plex functionality
- Added platform selection in configuration
- Updated configuration structure to support both platforms

~ v1.3 - 2022-05-20
- Switched string generation to use f-strings
- Cleaned up unnecessary code

~ v1.2 - 2022-04-27
- Refactored user variables to be configured via an external secrets file.
- Added a function to ping uptime status monitors

~ v1.1 - 2022-03-19
- Made it so that in case there are too many recently added shows/movies,
the list(s) will automatically be trimmed down to a size that can still be
sent via webhook. Before, if one or both lists were too long, the webhook
message would simply fail and not get sent.

~ v1.0 - 2022-03-17
- Initial build
------------------------------------------------------------------------------
'''
start_time = int(time.time())

# Setting variables from config file
with open(Path(__file__).with_name("config.yml"), encoding="utf-8") as file:
    config = yaml.safe_load(file)

# Determine platform (plex or jellyfin)
platform = config.get("platform", "plex").lower()
if platform not in ["plex", "jellyfin"]:
    logger.error("Platform must be either 'plex' or 'jellyfin'")
    sys.exit(1)

logger.info(f"Using platform: {platform}")

if platform == "plex":
    script_config = config["plex_discord_media_updates"]
    try:
        testing_mode = script_config["testing_mode"]
    except:
        testing_mode = False
    try:
        uptime_status = config["uptime_status"]["plex_discord_media_updates"]
    except:
        uptime_status = None
    plex_url = config["plex"]["url"]
    plex_token = config["plex"]["token"]
    webhook_url = script_config["webhook"]
    lookback_period = script_config["lookback_period"]
    skip_libraries = script_config["skip_libraries"]
    show_total_episodes = script_config["show_total_episode_count"]
    show_individual_episodes = script_config["show_episode_count_per_show"]
    message_title = script_config["message_options"]["titles"]
    embed_options = script_config["embed_options"]
    embed_thumbnail = embed_options["thumbnail"]
    bullet = embed_options["bullet"]
    max_length_exceeded_msg = script_config["overflow_footer"]

    # Library categories and their settings
    library_categories = {
        "movies": {
            "library": config["plex"]["libraries"]["movies"],
            "colour": embed_options["movies_colour"],
            "emote": embed_options["movies_emote"],
            "skip": skip_libraries["movies"]
        },
        "shows": {
            "library": config["plex"]["libraries"]["shows"],
            "colour": embed_options["shows_colour"],
            "emote": embed_options["shows_emote"],
            "skip": skip_libraries["shows"]
        },
        "kids_movies": {
            "library": config["plex"]["libraries"]["kids_movies"],
            "colour": embed_options["kids_movies_colour"],
            "emote": embed_options["kids_movies_emote"],
            "skip": skip_libraries["kids_movies"]
        },
        "kids_shows": {
            "library": config["plex"]["libraries"]["kids_shows"],
            "colour": embed_options["kids_shows_colour"],
            "emote": embed_options["kids_shows_emote"],
            "skip": skip_libraries["kids_shows"]
        },
        "anime_movies": {
            "library": config["plex"]["libraries"]["anime_movies"],
            "colour": embed_options["anime_movies_colour"],
            "emote": embed_options["anime_movies_emote"],
            "skip": skip_libraries["anime_movies"]
        },
        "anime_shows": {
            "library": config["plex"]["libraries"]["anime_shows"],
            "colour": embed_options["anime_shows_colour"],
            "emote": embed_options["anime_shows_emote"],
            "skip": skip_libraries["anime_shows"]
        },
        "uhd_movies": {
            "library": config["plex"]["libraries"]["uhd_movies"],
            "colour": embed_options["uhd_movies_colour"],
            "emote": embed_options["uhd_movies_emote"],
            "skip": skip_libraries["uhd_movies"]
        },
        "uhd_shows": {
            "library": config["plex"]["libraries"]["uhd_shows"],
            "colour": embed_options["uhd_shows_colour"],
            "emote": embed_options["uhd_shows_emote"],
            "skip": skip_libraries["uhd_shows"]
        },
        "mux_movies": {
            "library": config["plex"]["libraries"]["mux_movies"],
            "colour": embed_options["mux_movies_colour"],
            "emote": embed_options["mux_movies_emote"],
            "skip": skip_libraries["mux_movies"]
        },
        "mux_shows": {
            "library": config["plex"]["libraries"]["mux_shows"],
            "colour": embed_options["mux_shows_colour"],
            "emote": embed_options["mux_shows_emote"],
            "skip": skip_libraries["mux_shows"]
        }
    }
else:  # jellyfin
    script_config = config["jellyfin_discord_media_updates"]
    try:
        testing_mode = script_config["testing_mode"]
    except:
        testing_mode = False
    try:
        uptime_status = config["uptime_status"]["jellyfin_discord_media_updates"]
    except:
        uptime_status = None
    jellyfin_url = config["jellyfin"]["url"]
    jellyfin_api_key = config["jellyfin"]["api_key"]
    webhook_url = script_config["webhook"]
    lookback_period = script_config["lookback_period"]
    skip_libraries = script_config["skip_libraries"]
    show_total_episodes = script_config["show_total_episode_count"]
    show_individual_episodes = script_config["show_episode_count_per_show"]
    message_title = script_config["message_options"]["titles"]
    embed_options = script_config["embed_options"]
    embed_thumbnail = embed_options["thumbnail"]
    bullet = embed_options["bullet"]
    max_length_exceeded_msg = script_config["overflow_footer"]

    # Library categories and their settings
    library_categories = {
        "movies": {
            "library": config["jellyfin"]["libraries"]["movies"],
            "colour": embed_options["movies_colour"],
            "emote": embed_options["movies_emote"],
            "skip": skip_libraries["movies"]
        },
        "shows": {
            "library": config["jellyfin"]["libraries"]["shows"],
            "colour": embed_options["shows_colour"],
            "emote": embed_options["shows_emote"],
            "skip": skip_libraries["shows"]
        },
        "kids_movies": {
            "library": config["jellyfin"]["libraries"]["kids_movies"],
            "colour": embed_options["kids_movies_colour"],
            "emote": embed_options["kids_movies_emote"],
            "skip": skip_libraries["kids_movies"]
        },
        "kids_shows": {
            "library": config["jellyfin"]["libraries"]["kids_shows"],
            "colour": embed_options["kids_shows_colour"],
            "emote": embed_options["kids_shows_emote"],
            "skip": skip_libraries["kids_shows"]
        },
        "anime_movies": {
            "library": config["jellyfin"]["libraries"]["anime_movies"],
            "colour": embed_options["anime_movies_colour"],
            "emote": embed_options["anime_movies_emote"],
            "skip": skip_libraries["anime_movies"]
        },
        "anime_shows": {
            "library": config["jellyfin"]["libraries"]["anime_shows"],
            "colour": embed_options["anime_shows_colour"],
            "emote": embed_options["anime_shows_emote"],
            "skip": skip_libraries["anime_shows"]
        },
        "uhd_movies": {
            "library": config["jellyfin"]["libraries"]["uhd_movies"],
            "colour": embed_options["uhd_movies_colour"],
            "emote": embed_options["uhd_movies_emote"],
            "skip": skip_libraries["uhd_movies"]
        },
        "uhd_shows": {
            "library": config["jellyfin"]["libraries"]["uhd_shows"],
            "colour": embed_options["uhd_shows_colour"],
            "emote": embed_options["uhd_shows_emote"],
            "skip": skip_libraries["uhd_shows"]
        },
        "mux_movies": {
            "library": config["jellyfin"]["libraries"]["mux_movies"],
            "colour": embed_options["mux_movies_colour"],
            "emote": embed_options["mux_movies_emote"],
            "skip": skip_libraries["mux_movies"]
        },
        "mux_shows": {
            "library": config["jellyfin"]["libraries"]["mux_shows"],
            "colour": embed_options["mux_shows_colour"],
            "emote": embed_options["mux_shows_emote"],
            "skip": skip_libraries["mux_shows"]
        }
    }

# Character limit of a discord message including embeds
message_max_length = 4000

if testing_mode:
    webhook_url = script_config["testing"]["webhook"]

class JellyfinClient:
    def __init__(self, url, api_key):
        self.url = url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            'X-Emby-Token': api_key,
            'Content-Type': 'application/json'
        }
    
    def get_libraries(self):
        """Get all libraries from Jellyfin"""
        response = requests.get(f"{self.url}/Users/Items", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get libraries: {response.status_code}")
    
    def get_library_items(self, library_id, item_type=None, date_added_after=None):
        """Get items from a specific library"""
        params = {
            'ParentId': library_id,
            'IncludeItemTypes': item_type,
            'Recursive': True,
            'SortBy': 'DateCreated',
            'SortOrder': 'Descending'
        }
        
        if date_added_after:
            params['DateCreated'] = f">{date_added_after}"
        
        response = requests.get(f"{self.url}/Users/Items", headers=self.headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get library items: {response.status_code}")
    
    def get_item(self, item_id):
        """Get a specific item by ID"""
        response = requests.get(f"{self.url}/Users/Items/{item_id}", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to get item: {response.status_code}")

def clean_year(media):
    """
    Takes a Show/Movie object and returns the title of it with the year
    properly appended. Prevents media with the year already in the title
    from having duplicate years. (e.g., avoids situations like
    "The Flash (2014) (2014)").

    Arguments:
    media -- an object with both .title and .year variables (Plex) or dict with Name and ProductionYear (Jellyfin)
    """
    title = ""
    # year_regex matches any string ending with a year between 1000-2999 in
    # parentheses. e.g. "The Flash (2014)"
    year_regex = re.compile(".*\([12][0-9]{3}\)$")
    
    if platform == "plex":
        title += media.title
        if not year_regex.match(media.title):
            title += " (" + str(media.year) + ")"
    else:  # jellyfin
        title += media.get('Name', 'Unknown')
        if not year_regex.match(title):
            year = media.get('ProductionYear')
            if year:
                title += f" ({year})"
    
    return title


def trim_on_newlines(long_string, max_length):
    """
    Takes a long multi-line string and a max length, and returns a subsection
    of the string that's the max length or shorter, that ends before a
    newline.

    Arguments:
    long_string -- string; any string with a newline character
    max_length -- integer; denotes the max length to trim the string down to
    """
    if len(long_string) > max_length:
        end = long_string.rfind("\n", 0, max_length)
        return long_string[:end] + max_length_exceeded_msg
    else:
        return long_string + max_length_exceeded_msg


def create_embeds(embed_title, embed_description, embed_color, max_length, webhook_embeds):
    """
    Creates an embed with data from the given arguments, but modifies the
    description of the embed so be below a given amount of characters. Will
    only trim the embed at the end of a line to avoid partial lines, while
    still keeping the description below max_length.

    Arguments:
    embed_title -- title for the embed
    embed_description -- description for the embed
    embed_color -- colour for the embed
    max_length -- integer; the max length for the embed's description
    webhook_embeds -- list to append the created embed to
    """
    if len(embed_description) > max_length:
        embed_description = trim_on_newlines(embed_description, max_length)
    embed = Embed(
        title=embed_title,
        description=embed_description,
        color=embed_color)
    webhook_embeds.append(embed)


def parse_lookback_period(lookback_period):
    """Convert lookback period string to datetime"""
    unit = lookback_period[-1]
    value = int(lookback_period[:-1])
    
    now = datetime.now()
    if unit == 'm':
        return now - timedelta(minutes=value)
    elif unit == 'h':
        return now - timedelta(hours=value)
    elif unit == 'd':
        return now - timedelta(days=value)
    elif unit == 'w':
        return now - timedelta(weeks=value)
    else:
        raise ValueError(f"Invalid lookback period unit: {unit}")


def run_update():
    """
    Main function that runs the update process
    """
    logger.info("Starting update")
    start_time = int(time.time())
    total_webhooks = 0
    library_summary = {}

    # Formatting strings from user variables section
    bullet_local = bullet + " "
    max_length_exceeded_msg_local = f"\n\n**{max_length_exceeded_msg}**"
    # Checks whether the lookback period should be specified
    # in plural and makes the message text look more natural.
    period_dict = {
        "m": "minute",
        "h": "hour",
        "d": "day",
        "w": "week",
    }

    # Builds the webhook message that includes the max age of the new media
    if lookback_period[:-1] == "1":
        lookback_text = period_dict[lookback_period[-1]]
    else:
        lookback_text = (f"{lookback_period[:-1]}"
                         f" {period_dict[lookback_period[-1]]}s")

    logger.info(f"Looking back {lookback_text}")

    # Initialize platform-specific connection
    if platform == "plex":
        try:
            plex = PlexServer(plex_url, plex_token)
            webhook = Webhook(webhook_url)
            logger.info("Connected to Plex")
        except Exception as e:
            logger.error(f"Plex connection failed: {str(e)}")
            return
    else:  # jellyfin
        try:
            jellyfin = JellyfinClient(jellyfin_url, jellyfin_api_key)
            webhook = Webhook(webhook_url)
            logger.info("Connected to Jellyfin")
        except Exception as e:
            logger.error(f"Jellyfin connection failed: {str(e)}")
            return

    logger.info("Collecting Recently Added Media")

    # Process each group separately
    for group_name, group_config in script_config["library_groups"].items():
        webhook_embeds = []
        group_title = f"_ _\n**{script_config['message_options']['titles'][group_name]} {lookback_text}:**"

        # Process each category in the current group
        for category in group_config["libraries"]:
            settings = library_categories[category]
            if settings["skip"]:
                continue

            try:
                is_movie = "movies" in category

                if platform == "plex":
                    library = plex.library.section(settings["library"])

                    if is_movie:
                        # Process movies
                        new_media = library.search(filters={"addedAt>>": lookback_period})
                        if not new_media:
                            continue

                        media_str = bullet_local
                        new_media_formatted = [clean_year(item) for item in new_media]
                        total_items = len(new_media_formatted)
                        media_str += ("\n" + bullet_local).join(new_media_formatted)
                        library_summary[settings['library']] = total_items

                        # Build title
                        media_type = "Movie"
                        if total_items != 1:
                            media_type += "s"
                        title = f"{total_items} {media_type} {settings['emote']}"

                    else:
                        # Process TV shows
                        new_eps = library.searchEpisodes(filters={"addedAt>>": lookback_period})
                        if not new_eps:
                            continue

                        new_shows = []
                        for episode in new_eps:
                            new_shows.append(clean_year(
                                plex.fetchItem(episode.grandparentRatingKey)))

                        counted_shows = Counter(new_shows)
                        show_list = []
                        total_episodes = 0

                        for counted_show in counted_shows:
                            episode_count = counted_shows[counted_show]
                            total_episodes += episode_count
                            episodes_counted = "episode"
                            if episode_count > 1:
                                episodes_counted += "s"
                            if show_individual_episodes:
                                show_list.append(f"{bullet_local}{counted_show} -"
                                               f" *{episode_count} {episodes_counted}*")
                            else:
                                show_list.append(bullet_local + counted_show)
                        show_list.sort()
                        total_shows = len(show_list)
                        media_str = "\n".join(show_list)
                        library_summary[settings['library']] = total_episodes

                        # Build title
                        show_type = "Show"
                        episode_type = "Episode"
                        if total_shows > 1:
                            episode_type += "s"
                            show_type += "s"
                        elif total_episodes > 1:
                            show_type += "s"

                        if show_total_episodes:
                            title = (f"{total_shows} {show_type} /"
                                    f" {total_episodes} {episode_type}"
                                    f" {settings['emote']}")
                        else:
                            title = f"{total_shows} {show_type} {settings['emote']}"

                else:  # jellyfin
                    library_id = settings["library"]
                    
                    # Calculate the date threshold for Jellyfin
                    date_threshold = parse_lookback_period(lookback_period)
                    date_threshold_str = date_threshold.strftime("%Y-%m-%d")

                    if is_movie:
                        # Process movies
                        item_type = "Movie"
                        new_media_data = jellyfin.get_library_items(library_id, item_type, date_threshold_str)
                        new_media = new_media_data.get('Items', [])
                        
                        if not new_media:
                            continue

                        media_str = bullet_local
                        new_media_formatted = [clean_year(item) for item in new_media]
                        total_items = len(new_media_formatted)
                        media_str += ("\n" + bullet_local).join(new_media_formatted)
                        library_summary[settings['library']] = total_items

                        # Build title
                        media_type = "Movie"
                        if total_items != 1:
                            media_type += "s"
                        title = f"{total_items} {media_type} {settings['emote']}"

                    else:
                        # Process TV shows
                        item_type = "Episode"
                        new_eps_data = jellyfin.get_library_items(library_id, item_type, date_threshold_str)
                        new_eps = new_eps_data.get('Items', [])
                        
                        if not new_eps:
                            continue

                        new_shows = []
                        for episode in new_eps:
                            # Get the series information
                            series_id = episode.get('SeriesId')
                            if series_id:
                                series = jellyfin.get_item(series_id)
                                new_shows.append(clean_year(series))

                        counted_shows = Counter(new_shows)
                        show_list = []
                        total_episodes = 0

                        for counted_show in counted_shows:
                            episode_count = counted_shows[counted_show]
                            total_episodes += episode_count
                            episodes_counted = "episode"
                            if episode_count > 1:
                                episodes_counted += "s"
                            if show_individual_episodes:
                                show_list.append(f"{bullet_local}{counted_show} -"
                                               f" *{episode_count} {episodes_counted}*")
                            else:
                                show_list.append(bullet_local + counted_show)
                        show_list.sort()
                        total_shows = len(show_list)
                        media_str = "\n".join(show_list)
                        library_summary[settings['library']] = total_episodes

                        # Build title
                        show_type = "Show"
                        episode_type = "Episode"
                        if total_shows > 1:
                            episode_type += "s"
                            show_type += "s"
                        elif total_episodes > 1:
                            show_type += "s"

                        if show_total_episodes:
                            title = (f"{total_shows} {show_type} /"
                                    f" {total_episodes} {episode_type}"
                                    f" {settings['emote']}")
                        else:
                            title = f"{total_shows} {show_type} {settings['emote']}"

                # Create embed for this category
                create_embeds(title, media_str, settings["colour"], message_max_length, webhook_embeds)
            except Exception as e:
                logger.error(f"Error in {settings['library']}: {str(e)}")
                continue

        # Adds thumbnail image to embeds if specified
        [embed.set_thumbnail(embed_thumbnail) for embed in webhook_embeds]

        # Sending webhook for this group only if there are embeds
        if webhook_embeds:
            try:
                webhook.send(group_title, embeds=webhook_embeds)
                total_webhooks += 1
            except Exception as err:
                logger.error(f"Webhook failed for {group_name}: {str(err)}")

    # Log summary
    for library, count in library_summary.items():
        logger.info(f"{library}: {count}")
    logger.info(f"Webhooks sent: {total_webhooks}")

    # Ping uptime status monitor if specified
    if uptime_status:
        try:
            requests.get(f"{uptime_status}{int(time.time()) - start_time}")
        except Exception as err:
            logger.error(f"Uptime ping failed: {str(err)}")

    logger.info(f"Waiting for {lookback_text}")

def run_scheduler():
    """
    Function to run the scheduler in a separate thread
    """
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    logger.info("Starting")
    
    # Schedule the job based on lookback period
    unit = lookback_period[-1]
    value = int(lookback_period[:-1])
    
    if unit == 'm':
        schedule.every(value).minutes.do(run_update)
        logger.info(f"Schedule: every {value} minutes")
    elif unit == 'h':
        schedule.every(value).hours.do(run_update)
        logger.info(f"Schedule: every {value} hours")
    elif unit == 'd':
        schedule.every(value).days.do(run_update)
        logger.info(f"Schedule: every {value} days")
    elif unit == 'w':
        schedule.every(value).weeks.do(run_update)
        logger.info(f"Schedule: every {value} weeks")
    
    # Run initial update
    run_update()
    
    # Keep main thread alive and handle the scheduler
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping")
