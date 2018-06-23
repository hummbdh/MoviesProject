from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
import request
from django.urls import reverse, reverse_lazy, resolve
from . import middleware
from .models import FilmYear
from django.http.request import HttpRequest
from django.template import RequestContext


class MoviesIndex(TemplateView):
    model = FilmYear
    template_name ='movies.html'

    def get_context_data(self, **kwargs):
        context = super(MoviesIndex, self).get_context_data(**kwargs)
        context['years'] = middleware.WikiDataMiddleware.get_film_years(self)
        return context

class FilmYears(TemplateView):
    model = FilmYear
    template_name = 'films.html'

    def get_context_data(self, **kwargs):
        context = super(FilmYears, self).get_context_data(**kwargs)
        context['films'] = middleware.WikiDataMiddleware.get_films(self, context['pk'])
        context['images'] = middleware.WikiDataMiddleware.get_image(self, context['films'], context['pk'])
        context['movies'] = zip(context['films'], context['images'])
        return context
