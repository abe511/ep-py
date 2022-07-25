import os
import re
import sys
import json
import logging
import argparse
import requests
from bs4 import BeautifulSoup as bs

from datetime import datetime
# from dateparser import parse
from dateutil.parser import parse

__version__ = "0.1.2"
PATH = os.path.dirname(__file__)

def get_rss_feed(url, filename):
    """
    Downloads RSS feed, writes it into an XML file and parses it using BS.

        Parameters:
            url (string): A string of the RSS feed url

        Returns:
            contents (object): A bs4.BeautifulSoup object with the contents of the feed
    """

    try:
        logging.info(f"Fetching feed from {url}")
        response = requests.get(url)
    except Exception:
        if(response.status_code == 404):
            logging.error(f"No RSS found on {url}")
        else:
            logging.error("Connection error")
        sys.exit(1)
    else:
        if(response.status_code == 200):
            logging.info("Feed contents downloaded")
            try:
                logging.info("Caching feed")
                if(not os.path.isdir(PATH + "cache")):
                    os.mkdir(PATH + "cache")
                with open(f"{PATH}cache/{filename}.xml", "w") as xml_file:
                    xml_file.write(response.text)
            except Exception as e:
                logging.error("Could not create an XML file")
            else:
                logging.info("Feed contents saved")
        else:
            logging.error(f"{response.status_code} {response.reason}: {response.url}")
            sys.exit(1)


def read_xml_file(filename, args):
    """
    Opens the xml file, reads it and returns its contents
        filename (string): xml file name
        output: a string with the file contents
    """
    try:
        get_rss_feed(args.source, filename)
    except Exception:
        logging.warning("Could not get new RSS feed")
    if os.path.exists(f"{PATH}cache/{filename}.xml"):
        logging.info("Reading from cache")
        try:
            with open(f"{PATH}cache/{filename}.xml", "r") as xml_file:
                contents = bs(xml_file, "lxml-xml")
        except Exception:
            logging.error("Could not read the XML file")
        else:
            return contents
    else:
        logging.warning("No cache for this channel found")


def xml_to_obj(contents, args):
    """
    Creates a list of dictionaries with tag names as keys and their contents as values.
    Writes the list into a JSON file if --json option is provided.
        contents (string): a string with xml contents
        args (Namespace object): command line arguments
        output: a list of key-value pair objects in a <tag name>:<tag value> format
    """
    feed = []
    tags = []
    channel = {}
    if(contents):
        logging.info("Scanning the XML file for feeds")
        header = contents.find("channel")
        items = contents.find_all("item")
        channel["Title"] = header.find("title").string
        channel["Link"] = header.find("link").string
        feed.append(channel)
        # feed.extend(channel)
        for item in items:
            entry = {}
            links = []
            tags = item.find_all(True)
            for tag in tags:
                link_check = extract_links(tag)
                if(link_check):
                    links.extend(link_check)
                if (tag.name == "pubDate"):
                    entry["Date"] = tag.string
                elif (tag.name == "description"):
                    entry["Description"] = bs(tag.string, "html.parser").get_text()
                elif (tag.name == "title") or (tag.name == "link"):
                    entry[tag.name.capitalize()] = tag.string
            entry["Links"] = links
            feed.append(entry)
            # feed.extend(entry)
        if(args.json):
            try:
                logging.info("Creating a JSON file for the feed contents")
                with open(f"{PATH}cache/{channel['Title']}.json", "w", encoding="utf-8") as json_file:
                    json_file.write(json.dumps(feed, indent=4, ensure_ascii=False))
                    # json_file.write(json.dump(feed))
                    # json_file.write(json.dumps(feed, indent=4))
                    logging.info("All entries saved in a JSON file")
            except Exception:
                logging.error("Could not write to a JSON file")
        return (feed[0], feed[1:])
    else:
        logging.warning("No feed to display")
        sys.exit(0)


