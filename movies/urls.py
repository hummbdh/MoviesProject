from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [

    path('', views.MoviesIndex.as_view(), name='film-years'),
    re_path(r'(?P<pk>[0-9]{4})/$', views.FilmYears.as_view(), name='films'),
    ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
