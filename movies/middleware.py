import requests, json, re
from . import views
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from .models import FilmYear
from config import API_KEYS

class WikiDataMiddleware(MiddlewareMixin):
    """
        Middleware designed to send out requests and retrieve responses
        from Wikipedia APIs
    """

    # Make calls to Wikipedia API to retrieve list of
    # years that movies were made
    def get_film_years(self):
        base_url = 'https://en.wikipedia.org/w/api.php'
        params = {
                    'action': 'query',
                    'list': 'categorymembers',
                    'cmtitle': 'Category: Films by year',
                    'format': 'json',
                    'cmlimit': '500',
                 }
                 
        r = requests.get(base_url, params=params)
        movies = r.json()

        # Parse response to retrieve years
        movies = movies['query']['categorymembers'][8::]
        movies = [ x['title'] for x in movies[1::] ]
        movie_list = [ (re.search(r"[^Category:](.*)[^ films]", str(x)).group(0)) for x in movies]
        return movie_list

    # Based on users choice of year, call wikipedia
    # API and request all of the movies recorded for that year
    def get_films(self, year):
        base_url = 'https://en.wikipedia.org/w/api.php'
        params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': 'List of American films of ' + year,
                    'prop': 'wikitext',
                    'formatversion': '1',
                 }

        r = requests.get(base_url, params=params)
        films = r.json()
        films = films['parse']['wikitext']['*']

        # Wikipedia's response, when put into JSON format is
        # very messy, requires a number of regular expression
        # searches
        film = list(set(re.findall(r"\'\'\[\[(.*?)\]\]\'\'", films))) # set() used to remove duplicates
        film_list = []
        for movie_title in film:
            if '|' in movie_title:
                text_search = re.search('(?<=\|).*', str(movie_title))
                film_list.append(text_search.group(0))
            else:
                film_list.append(movie_title)
        return film_list

    # From Open Movie Database API retrieve movie posters
    # associated with each movie
    def get_image(self, *args):
        POSTER_API = "http://img.omdbapi.com/"
        OMDB_API = "http://www.omdbapi.com/"

        OMDB_params = {
                            'apikey': API_KEYS['OMDB_API_KEY'],
                            'y': args[1]
                      }

        POSTER_params = {
                            'apikey': API_KEYS['OMDB_API_KEY'],
                        }
        images = []
        film_list = args[0]
        for film in film_list:
            OMDB_params['t'] =  film

            # OMDB API often returns a 404 response for the movie
            # poster requested.  Try and Except are included for
            # continutiy and as a future effort to retry failed
            # requests
            try:
                r = requests.get(OMDB_API, params=OMDB_params,timeout=0.1).json()
                if (r['Response'] == 'True'):
                    POSTER_params['i'] = r['imdbID']
                    try:
                        r =  requests.get(POSTER_API, params=POSTER_params, timeout=0.1)
                        if (r.status_code == 200):
                            print(r)
                            images.append(r.url)
                    except:
                        print('Did not work')
            except:
                pass
        return images

    def __call__(self, request):
        return self.get_response(request)
