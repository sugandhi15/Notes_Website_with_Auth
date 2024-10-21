from django.urls import path
# from .views import NotesViewSet
from rest_framework.routers import DefaultRouter
from .views import Register,ResetPassword,passwordResetToken,specificNote,google_login,google_callback,FetchAllNotes,NotesEndpt,UserPassReset,homepage

# router = DefaultRouter()
# router.register(r'notes', NotesViewSet, basename='notes')

urlpatterns = [
    path("",homepage,name="homepage"),
    path('notes/',NotesEndpt,name="NotesEndpt"),
    path('register/',Register,name="register"),
    path('note/<int:id>',specificNote,name="specificNote"),
    path("notes/all",FetchAllNotes,name="fetchAllNotes"),
    path('password/reset/',ResetPassword,name="resetPassword"),
    path('password/reset/<str:token>',passwordResetToken,name="resetPassword"),
    path('auth/google/', google_login, name='google_login'),
    path('auth/google/callback/', google_callback, name='google_callback'),
    path('pass/reset/',UserPassReset,name="passReset"),
]
# urlpatterns += router.urls