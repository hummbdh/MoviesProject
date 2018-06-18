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
        movies = movies['query']['categorymembers'][8::]
        movies = [ x['title'] for x in movies[1::] ]
        movie_list = [ (re.search(r"[^Category:](.*)[^ films]", str(x)).group(0)) for x in movies]
        return movie_list

    def get_films(self, year):
        base_url = 'https://en.wikipedia.org/w/api.php'
        params = {
                    'action': 'parse',
                    'format': 'json',
                    'page': 'List of American films of ' + year,
                    'prop': 'wikitext',
                    #'section': '10',
                    'formatversion': '1',
                 }

        r = requests.get(base_url, params=params)
        films = r.json()
        films = films['parse']['wikitext']['*']

        film = list(set(re.findall(r"\'\'\[\[(.*?)\]\]\'\'", films))) # set() used to remove duplicates
        #film_list = re.findall(r".+?(?=\|)", film[6])
        film_list = []
        for movie_title in film:
            if '|' in movie_title:
                text_search = re.search('(?<=\|).*', str(movie_title))
                film_list.append(text_search.group(0))
            else:
                film_list.append(movie_title)
        return film_list #set(film_list)

    def get_image(self, *args):
        POSTER_API = "http://img.omdbapi.com/" #+ OMBDB_API_KEY
        OMDB_API = "http://www.omdbapi.com/" #+ OMBDB_API_KEY

        OMDB_params = {
                            'apikey': API_KEYS['OMDB_API_KEY'],
                            'y': args[1]
                      }

        POSTER_params = {
                            'apikey': API_KEYS['OMDB_API_KEY'],
                            #'h': 500,
                        }
        images = []
        film_list = args[0]
        for film in film_list:
            OMDB_params['t'] =  film
            try:
                r = requests.get(OMDB_API, params=OMDB_params,timeout=0.1).json()
                if (r['Response'] == 'True'):
                    POSTER_params['i'] = r['imdbID']
                    try:
                        r =  requests.get(POSTER_API, params=POSTER_params, timeout=0.1)
                        if (r.status_code == 200):
                            print(r)
                            images.append(r.url)
                        else:
                            pass
                    except:
                        print('Did not work')
                else:
                    #print(r['Response'])
                    pass
            except:
                pass #print(r)
            else:
                pass
        return images

    def __call__(self, request):
        return self.get_response(request)
