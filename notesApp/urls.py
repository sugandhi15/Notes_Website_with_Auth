from django.urls import path
from .views import NotesViewSet
from rest_framework.routers import DefaultRouter
from .views import Register

router = DefaultRouter()
router.register(r'notes', NotesViewSet, basename='notes')

urlpatterns = [
    path('register/',Register,name="register"),
]
urlpatterns += router.urls