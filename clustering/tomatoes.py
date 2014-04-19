import argparse
import logging
import requests

__author__ = 'nikolayanokhin'


class Movie(object):

    def __init__(self, movie_id, title):
        assert isinstance(title, unicode), "Name {0} is of type {1}".format(title, type(title))
        self.movie_id = movie_id
        self.title = title
        self.actors = set()
        self.synopsis = ""

    def add_actor(self, actor):
        assert isinstance(actor, unicode), "Tag {0} is of type {1}".format(actor, type(actor))
        self.actors.add(actor)

    def __repr__(self):
        return "Movie('{0}', '{1}', actors={2})".format(self.movie_id, self.title.encode('ascii', 'ignore'), self.actors)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.movie_id == other.movie_id and self.title == other.title

    def __hash__(self):
        return hash(self.movie_id)


class ApiClient(object):

    API_URL = "http://api.rottentomatoes.com/api/public/v1.0/movies.json"

    def __init__(self, api_key):
        self.api_key = api_key

    def _load(self, **kwargs):
        params = dict(kwargs)
        params["apikey"] = self.api_key
        response = requests.get(self.API_URL, params=params).json()
        if response and "Error" in response:
            raise ValueError(response.get("Error", "Unknown error"))
        else:
            return response

    def search_movies(self, keyword, page_limit=50):
        logging.debug("Searching movies by keyword '%s'", keyword)
        response = self._load(q=keyword, page_limit=page_limit)
        if response:
            movies = response.get("movies")
            if movies:
                for result in movies:
                    movie_id = result.get("id")
                    title = result.get("title")
                    if movie_id and title:
                        movie = Movie(movie_id, title)
                        movie.synopsis = result.get("synopsis", "")
                        # Actors
                        cast = result.get("abridged_cast", [])
                        for actor in cast:
                            actor_name = actor.get("name")
                            if actor_name:
                                movie.add_actor(actor_name)
                        # TODO: Load target variable, i.e. Genres
                        yield movie


def main():
    # Set up logging
    logging.basicConfig(level=logging.ERROR, format="[%(asctime)-15s] %(message)s")
    print "Welcome to the IMDB clustering example"

    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", action="store", help="LastFM account api key", required=True)
    parser.add_argument("keywords", nargs='+', help="The keywords used to search movies")
    args = parser.parse_args()

    for keyword in args.keywords:
        logging.debug("Searching movies for keyword '%s'", keyword)
        client = ApiClient(args.key)
        for movie in client.search_movies(keyword):
            print movie


if __name__ == "__main__":
    main()
