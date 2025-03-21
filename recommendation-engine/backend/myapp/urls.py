from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import FlightDataViewSet

router = DefaultRouter()
router.register(r'flights', FlightDataViewSet, basename='flight')


urlpatterns = [
    path("", views.home, name="home"),
    path('api/', include(router.urls)),
    path('api/query/', views.langchain_query, name='query'),
    path('api/calculatemiles/',views.upload_csv_file, name='calculatemiles'),
    path('api/cache/clear/', views.clear_cache, name='clear_cache')
]