def extract_links(tag):
    """
    Find all existing xml attributes and check if their value has a url
        tag : bs object with tags
        output: list with links
    """
    links = []
    if tag.attrs:
        for _, value in tag.attrs.items():
            if (re.findall("http[s]", value)):
                links.append(value)
    if tag.contents:
        links_found = re.findall(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", tag.contents[0])
        if(links_found):
            links.extend(links_found)
    return links


def output_feed(args):
    """
    Reads downloaded or cached XML file.
    Converts it into a dictionary, unpacks the header and the body of the feed.
    Sends the output to printing functions.
        args (Namespace object): command line arguments
    """
    filename = re.findall(
        r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)", args.source)
    xml_output = read_xml_file(filename, args)
    channel, feed = xml_to_obj(xml_output, args)
    if(args.json):
        logging.info("Displaying feed in JSON format")
        display_json(channel, args)
    else:
        logging.info("Printing out feed")
        print_output(channel, feed, args)


def print_output(channel, feed, args):
    """
    Checks if the dictionaries have the necessary properties.
    Compiles the output according to set limit.
    Shows the output on the terminal
        channel (dict): the header of the feed
        feed (dict): the body of the feed
        args (Namespace object): command line arguments
        output: text sent to STDOUT in custom format
    """
    channel_title = channel["Title"] if "Title" in channel else ""
    channel_link = channel["Link"] if "Link" in channel else ""
    print(f"\nChannel: {channel_title} - {channel_link}")
    if (args.limit and args.limit >= len(feed)):
        args.limit = None
    for entry in feed[:args.limit]:
        date = entry["Date"] if "Date" in entry else ""
        title = entry["Title"] if "Title" in entry else ""
        link = entry["Link"] if "Link" in entry else ""
        description = entry["Description"] if "Description" in entry else ""
        if(args.date):
            if(parse(str(args.date)).date() != parse(date).date()):
                continue
        print_entry(entry, date, title, link, description)


def print_entry(entry, date, title, link, description):
    """
    Prints out a single entry.
        entry (dict): contains all the fields of the post 
        date (string): publication date 
        title (string): title of the entry
        link (string): link to the post 
        description (string): the main content of the entry 
    """
    # print(f"\nDate:\t{date}\nTitle:\t{title}\nLink:\t{link}\n\t{description}")
    print(f"\nDate:\t{date}\nTitle:\t{title}\nLink:\t{link}\n\t{description}")
    if ("Links" in entry):
        print("Links:")
        for num, url in enumerate(entry["Links"]):
            print(f"[{num + 1}]:\t{url}")


def display_json(channel, args):
    """
    Reads the existing JSON file with cached feed.
    Prints out the contents according to set limit.
        channel (dict): the complete feed
        args (Namespace object): command line arguments
        output: text sent to STDOUT in JSON format
    """
    contents = ""
    limit = args.limit
    try:
        with open(f"{PATH}cache/{channel['Title']}.json", "r", encoding="utf-8") as json_file:
            contents = json.load(json_file)
    except Exception:
        logging.error("Could not read the JSON file")
    if(limit and limit >= len(contents)):
        limit = None
    elif(limit):
        limit += 1
    for entry in contents[:limit]:
        if(args.date and "Date" in entry):
            if(parse(str(args.date)).date() != parse(entry["Date"]).date()):
                continue
        print(json.dumps(entry, indent=4, ensure_ascii=False))


def main():
    """
    Configures argparse module
        output (Namespace): a Namespace object of parsed arguments
    """
    parser = argparse.ArgumentParser(description="Pure Python command-line RSS reader.")
    parser.add_argument("source", help="RSS URL")
    parser.add_argument("--version", action="version", version=__version__, help="Print version info")
    parser.add_argument("--json", action="store_true", help="Print result as JSON in stdout")
    parser.add_argument("--verbose", action="store_true", help="Outputs verbose status messages")
    parser.add_argument("--limit", nargs="?", type=int, help="Limit news topics if this parameter provided")
    parser.add_argument("--colorize", action="store_true", help="Colorizes the output")
    parser.add_argument("--date", nargs="?", type=int, help="Show news for the chosen date")
    args = parser.parse_args()

    log_level = logging.INFO if args.verbose else logging.WARNING
    log_fmt = "%(asctime)s - %(levelname)s: %(message)s"
    logging.basicConfig(level=log_level, stream=sys.stdout, format=log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
    logging.info("Parsing arguments")
    logging.info("Setting up logger")
    
    output_feed(args)
    logging.info("Done!")
    

if __name__ == "__main__":
    main()
