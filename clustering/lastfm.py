import argparse
import logging

import requests


__author__ = "Nikolay Anokhin"


class Artist(object):

    def __init__(self, name):
        assert isinstance(name, unicode), "Name {0} is of type {1}".format(name, type(name))
        self.name = name
        self.tags = set()
        self.summary = ""

    def add_tag(self, tag):
        assert isinstance(tag, unicode), "Tag {0} is of type {1}".format(tag, type(tag))
        self.tags.add(tag)

    def __repr__(self):
        return "Artist('{0}', tags={1})".format(self.name.encode('ascii', 'ignore'), self.tags)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.name == other.name

    def __hash__(self):
        return hash(self.name)


class ApiClient(object):

    API_URL = "http://ws.audioscrobbler.com/2.0/"

    def __init__(self, api_key):
        self.api_key = api_key

    def _load(self, method, **kwargs):
        params = dict(kwargs)
        params["method"] = method
        params["api_key"] = self.api_key
        params["format"] = "json"
        response = requests.get(self.API_URL, params=params).json()
        if response and "error" in response:
            raise ValueError(response.get("message", "Unknown error"))
        else:
            return response

    def top_artist_names(self, tag):
        logging.debug("Loading top artists for tag '%s'", tag)
        response = self._load("tag.gettopartists", tag=tag, limit=100)
        if response:
            artists_group = response.get("topartists")
            if artists_group:
                artists = artists_group.get("artist", [])
                for artist in artists:
                    name = artist.get("name")
                    if name:
                        yield name

    def load_artist(self, name):
        logging.debug("Loading artist %s", name)
        response = self._load("artist.getinfo", artist=name, autocorrect=1).get("artist")
        if response:
            name = response.get("name")
            if name:
                artist = Artist(name)
                # Load tags
                tags_group = response.get("tags")
                if tags_group:
                    tags = tags_group.get("tag", [])
                    for tag in tags:
                        artist.add_tag(tag.get("name"))
                # Load description
                bio = response.get("bio")
                if bio:
                    summary = bio.get("summary")
                    if summary:
                        artist.summary = summary
                # TODO: Load festivals

                return artist

        logging.debug('Can not load artist {0}'.format(name))
        return None


def main():
    # Set up logging
    logging.basicConfig(level=logging.ERROR, format="[%(asctime)-15s] %(message)s")
    print "Welcome to the LastFM clustering example"

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", action="store", help="LastFM account api key", required=True)
    parser.add_argument("tags", nargs='+', help="The tags used to search artists")
    args = parser.parse_args()

    for tag in args.tags:
        logging.debug("Searching top artists for tag '%s'", tag)
        client = ApiClient(args.key)
        for artist_name in client.top_artist_names(tag):
            artist = client.load_artist(artist_name)
            print artist


if __name__ == "__main__":
    main()